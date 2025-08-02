import rjsmin

def minify_js(code: str) -> str:
    return rjsmin.jsmin(code)
