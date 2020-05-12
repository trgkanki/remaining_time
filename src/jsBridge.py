from aqt import gui_hooks
from aqt.utils import showInfo

import json
import re
import uuid
import traceback

_handlerMap = {}
_addonMessageRegex = re.compile(r"addonmsg:(\d+):(.+)")


def _onBridgeMessage(handled, message, context):
    matches = _addonMessageRegex.match(message)
    if matches:
        handlerKey = matches.group(1)
        message = matches.group(2)
        if handlerKey in _handlerMap:
            _handlerMap[handlerKey](json.loads(message))
            del _handlerMap[handlerKey]
            return (True, None)

    return handled


gui_hooks.webview_did_receive_js_message.append(_onBridgeMessage)


def evalJsExpr(web, funcexpr, cb):
    handlerKey = str(uuid.uuid4().int)
    _handlerMap[handlerKey] = cb
    web.eval(
        """
    Promise.resolve(%s).then(msg => {
        pycmd(`addonmsg:%s:${JSON.stringify(msg)}`)
    })"""
        % (funcexpr, handlerKey)
    )


def JSCallableFunc(func):
    """ Decorator for js-callable python function """
    funcname = func.__name__
    msgPrefix = 'pyfunc:%s:' % funcname

    def _onBridgeMessage(handled, message: str, context):
        if not message.startswith(msgPrefix):
            return handled

        # Need to json decode on the input
        try:
            argList = json.loads(message[len(msgPrefix):])
        except json.JSONDecodeError:
            showInfo(
                ("Error: malformed message from addon %s:\n%s")
                % (funcname, traceback.format_exc()))

            return (True, {
                'error': 'malformed message'
            })


        ret = func(*argList)
        # json encoding is not needed on return - already handled by Anki.
        return (True, {
            'error': None,
            'payload': ret
        })

    gui_hooks.webview_did_receive_js_message.append(_onBridgeMessage)

    return func
