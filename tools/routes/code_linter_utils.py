import subprocess
import tinycss2
from html.parser import HTMLParser

class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.open_tags = []
        self.issues = []

    def handle_starttag(self, tag, attrs):
        self.open_tags.append(tag)

    def handle_endtag(self, tag):
        if tag not in self.open_tags:
            self.issues.append(f"Unmatched end tag: </{tag}>")
        else:
            self.open_tags.remove(tag)

def lint_html(code: str) -> list:
    parser = TagChecker()
    parser.feed(code)
    return parser.issues if parser.issues else ["No HTML issues found."]

def lint_css(code: str) -> list:
    issues = []
    try:
        rules = tinycss2.parse_stylesheet(code, skip_comments=True, skip_whitespace=True)
        if not rules:
            issues.append("Empty or invalid CSS.")
    except Exception:
        issues.append("Syntax error in CSS.")
    return issues if issues else ["No CSS issues found."]

def lint_js(code: str) -> list:
    try:
        result = subprocess.run(["esprima", "--parse", "-"], input=code.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        if result.returncode != 0:
            return [result.stderr.decode().strip()]
        return ["No JavaScript issues found."]
    except Exception as e:
        return [f"Error running JS linter: {str(e)}"]
