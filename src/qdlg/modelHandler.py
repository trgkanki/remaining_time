def configureModel(obj, attrName, onInput, setValue):
    setValue(getattr(obj, attrName))
    obj._registerAttrObserver(attrName, setValue)

    def _(v):
        oldV = getattr(obj, attrName)
        if oldV != v:
            setattr(obj, attrName, v)

    onInput(_)
