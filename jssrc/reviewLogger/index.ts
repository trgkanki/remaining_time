import isMobile from 'is-mobile'
import { ReviewLogger } from './types'
import { MobileReviewLogger } from './mobileReviewLogger'
import { DesktopReviewLogger } from './desktopReviewLogger'

let cached: ReviewLogger | null = null

export async function getReviewLogger (): Promise<ReviewLogger> {
  if (!cached) cached = isMobile() ? new MobileReviewLogger() : new DesktopReviewLogger()
  return cached
}
