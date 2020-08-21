def configureModel(obj, onInput, setValue, *, attr=None, index=None):
    if index is None:
        setValue(getattr(obj, attr))
        obj._registerAttrObserver(attr, setValue)

        def _(v):
            oldV = getattr(obj, attr)
            if oldV != v:
                setattr(obj, attr, v)

        onInput(_)

    elif attr is None:
        setValue(obj[index])
        obj._registerItemObserver(lambda: setValue(obj[index]))

        def _(v):
            oldItem = obj[index]
            if oldItem != v:
                obj[index] = v

        onInput(_)

    else:
        raise RuntimeError("at least one of attr and index should be None")
