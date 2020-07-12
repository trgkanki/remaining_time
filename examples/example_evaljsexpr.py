from .utils.JSEval import evalJS


def cb(data):
    # Data should be 2
    pass


# Web is some AnkiWebView instance
evalJS(web, "1 + 1", cb)
