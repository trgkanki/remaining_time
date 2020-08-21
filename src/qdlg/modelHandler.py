def configureModel(obj, attrName, onInput, setValue):
    assert hasattr(obj, "_observersDict")  # check observable
    setValue(getattr(obj, attrName))
    _registerObserver(obj, attrName, setValue)

    def _(v):
        oldV = getattr(obj, attrName)
        if oldV != v:
            setattr(obj, attrName, v)

    onInput(_)


def _registerObserver(self, attrName, handler):
    try:
        handlerList = self._observersDict[attrName]
    except KeyError:
        handlerList = []
        self._observersDict[attrName] = handlerList
    handlerList.append(handler)


def QObservable(Cls):
    oldInit = Cls.__init__
    oldSetAttr = Cls.__setattr__

    def newInit(self, *args, **kwargs):
        oldInit(self, *args, **kwargs)
        self._observersDict = {}

    def newSetAttr(self, name, value):
        oldSetAttr(self, name, value)
        if hasattr(self, "_observersDict"):
            for handler in self._observersDict.get(name, []):
                handler(value)

    Cls.__init__ = newInit
    Cls.__setattr__ = newSetAttr

    return Cls
