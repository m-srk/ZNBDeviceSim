# Contributing to ZNBDeviceSim

Thank you for your interest in contributing to ZNBDeviceSim! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in [Issues](https://github.com/m-srk/ZNBDeviceSim/issues)
- If not, create a new issue with:
  - Clear title and description
  - Steps to reproduce
  - Expected vs actual behavior
  - Python version and OS

### Suggesting Enhancements

- Open an issue with the `enhancement` label
- Describe the feature and its use case
- Explain why it would be useful

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`python -m unittest test_ZonedNBDevice`)
6. Commit with clear messages (`git commit -m 'Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/m-srk/ZNBDeviceSim.git
cd ZNBDeviceSim

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest test_ZonedNBDevice -v
```

## Code Style

- Follow PEP 8 guidelines
- Add docstrings to public methods
- Keep functions focused and concise
- Add type hints where appropriate

## Testing

- Write unit tests for new features
- Ensure existing tests pass
- Aim for meaningful test coverage

## Questions?

Feel free to open an issue for any questions or clarifications.
