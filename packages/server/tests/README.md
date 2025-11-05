# Server Tests

Comprehensive test suite for the `webrtc-enterprise-server` package.

## Running Tests

### All Tests

```bash
pytest
```

### With Coverage

```bash
pytest --cov=webrtc_enterprise --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Specific Test Files

```bash
pytest tests/test_signaling.py
pytest tests/test_server.py
pytest tests/test_gemini_integration.py
pytest tests/test_types.py
```

### Verbose Output

```bash
pytest -v
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures and configuration
├── test_signaling.py        # SignalingServer tests
├── test_server.py           # WebRTCServer and WebRTCSession tests
├── test_gemini_integration.py  # Gemini integration tests
└── test_types.py            # Type definition tests
```

## Test Coverage

Current coverage targets:
- Overall: 80%+
- Critical paths: 90%+

## Writing Tests

### Unit Tests

Mark with `@pytest.mark.unit`:

```python
@pytest.mark.unit
class TestMyFeature:
    def test_something(self):
        assert True
```

### Integration Tests

Mark with `@pytest.mark.integration`:

```python
@pytest.mark.integration
class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_flow(self):
        # Test complete workflow
        pass
```

### Async Tests

Use `@pytest.mark.asyncio` for async functions:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Fixtures

Common fixtures available in `conftest.py`:

- `media_config` - MediaConfig instance
- `session_config` - SessionConfig instance
- `signaling_server` - SignalingServer instance
- `webrtc_server` - WebRTCServer instance
- `mock_websocket` - Mocked WebSocket
- `mock_peer_connection` - Mocked RTCPeerConnection
- `mock_gemini` - Mocked GeminiIntegration
- `mock_media_stream_track` - Mocked MediaStreamTrack

## CI/CD

Tests run automatically on:
- Pull requests
- Commits to main/develop branches

Required:
- All tests must pass
- Coverage must be ≥80%
- No linting errors
