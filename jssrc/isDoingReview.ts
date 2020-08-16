import ankiLocalStorage from './utils/ankiLocalStorage'

/**
 * epoch in seconds
 */
function now () {
  return new Date().getTime() / 1000
}

const windowAny = window as any
if (!windowAny._rtIsDoingReview) {
  windowAny._rtIsDoingReview = true

  ankiLocalStorage.setItem('_rt_lasttime', now().toString())
  setInterval(() => {
    ankiLocalStorage.setItem('_rt_lasttime', now().toString())
  }, 1000)
}

export async function onSameReviewSession () {
  const lastTimeString = await ankiLocalStorage.getItem('_rt_lasttime')
  if (!lastTimeString) return false
  const currentTime = now()

  return (currentTime - Number(lastTimeString)) < 3
}
