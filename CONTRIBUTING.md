# Contributing to Zettel-Memory

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

1.  **Fork the repo** and create your branch from `main`.
2.  **Setup Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .[dev]
    ```
3.  **Run Tests**:
    ```bash
    pytest tests/
    ```
4.  **Code Style**: We use `black` and `pydantic`. Please ensure your code follows standard Python practices.
5.  **Pull Requests**:
    - Include a clear description of the change.
    - Ensure all tests pass.
    - Add new tests for new features.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
