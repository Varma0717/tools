import re

def bundle_files(file_contents: list[str], mode: str) -> tuple[str | None, str | None]:
    try:
        combined = "\n".join(file_contents)

        if mode == "css":
            # Remove comments /* ... */ and extra whitespace
            combined = re.sub(r'/\*[\s\S]*?\*/', '', combined)
            combined = re.sub(r'\s{2,}', ' ', combined)
            combined = re.sub(r'\s*([{}:;,])\s*', r'\1', combined).strip()
        elif mode == "js":
            # Remove single-line and multi-line comments
            combined = re.sub(r'//.*', '', combined)
            combined = re.sub(r'/\*[\s\S]*?\*/', '', combined)
            combined = re.sub(r'\s{2,}', ' ', combined)
            combined = re.sub(r'\s*([{}();,:])\s*', r'\1', combined).strip()
        else:
            return None, "Unsupported mode. Choose 'css' or 'js'."

        return combined, None
    except Exception as e:
        return None, str(e)
