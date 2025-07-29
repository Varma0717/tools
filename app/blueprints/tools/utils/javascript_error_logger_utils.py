import subprocess
import os
import tempfile
import re

def log_js_errors(code: str) -> tuple[list[dict] | None, str | None]:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w") as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        result = subprocess.run(
            ["node", "--trace-warnings", temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )

        os.unlink(temp_file_path)
        stderr = result.stderr.decode().strip()

        if not stderr:
            return [{"line": None, "message": "✅ No JavaScript runtime errors detected."}], None

        # Grab only first ReferenceError, SyntaxError, etc.
        lines = stderr.splitlines()
        issues = []
        for line in lines:
            if re.search(r'(ReferenceError|SyntaxError|TypeError)', line):
                match = re.search(r'at\s.*:(\d+):', line)
                lineno = int(match.group(1)) if match else None
                issues.append({"line": lineno, "message": line.strip()})
                break  # Only show 1 clean error

        if not issues:
            issues.append({"line": None, "message": lines[0].strip()})

        return issues, None
    except Exception as e:
        return None, str(e)
