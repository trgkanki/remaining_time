import inspect

_immutableTypes = {int, str, bool, float}


def bind(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the 
    instance as the first argument, i.e. "self".

    from https://stackoverflow.com/questions/1015307/python-bind-an-unbound-method
    """
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method


def observable(obj):
    if type(obj) in _immutableTypes:
        return obj

    obj._observable = True
    makeObjectObservable(obj)
    for key in dir(obj):
        if not key.startswith("_"):
            # re-setting attribute attaches observer to attribute
            setattr(obj, key, getattr(obj, key))

    return obj


def makeObjectObservable(obj):
    oldInit = obj.__init__
    oldSetAttr = obj.__setattr__
    _attrObserversDict = {}

    # Setters for attributes
    def newSetAttr(self, name, value):
        oldSetAttr(name, observable(value))

        if not name.startswith("_"):  # ignore builtins/private
            for handler in _attrObserversDict.get(name, []):
                handler(value)

    def _registerAttrObserver(self, name, handler):
        try:
            handlerList = _attrObserversDict[name]
        except KeyError:
            handlerList = []
            _attrObserversDict[name] = handlerList
        handlerList.append(handler)

    obj.__setattr__ = bind(obj, newSetAttr)
    obj._registerAttrObserver = bind(obj, _registerAttrObserver)

    # setitem prohibited
    def prohibited(self, *args, **kwargs):
        raise RuntimeError("Cannot use __setitem__ on observable object")

    obj.__setitem__ = bind(obj, prohibited)
    obj.__getitem__ = bind(obj, prohibited)
