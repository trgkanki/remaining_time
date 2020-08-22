_notified = set()


def registerNotification(*items):
    for v in items:

        def _():
            _notified.add(id(v))

        v.registerObserver(_)


def assertNotified(*items):
    assert len(items) == len(_notified)
    for item in items:
        assert id(item) in _notified


def resetNotification():
    _notified.clear()
