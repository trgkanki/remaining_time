import { ReviewLogger } from './types'
import { MobileReviewLogger } from './mobileReviewLogger'
import { DesktopReviewLogger } from './desktopReviewLogger'
import { isAnkiDroid } from '../utils/apiAnkiDroid'

let cached: ReviewLogger | null = null

export async function getReviewLogger (): Promise<ReviewLogger> {
  if (!cached) cached = isAnkiDroid() ? new MobileReviewLogger() : new DesktopReviewLogger()
  return cached
}
