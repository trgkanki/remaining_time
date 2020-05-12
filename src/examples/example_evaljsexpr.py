from ..jsBridge import evalJsExpr

def cb(data):
    # Data should be 2
    pass

# Web is some AnkiWebView instance
evalJsExpr(web, "1 + 1", cb)
