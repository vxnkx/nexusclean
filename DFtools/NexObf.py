#!/usr/bin/env python3
import os
import sys
import ast
import base64
import random
import string
import zlib
import argparse
import hashlib

# ------------------------------------------------------------
# CONFIGURATION (change these as needed)
# ------------------------------------------------------------
RENAME_VARS = True
ENCODE_STRINGS = True
ADD_DEAD_CODE = True
ADD_ANTI_DEBUG = True
FLATTEN_CONTROL_FLOW = False   # Set to True only if you're sure your code can handle it
COMPRESS_FINAL = True

random.seed(0)  # deterministic for reproducibility (remove for true randomness)

def random_name(length=8):
    first = random.choice(string.ascii_letters)
    rest = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length-1))
    return first

# ------------------------------------------------------------
# STRING ENCODER (XOR + zlib + base64)
# ------------------------------------------------------------
def encode_string(s):
    if len(s) < 3:
        return repr(s)
    key = random.randint(1, 255)
    data = s.encode()
    xor_bytes = bytes([b ^ key for b in data])
    compressed = zlib.compress(xor_bytes)
    b64 = base64.b64encode(compressed).decode()
    # Decoder lambda that decompresses, XORs, then decodes
    decoder = f"(lambda k,b: (lambda x: x.decode())(__import__('zlib').decompress(__import__('base64').b64decode(b))).decode() if False else (lambda x: bytes([(x[i] ^ k) for i in range(len(x))]))(__import__('zlib').decompress(__import__('base64').b64decode(b))))({key},'{b64}')"
    return decoder

def obfuscate_strings_in_ast(tree):
    class StringObfuscator(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str) and len(node.value) > 2:
                # Skip docstrings and specials
                if node.value.startswith(('"""', "'''")) or node.value in ('__main__', '__name__', '__file__'):
                    return node
                encoded = encode_string(node.value)
                new_node = ast.parse(encoded).body[0].value
                return new_node
            return node
    return StringObfuscator().visit(tree)

# ------------------------------------------------------------
# VARIABLE RENAMING
# ------------------------------------------------------------
class NameObfuscator(ast.NodeTransformer):
    def __init__(self):
        self.name_map = {}
        self.used = set()
        self.globals = set(dir(__builtins__))
        self.globals.update({'print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list', 'dict',
                             'set', 'tuple', 'type', 'isinstance', 'issubclass', 'hasattr', 'getattr',
                             'setattr', 'delattr', 'dir', 'vars', 'locals', 'globals', '__name__',
                             '__main__', '__file__', '__doc__', '__import__', 'exec', 'eval', 'compile',
                             'open', 'exit', 'quit'})
    def new_name(self, old):
        if old in self.globals:
            return old
        if old in self.name_map:
            return self.name_map[old]
        n = random_name()
        while n in self.used or n in self.globals:
            n = random_name()
        self.used.add(n)
        self.name_map[old] = n
        return n
    def visit_FunctionDef(self, node):
        node.name = self.new_name(node.name)
        new_args = []
        for arg in node.args.args:
            arg.arg = self.new_name(arg.arg)
            new_args.append(arg)
        node.args.args = new_args
        self.generic_visit(node)
        return node
    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)):
            if node.id in self.name_map:
                node.id = self.name_map[node.id]
        return node

# ------------------------------------------------------------
# DEAD CODE INSERTION
# ------------------------------------------------------------
def insert_dead_code(body):
    dead_templates = [
        ast.Assign(targets=[ast.Name(id='_', ctx=ast.Store())], value=ast.Constant(value=random.randint(0,9999))),
        ast.Expr(value=ast.Call(func=ast.Name(id='len', ctx=ast.Load()), args=[ast.Constant(value='')], keywords=[])),
        ast.Expr(value=ast.Call(func=ast.Name(id='hash', ctx=ast.Load()), args=[ast.Constant(value=random.randint(1,100))], keywords=[])),
    ]
    new_body = []
    for stmt in body:
        new_body.append(stmt)
        if random.random() < 0.15:
            new_body.append(random.choice(dead_templates))
    return new_body

class DeadCodeInserter(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        node.body = insert_dead_code(node.body)
        self.generic_visit(node)
        return node
    def visit_Module(self, node):
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, ast.FunctionDef):
                node.body[i] = self.visit(stmt)
        return node

