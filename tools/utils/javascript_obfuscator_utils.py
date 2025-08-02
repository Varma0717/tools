import re
import base64

def obfuscate_js(code: str) -> str:
    # Remove comments
    code = re.sub(r"\/\/.*?$|\/\*.*?\*\/", "", code, flags=re.MULTILINE | re.DOTALL)

    # Remove extra whitespace
    code = re.sub(r"\s+", " ", code)

    # Encode the code using base64 for simple obfuscation
    encoded = base64.b64encode(code.encode('utf-8')).decode('utf-8')

    # Wrap it in a loader
    return f"""(function() {{
    const decoded = atob("{encoded}");
    eval(decoded);
}})();"""
