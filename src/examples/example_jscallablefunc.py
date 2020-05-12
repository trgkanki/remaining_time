from ..jsBridge import JSCallableFunc

@JSCallableFunc
def test(a, b):
    return a + b

"""
// JS counterpart code
import { callPyFunc } from './pyfunc'

callPyFunc('test', 1, 2).then(ret => {
  alert(`Test addon initiailized, pyfunc test returned ${ret}`)
})
"""
