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
    return bound_method


def _forwardMethod(key, callHandlersAfter):
    def _(self, *args, **kwargs):
        with self._noNotify():
            ret = getattr(self._obj, key)(*args, **kwargs)

        if callHandlersAfter:
            self.notify()

        return ret

    return _
