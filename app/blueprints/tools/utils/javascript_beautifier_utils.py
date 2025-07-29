import jsbeautifier

def beautify_js(code: str) -> str:
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    opts.preserve_newlines = True
    return jsbeautifier.beautify(code, opts)
