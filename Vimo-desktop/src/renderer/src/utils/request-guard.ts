export function createRequestGuard() {
  let currentRequest = 0

  return {
    begin(): number {
      currentRequest += 1
      return currentRequest
    },
    isCurrent(requestId: number): boolean {
      return requestId === currentRequest
    },
    invalidate(requestId: number): void {
      if (requestId === currentRequest) currentRequest += 1
    },
  }
}
