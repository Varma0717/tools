import subprocess
import cssutils
import re

# ✅ HTML Linter using `tidy` CLI
def lint_html(code: str) -> list:
    try:
        result = subprocess.run(
            ["tidy", "-quiet", "-errors"],
            input=code.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        output = result.stderr.decode()
        issues = []

        for line in output.splitlines():
            match = re.search(r'line\s+(\d+)\s+column\s+\d+\s+-\s+(.*)', line, re.IGNORECASE)
            if match:
                lineno = int(match.group(1))
                msg = match.group(2).strip().capitalize()
                issues.append({
                    "line": lineno,
                    "message": f"HTML: {msg}"
                })

        return issues if issues else [{"line": None, "message": "✅ No HTML issues found."}]
    except Exception as e:
        return [{"line": None, "message": f"HTML Lint Error: {str(e)}"}]



# ✅ CSS Linter using `cssutils` (with cleaned output and guessed line numbers)
def lint_css(code: str) -> list:
    issues = []
    cssutils.log.setLevel('FATAL')  # Suppress internal warnings

    try:
        sheet = cssutils.parseString(code)
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                for prop in rule.style:
                    if not prop.valid:
                        # Rough estimate of line number from first appearance
                        prop_name = re.escape(prop.name)
                        match = re.search(rf"{prop_name}\s*:", code, re.IGNORECASE)
                        lineno = code[:match.start()].count('\n') + 1 if match else None
                        issues.append({
                            "line": lineno,
                            "message": f"CSS: Invalid property '{prop.name}'"
                        })
    except Exception as e:
        issues.append({
            "line": None,
            "message": f"CSS Parsing Error: {str(e)}"
        })

    return issues if issues else [{"line": None, "message": "✅ No CSS issues found."}]



# ✅ JS Linter using `esparse` CLI (cleaned and minimal error display)
def lint_js(code: str) -> list:
    try:
        result = subprocess.run(
            ["esparse", "-"],
            input=code.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )

        stderr = result.stderr.decode().strip()

        if stderr:
            match = re.search(r'Line\s+(\d+):\s+(.*)', stderr)
            line = int(match.group(1)) if match else 1
            message = match.group(2).strip() if match else "JavaScript syntax error"
            return [{"line": line, "message": f"JS: {message}"}]

        return [{"line": None, "message": "✅ No JavaScript issues found."}]

    except Exception as e:
        return [{"line": None, "message": f"JS Error: {str(e)}"}]
