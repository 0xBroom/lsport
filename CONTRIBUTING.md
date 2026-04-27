# Contributing to portctl

First off, thank you for considering contributing to portctl! It's people like you that make portctl such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed and what you expected to see
- Include screenshots if relevant
- Include your environment details (macOS version, Python version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- List any alternative solutions you've considered

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing code style
5. Write a clear commit message

## Development Setup

### Prerequisites

- macOS (portctl is macOS-only)
- Python 3.9 or higher
- pip

### Setting up your development environment

1. **Clone your fork:**

   ```bash
   git clone https://github.com/YOUR_USERNAME/portctl.git
   cd portctl
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install the tool in development mode:**

   You can symlink the script to test it locally:

   ```bash
   ln -sf "$(pwd)/portctl.py" /usr/local/bin/portctl-dev
   ```

### Running Tests

We use pytest for testing. Make sure all tests pass before submitting a PR:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=portctl

# Run specific test file
pytest tests/test_portctl.py

# Run a specific test
pytest tests/test_portctl.py::TestGetOpenPorts::test_get_open_ports_basic
```

### Code Style

We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for linting issues
python3 -m ruff check portctl.py

# Auto-fix issues
python3 -m ruff check --fix portctl.py

# Format code
python3 -m ruff format portctl.py
```

**Key style guidelines:**

- Line length: 120 characters
- Use double quotes for strings
- Follow PEP 8 naming conventions
- Use type hints for function signatures
- Write docstrings for public functions
- Keep functions focused and small

### Type Checking

We use mypy for optional type checking:

```bash
mypy portctl.py
```

## Project Structure

```
portctl/
├── portctl.py           # Main CLI application (single file)
├── install.sh           # Installation script for macOS
├── tests/               # Test suite
│   ├── test_portctl.py  # Unit tests
│   └── test_cli.py      # CLI integration tests
├── pyproject.toml       # Project configuration
├── requirements.txt     # Dependencies
├── README.md            # User documentation
└── CONTRIBUTING.md      # This file
```

## Commit Message Guidelines

We follow conventional commits for clear and standardized commit messages:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Adding or updating tests
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

**Examples:**

```
feat: Add support for UDP port listing
fix: Handle permission errors when killing processes
docs: Update README with installation instructions
test: Add tests for port filtering functionality
```

## Testing Guidelines

- Write tests for all new features
- Ensure existing tests still pass
- Use mocks for external dependencies (psutil, file system, etc.)
- Aim for high code coverage (we're currently at 68%)
- Test both success and error cases

## Pull Request Process

1. **Update documentation** if you're changing functionality
2. **Add tests** for new features or bug fixes
3. **Run the full test suite** and ensure everything passes
4. **Update the CHANGELOG.md** with your changes
5. **Request review** from maintainers
6. **Address feedback** and make requested changes
7. **Merge** once approved (maintainers will handle this)

## Development Tips

### Testing portctl locally

```bash
# Test list command
./portctl.py list

# Test with state filter
./portctl.py list -s listen

# Test kill command (be careful!)
./portctl.py kill 8080 --yes
```

### Debugging

Add print statements or use Python's debugger:

```python
import pdb; pdb.set_trace()
```

### Common Issues

**"Command not found" after symlinking:**
- Ensure `/usr/local/bin` is in your PATH
- Check the symlink: `ls -la /usr/local/bin/portctl`

**Tests failing:**
- Make sure you have all dependencies: `pip install -r requirements.txt`
- Check Python version: `python3 --version` (must be 3.9+)

**Permission errors:**
- Some operations require elevated privileges
- The `kill` command may need sudo depending on the process owner

## Questions?

Feel free to open an issue with the "question" label, or reach out to the maintainers.

## Recognition

Contributors will be recognized in the project README. Thank you for making portctl better!
