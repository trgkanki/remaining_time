import ankiPersistentStorage from './utils/ankiPersistentStorage'
import { now } from './utils'

export const kRtLastTime = '_rt_lastTime'

const windowAny = window as any
if (!windowAny._rtIsDoingReview) {
  windowAny._rtIsDoingReview = true

  ankiPersistentStorage.setItem(kRtLastTime, now().toString())
  setInterval(() => {
    ankiPersistentStorage.setItem(kRtLastTime, now().toString())
  }, 1000)
}

export async function onSameReviewSession () {
  const lastTimeString = await ankiPersistentStorage.getItem(kRtLastTime)
  if (!lastTimeString) return false
  const currentTime = now()

  return (currentTime - Number(lastTimeString)) < 3
}