# ------------------------------------------------------------
# CONTROL FLOW FLATTENING (simple version)
# ------------------------------------------------------------
def flatten_function_body(body):
    state_var = '__state__'
    state_val = 0
    flattened = [ast.Assign(targets=[ast.Name(id=state_var, ctx=ast.Store())], value=ast.Constant(value=state_val))]
    loop_body = []
    for i, stmt in enumerate(body):
        cond = ast.Compare(left=ast.Name(id=state_var, ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value=i)])
        if_stmt = ast.If(test=cond, body=[stmt] + [ast.Assign(targets=[ast.Name(id=state_var, ctx=ast.Store())], value=ast.Constant(value=i+1))], orelse=[])
        loop_body.append(if_stmt)
    loop_body.append(ast.Break())
    flattened.append(ast.While(test=ast.Constant(value=True), body=loop_body, orelse=[]))
    return flattened

class ControlFlowFlattener(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        if len(node.body) > 1:
            node.body = flatten_function_body(node.body)
        self.generic_visit(node)
        return node

# ------------------------------------------------------------
# ANTI-DEBUG WRAPPER
# ------------------------------------------------------------
def anti_debug_wrapper():
    return '''
import sys, ctypes, threading, time
def _a():
    if sys.gettrace() is not None:
        while 1: time.sleep(999)
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            while 1: time.sleep(999)
    except: pass
threading.Thread(target=_a, daemon=True).start()
del _a
'''

# ------------------------------------------------------------
# MAIN OBFUSCATION FUNCTION
# ------------------------------------------------------------
def obfuscate_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        source = f.read()

    # Parse AST
    tree = ast.parse(source)

    # Apply transformations
    if RENAME_VARS:
        tree = NameObfuscator().visit(tree)
    if ENCODE_STRINGS:
        tree = obfuscate_strings_in_ast(tree)
    if ADD_DEAD_CODE:
        tree = DeadCodeInserter().visit(tree)
    if FLATTEN_CONTROL_FLOW:
        tree = ControlFlowFlattener().visit(tree)

    ast.fix_missing_locations(tree)

    # Convert back to source
    try:
        obf_source = ast.unparse(tree)
    except Exception as e:
        print(f"Warning: ast.unparse failed ({e}), falling back to original.")
        obf_source = source

    # Add anti-debug
    if ADD_ANTI_DEBUG:
        obf_source = anti_debug_wrapper() + obf_source

    # Final compression
    if COMPRESS_FINAL:
        compressed = base64.b64encode(zlib.compress(obf_source.encode())).decode()
        final_stub = f'''import zlib, base64
exec(zlib.decompress(base64.b64decode("{compressed}")))
'''
        obf_source = final_stub

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(obf_source)

    orig = len(source)
    final = len(obf_source)
    print(f"✓ Obfuscated: {input_path} -> {output_path}")
    print(f"  Original size: {orig} bytes")
    print(f"  Obfuscated size: {final} bytes")
    print(f"  Ratio: {final/orig*100:.1f}%")
    return True

# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description='Nexus Obfuscator - Strong multi-layer obfuscation')
    parser.add_argument('input', help='Input Python file')
    parser.add_argument('-o', '--output', help='Output file (default: obf_<input>)')
    parser.add_argument('--no-vars', action='store_true', help='Disable variable renaming')
    parser.add_argument('--no-strings', action='store_true', help='Disable string encoding')
    parser.add_argument('--no-deadcode', action='store_true', help='Disable dead code insertion')
    parser.add_argument('--no-debug', action='store_true', help='Disable anti-debug')
    parser.add_argument('--no-compress', action='store_true', help='Disable final compression')
    parser.add_argument('--flatten', action='store_true', help='Enable control flow flattening (experimental)')
    args = parser.parse_args()

    global RENAME_VARS, ENCODE_STRINGS, ADD_DEAD_CODE, ADD_ANTI_DEBUG, COMPRESS_FINAL, FLATTEN_CONTROL_FLOW
    if args.no_vars:
        RENAME_VARS = False
    if args.no_strings:
        ENCODE_STRINGS = False
    if args.no_deadcode:
        ADD_DEAD_CODE = False
    if args.no_debug:
        ADD_ANTI_DEBUG = False
    if args.no_compress:
        COMPRESS_FINAL = False
    if args.flatten:
        FLATTEN_CONTROL_FLOW = True

    output = args.output or f"obf_{os.path.basename(args.input)}"
    obfuscate_file(args.input, output)

if __name__ == "__main__":
    main()
