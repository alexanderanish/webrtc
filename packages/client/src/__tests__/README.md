# Client Tests

Test suite for the `@webrtc-enterprise/client` package.

## Running Tests

### All Tests

```bash
npm test
```

### Watch Mode

```bash
npm test -- --watch
```

### With Coverage

```bash
npm test -- --coverage
```

### Specific Test File

```bash
npm test -- WebRTCClient.test.ts
npm test -- hooks.test.ts
```

### Update Snapshots

```bash
npm test -- -u
```

## Test Structure

```
src/__tests__/
├── setup.ts                 # Test setup and mocks
├── WebRTCClient.test.ts     # WebRTCClient tests
└── hooks.test.ts            # React hooks tests
```

## Test Coverage

Current coverage targets:
- Overall: 80%+
- Critical paths: 90%+

View coverage report:
```bash
open coverage/lcov-report/index.html
```

## Writing Tests

### Basic Test

```typescript
describe('MyFeature', () => {
  it('should do something', () => {
    expect(true).toBe(true);
  });
});
```

### Async Tests

```typescript
it('should handle async operation', async () => {
  const result = await asyncFunction();
  expect(result).toBeDefined();
});
```

### Testing Hooks

```typescript
import { renderHook, act } from '@testing-library/react';

it('should use hook correctly', () => {
  const { result } = renderHook(() => useMyHook());

  act(() => {
    result.current.doSomething();
  });

  expect(result.current.value).toBe(expected);
});
```

### Mocking

WebRTC APIs are automatically mocked in `setup.ts`:
- `RTCPeerConnection`
- `RTCSessionDescription`
- `RTCIceCandidate`
- `WebSocket`
- `navigator.mediaDevices.getUserMedia`

## Mocked APIs

All WebRTC browser APIs are mocked for testing:

```typescript
// WebSocket mock
const mockWs = new WebSocket('ws://test');
mockWs.send('data');

// RTCPeerConnection mock
const mockPc = new RTCPeerConnection();
await mockPc.createOffer();

// getUserMedia mock
const stream = await navigator.mediaDevices.getUserMedia({
  audio: true
});
```

## CI/CD

Tests run automatically on:
- Pull requests
- Commits to main branch

Required:
- All tests must pass
- Coverage must be ≥80%
- No TypeScript errors
- No linting errors

## Debugging Tests

### Run Single Test

```bash
npm test -- -t "test name pattern"
```

### Debug in VS Code

Add to `.vscode/launch.json`:

```json
{
  "type": "node",
  "request": "launch",
  "name": "Jest Debug",
  "program": "${workspaceFolder}/node_modules/.bin/jest",
  "args": ["--runInBand"],
  "console": "integratedTerminal"
}
```

### Verbose Output

```bash
npm test -- --verbose
```
