from aqt import gui_hooks
from aqt.utils import showInfo
from .uuid import addonUUID

import json
import traceback


def JSCallable(func):
    """ Decorator for js-callable python function """
    funcName = func.__name__
    msgPrefix = "pyfunc:%s:%s:" % (addonUUID(), funcName)

    def _onBridgeMessage(handled, message: str, context):
        if not message.startswith(msgPrefix):
            return handled

        # Need to json decode on the input
        try:
            argList = json.loads(message[len(msgPrefix) :])
        except json.JSONDecodeError:
            showInfo(
                ("Error: malformed message from addon %s:\n%s")
                % (funcName, traceback.format_exc())
            )

            return (True, {"error": "malformed message"})

        ret = func(*argList)
        # json encoding is not needed on return - already handled by Anki.
        return (True, {"error": None, "payload": ret})

    gui_hooks.webview_did_receive_js_message.append(_onBridgeMessage)

    # return function as-is. We don't need to modify them really
    return func
