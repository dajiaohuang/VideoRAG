import assert from 'node:assert/strict'
import test from 'node:test'

import { createRequestGuard } from '../src/renderer/src/utils/request-guard.ts'

test('new requests supersede older results and cleanup invalidates the current request', () => {
  const guard = createRequestGuard()
  const oldRequest = guard.begin()
  const currentRequest = guard.begin()

  assert.equal(guard.isCurrent(oldRequest), false)
  assert.equal(guard.isCurrent(currentRequest), true)

  guard.invalidate(currentRequest)
  assert.equal(guard.isCurrent(currentRequest), false)
})

test('stale cleanup cannot invalidate a newer request', () => {
  const guard = createRequestGuard()
  const oldRequest = guard.begin()
  const currentRequest = guard.begin()

  guard.invalidate(oldRequest)
  assert.equal(guard.isCurrent(currentRequest), true)
})
