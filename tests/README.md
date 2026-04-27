# Tests for portctl

This directory contains the test suite for portctl.

## Test Structure

- `test_portctl.py` - Unit tests for core functions
- `test_cli.py` - Integration tests for CLI commands

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=portctl

# Run specific test file
pytest tests/test_portctl.py

# Run specific test
pytest tests/test_portctl.py::TestGetOpenPorts::test_get_open_ports_basic
```

## Test Coverage

The test suite covers:
- Port listing with various filters
- Process killing functionality
- Error handling (NoSuchProcess, AccessDenied)
- CLI command integration
- State validation
