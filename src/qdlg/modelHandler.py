from .observable.ObservableBase import ObservableBase


def configureModel(obj: ObservableBase, onInput, setValue, *, attr=None, index=None):
    if index is None:
        oldValue = getattr(obj, attr)
        setValue(oldValue)

        def _setter():
            nonlocal oldValue
            v = getattr(obj, attr)
            if v != oldValue:
                oldValue = v
                setValue(v)

        obj.registerObserver(_setter)

        def _onInput(v):
            nonlocal oldValue
            if oldValue != v:
                oldValue = v
                setattr(obj, attr, v)

        onInput(_onInput)

    elif attr is None:
        oldValue = obj[index]
        setValue(obj[index])

        def _setter():
            nonlocal oldValue
            v = obj[index]
            if v != oldValue:
                oldValue = v
                setValue(v)

        obj.registerObserver(_setter)

        def _onInput(v):
            nonlocal oldValue
            if oldValue != v:
                oldValue = v
                obj[index] = v

        onInput(_onInput)

    else:
        raise RuntimeError("at least one of attr and index should be None")
