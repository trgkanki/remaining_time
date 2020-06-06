from aqt import gui_hooks
from aqt.utils import showInfo
from .configrw import getCurrentAddonName

import json
import re
import uuid
from .resource import readResource

_handlerMap = {}
_addonMessageRegex = re.compile(r"addonmsg:(\d+):(.+)")


def _onBridgeMessage(handled, message, context):
    matches = _addonMessageRegex.match(message)
    if not matches:
        return handled


    handlerKey = matches.group(1)
    message = matches.group(2)
    if handlerKey in _handlerMap:
        _handlerMap[handlerKey](json.loads(message))
        del _handlerMap[handlerKey]
        return (True, None)

gui_hooks.webview_did_receive_js_message.append(_onBridgeMessage)

def execJSFile(web, jspath, *, once=False):
    if once:
        if not hasattr(web, '__plugin_jsTable'):
            web.__plugin_jsTable = set()

        checkKey = ''.join([getCurrentAddonName(), '#', jspath])
        if checkKey in web.__plugin_jsTable:
            return

    js = readResource(jspath)
    web.eval(js)
    if once:
        web.__plugin_jsTable.add(checkKey)


def execJSFileOnce(web, jspath):
    """
    Excute JS file only once. useful for webpack-based modules
    """
    return execJSFile(web, jspath, once=True)

def evalJS(web, funcexpr, cb):
    # Register handler
    handlerKey = str(uuid.uuid4().int)
    _handlerMap[handlerKey] = cb

    # Execute js code
    web.eval(
        """
    Promise.resolve(%s).then(msg => {
        pycmd(`addonmsg:%s:${JSON.stringify(msg)}`)
    })"""
        % (funcexpr, handlerKey)
    )
