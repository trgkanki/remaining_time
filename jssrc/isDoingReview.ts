import ankiLocalStorage from './utils/ankiLocalStorage'
import { now } from './utils'

const kRtLastTime = '_rt_lastTime'

const windowAny = window as any
if (!windowAny._rtIsDoingReview) {
  windowAny._rtIsDoingReview = true

  ankiLocalStorage.setItem(kRtLastTime, now().toString())
  setInterval(() => {
    ankiLocalStorage.setItem(kRtLastTime, now().toString())
  }, 1000)
}

export async function onSameReviewSession () {
  const lastTimeString = await ankiLocalStorage.getItem(kRtLastTime)
  if (!lastTimeString) return false
  const currentTime = now()

  return (currentTime - Number(lastTimeString)) < 3
}
