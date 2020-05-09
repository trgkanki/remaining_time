from aqt import gui_hooks

import json
import re
import uuid

_handlerMap = {}
_addonMessageRegex = re.compile(r"addonmsg:(\d+):(.+)")


def _onBridgeMessage(handled, message: str, context):
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
