# Contributing to Rodent AI Vision Box

First off, thank you for considering contributing to Rodent AI Vision Box! It's people like you that make this project better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and expected**
- **Include logs and screenshots if possible**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Provide specific examples to demonstrate the enhancement**
- **Describe the current behavior and explain the expected behavior**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `develop`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows the style guidelines
6. Issue that pull request!

## Development Process

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/rodent-ai-vision-box.git
cd rodent-ai-vision-box

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make dev-install
```

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all checks:
```bash
make check-all
```

Format code:
```bash
make format
```

### Testing

Write tests for any new functionality:

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_detection_engine.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Commit Messages

Follow conventional commits specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add support for multiple camera sources
fix: resolve memory leak in video processing
docs: update installation instructions
```

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Urgent fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## Project Structure

```
rodent-ai-vision-box/
├── src/                 # Source code
│   ├── detection_engine.py
│   ├── alert_engine.py
│   └── ...
├── tests/              # Test suite
│   ├── unit/
│   └── integration/
├── config/             # Configuration files
├── models/             # Model files
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

## Documentation

- Update docstrings for all public functions
- Use Google-style docstrings
- Update README.md for user-facing changes
- Update technical documentation for implementation details

Example docstring:
```python
def detect_rodents(image: np.ndarray, confidence: float = 0.25) -> List[Detection]:
    """Detect rodents in an image.
    
    Args:
        image: Input image as numpy array (H, W, C).
        confidence: Minimum confidence threshold for detections.
    
    Returns:
        List of Detection objects containing bounding boxes and classes.
    
    Raises:
        ValueError: If image is not in correct format.
    """
```

## Release Process

1. Update version in `setup.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create pull request to `main`
4. After merge, tag the release: `git tag -a v1.0.0 -m "Release version 1.0.0"`
5. Push tags: `git push origin --tags`

## Questions?

Feel free to open an issue with your questions or reach out to the maintainers.

## Recognition

Contributors will be recognized in:
- The project README
- Release notes
- Project documentation

Thank you for contributing to make rodent detection better for everyone! 🐀🤖