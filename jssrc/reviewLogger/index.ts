import { ReviewLogger } from './types'
import { MobileReviewLogger } from './mobileReviewLogger'

let cached: ReviewLogger | null = null

export async function getReviewLogger (): Promise<ReviewLogger> {
  if (!cached) cached = new MobileReviewLogger()
  return cached
}
