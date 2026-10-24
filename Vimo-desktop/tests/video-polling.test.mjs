import assert from 'node:assert/strict'
import test from 'node:test'

import { shouldStartVideoStatusPoll } from '../src/renderer/src/lib/video-polling.ts'

test('does not start a duplicate polling loop for an already-processing video', () => {
  assert.equal(shouldStartVideoStatusPoll(undefined), true)
  assert.equal(shouldStartVideoStatusPoll({ status: 'processing' }), false)
  assert.equal(shouldStartVideoStatusPoll({ status: 'completed' }), false)
  assert.equal(shouldStartVideoStatusPoll({ status: 'error' }), false)
})
