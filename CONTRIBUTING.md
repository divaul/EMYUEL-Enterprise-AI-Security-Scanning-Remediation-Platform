# Contributing to EMYUEL

Thank you for considering contributing to EMYUEL! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/your-org/emyuel/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with `[Feature Request]` prefix
3. Describe the feature and use case
4. Explain why this would be valuable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Ensure all tests pass
6. Update documentation
7. Commit with clear messages
8. Push to your fork
9. Open a Pull Request

## Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/emyuel.git
cd emyuel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest
```

## Coding Standards

### Python Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions/classes
- Maximum line length: 100 characters

### Commit Messages

Format: `type(scope): description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example:
```
feat(scanner): add RCE detector
fix(api): correct CORS headers
docs(readme): update installation steps
```

### Testing

- Write tests for new features
- Maintain minimum 80% code coverage
- Run full test suite before submitting PR

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=services

# Run specific test
pytest tests/test_scanner.py::test_sqli_detection
```

## Project Structure

```
emyuel/
├── services/           # Microservices
├── libs/               # Shared libraries
├── tests/              # Test suites
├── docs/               # Documentation
├── configs/            # Configuration files
└── database/           # Database migrations
```

## Adding a New Vulnerability Detector

1. Create detector in `services/scanner-core/detectors/`
2. Inherit from base detector class
3. Implement required methods
4. Add tests in `tests/detectors/`
5. Update documentation

Example:

```python
# services/scanner-core/detectors/my_detector.py

class MyVulnerabilityDetector:
    def __init__(self, llm_orchestrator):
        self.llm = llm_orchestrator
    
    async def analyze(self, source_code, file_path, context):
        # Implementation
        pass
```

## Documentation

- Update relevant documentation when adding features
- Use clear, concise language
- Include code examples where appropriate
- Keep README.md up to date

## Release Process

1. Update version in `__version__.py`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release with notes
6. Deploy to production

## Questions?

- GitHub Discussions
- Email: dev@emyuel.io
- Slack: [Join our Slack](https://slack.emyuel.io)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
