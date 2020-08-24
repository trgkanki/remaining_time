import ankiLocalStorage from './utils/ankiLocalStorage'
import { now } from './utils'

const windowAny = window as any
if (!windowAny._rtIsDoingReview) {
  windowAny._rtIsDoingReview = true

  ankiLocalStorage.setItem('_rt_lastTime', now().toString())
  setInterval(() => {
    ankiLocalStorage.setItem('_rt_lastTime', now().toString())
  }, 1000)
}

export async function onSameReviewSession () {
  const lastTimeString = await ankiLocalStorage.getItem('_rt_lastTime')
  if (!lastTimeString) return false
  const currentTime = now()

  return (currentTime - Number(lastTimeString)) < 3
}
