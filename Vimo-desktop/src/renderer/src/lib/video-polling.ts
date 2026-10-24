export interface PollableVideoStatus {
  status: string
}

export function shouldStartVideoStatusPoll(
  status: PollableVideoStatus | undefined
): boolean {
  return status === undefined
}
