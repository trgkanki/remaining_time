from .obsproxy import observable
from nose.tools import with_setup, assert_equal


notified = set()


def register(v):
    def _():
        notified.add(id(v))

    v.registerObserver(_)


def assertNotified(*items):
    assert len(items) == len(notified)
    for item in items:
        assert id(item) in notified


a = observable([])


def setup_func():
    global a
    a = observable([1, 3])
    register(a)
    notified.clear()


def teardown_func():
    pass


# Test for notifying things
@with_setup(setup_func, teardown_func)
def test_list_setitem():
    a[0] = 2
    assert a == [2, 3]
    assert notified == {id(a)}


@with_setup(setup_func, teardown_func)
def test_list_append():
    a.append(4)
    assert notified == {id(a)}
    assert a == [1, 3, 4]


@with_setup(setup_func, teardown_func)
def test_list_pop():
    a.pop()
    assert notified == {id(a)}
    assert a == [1]


@with_setup(setup_func, teardown_func)
def test_list_pop():
    a.clear()
    assert notified == {id(a)}
    assert a == []


@with_setup(setup_func, teardown_func)
def test_list_extend():
    a.extend([4, 7])
    assert notified == {id(a)}
    assert a == [1, 3, 4, 7]


@with_setup(setup_func, teardown_func)
def test_list_insert():
    a.insert(1, 5)
    assert notified == {id(a)}
    assert a == [1, 5, 3]


# Test for non-notifying tests


@with_setup(setup_func, teardown_func)
def test_list_getitem():
    assert_equal(a[1], 3)
    assert not notified
    assert a == [1, 3]


@with_setup(setup_func, teardown_func)
def test_list_str_repr():
    assert_equal(str(a), "[1, 3]")
    assert_equal(repr(a), "[1, 3]")
    assert not notified


@with_setup(setup_func, teardown_func)
def test_list_len():
    assert_equal(len(a), 2)
    assert not notified


@with_setup(setup_func, teardown_func)
def test_list_index():
    assert_equal(a.index(3), 1)
    assert not notified


@with_setup(setup_func, teardown_func)
def test_list_count():
    assert_equal(a.count(1), 1)
    assert_equal(a.count(4), 0)
    assert not notified


def test_nested_list():
    a = observable([[1, 2], [3, 4]])
    register(a)
    register(a[0])
    register(a[1])

    notified.clear()
    a[0][0] = 0
    assert a == [[0, 2], [3, 4]]
    assertNotified(a, a[0])


class TestClass:
    def __init__(self):
        self.l = [1, 2]


def test_nested_object_list():
    a = observable(TestClass())
    register(a)
    register(a.l)

    notified.clear()
    a.l[0] = 3
    assert a.l == [3, 2]
    assertNotified(a, a.l)


class TestClass2:
    def __init__(self):
        self.a = 4


def test_nested_list_object():
    a = observable([TestClass2(), TestClass2()])
    register(a)
    register(a[0])
    register(a[1])

    notified.clear()
    assert a[0].a == 4
    assert not notified
    a[0].a = 3
    assert a[0].a == 3
    assertNotified(a, a[0])
