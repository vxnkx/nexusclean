import ast
import base64
import os
import sys
import zlib


def extract_bytes_from_ast(source_code):
    """Safely parses the code structure to extract the raw bytes payload."""
    try:
        tree = ast.parse(source_code)
        # Walk through all nodes in the script looking for a Bytes literal
        for node in ast.walk(tree):
            # In Python 3.8+, Constant nodes store literal values
            if isinstance(node, ast.Constant) and isinstance(node.value, bytes):
                return node.value
            # For compatibility with older Python 3 versions
            elif isinstance(node, ast.Bytes):
                return node.s
    except Exception:
        pass
    return None


def deobfuscate_layers(initial_content):
    layer = 0
    current_content = initial_content

    while True:
        # Extract the exact byte sequence using the AST parser
        encoded_data = extract_bytes_from_ast(current_content)

        if not encoded_data:
            break

        try:
            # Apply the reconstruction logic
            reversed_data = encoded_data[::-1]
            decoded_data = base64.b64decode(reversed_data)
            decompressed_data = zlib.decompress(decoded_data)

            # Update string content for the next layer
            current_content = decompressed_data.decode("utf-8", errors="ignore")
            layer += 1
            print(f"[+] Successfully peeled back layer {layer}...")

        except Exception as e:
            # Stop when the extracted bytes can no longer be decompressed/decoded
            print(f"[*] Iteration stopped: Final layer reached ({e}).")
            break

    return current_content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        script_name = os.path.basename(sys.argv[0])
        print(f"Usage: python {script_name} <path_to_obfuscated_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"[-] Error: File '{file_path}' does not exist.")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_content = f.read()

    print(f"[*] Analyzing layers in {file_path}...")
    final_source_code = deobfuscate_layers(raw_content)

    print("\n--- FINAL UNPACKED SOURCE CODE ---")
    print(final_source_code)
