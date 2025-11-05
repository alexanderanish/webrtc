# Contributing to WebRTC Enterprise Library

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Git

### Setup Development Environment

1. Fork and clone the repository:
```bash
git clone https://github.com/yourusername/webrtc-enterprise.git
cd webrtc-enterprise
```

2. Install dependencies:
```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
cd packages/server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Making Changes

1. Create a branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes

3. Test your changes:
```bash
# Client tests
cd packages/client
npm test

# Server tests
cd packages/server
pytest
```

4. Commit with conventional commits:
```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in WebRTC connection"
git commit -m "docs: update API documentation"
```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Code Standards

### TypeScript/JavaScript

- Use TypeScript for all new code
- Follow ESLint rules
- Write JSDoc comments for public APIs
- Include unit tests

Example:
```typescript
/**
 * Send data through the data channel
 * @param message - The message to send
 * @throws {Error} If data channel is not open
 */
async sendData(message: DataMessage): Promise<void> {
  // implementation
}
```

### Python

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all public functions
- Include unit tests

Example:
```python
async def send_text(self, text: str) -> str:
    """
    Send text message to Gemini and get response.

    Args:
        text: Input text message

    Returns:
        Response text from Gemini

    Raises:
        Exception: If not connected to Gemini
    """
    # implementation
```

### Testing

- Write unit tests for new features
- Maintain test coverage above 80%
- Test edge cases and error conditions

Client tests:
```typescript
describe('WebRTCClient', () => {
  it('should connect to signaling server', async () => {
    const client = new WebRTCClient(config);
    await client.connect();
    expect(client.isConnected).toBe(true);
  });
});
```

Server tests:
```python
async def test_create_session():
    server = WebRTCServer()
    session = await server.create_session(SessionConfig(session_id="test"))
    assert session.session_id == "test"
```

## Documentation

### Code Documentation

- Document all public APIs
- Include usage examples
- Explain complex algorithms
- Add inline comments for clarity

### User Documentation

When adding features, update:
- README.md
- API documentation (docs/client-api.md or docs/server-api.md)
- Examples
- Deployment guide if needed

## Pull Request Process

1. Update documentation
2. Add/update tests
3. Run linting and tests
4. Update CHANGELOG.md
5. Create pull request with:
   - Clear title and description
   - Reference related issues
   - Screenshots/demos if applicable

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test the changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] No new warnings
```

## Architecture Guidelines

### Client Library

- Keep bundle size small
- Use event-driven architecture
- Provide React hooks for common patterns
- Handle errors gracefully
- Support reconnection

### Server Library

- Use async/await throughout
- Implement proper resource cleanup
- Log important events
- Handle WebSocket disconnections
- Support multiple concurrent sessions

## Security

### Reporting Vulnerabilities

Email security issues to: security@yourdomain.com

Do not create public issues for security vulnerabilities.

### Security Checklist

- Never commit API keys or secrets
- Validate all inputs
- Use HTTPS/WSS in production
- Implement rate limiting
- Add authentication where needed

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Publish to npm/PyPI

## Questions?

- Open an issue for bugs or feature requests
- Join our Discord for discussions
- Check existing issues and PRs

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Give constructive feedback
- Focus on what's best for the project

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
