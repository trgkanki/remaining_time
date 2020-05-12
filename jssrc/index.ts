import { callPyFunc } from './utils/pyfunc'

callPyFunc('test', 1, 2).then(ret => {
  alert(`Test addon initiailized, pyfunc test returned ${ret}`)
})
