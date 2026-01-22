# Build, Release, and Local Integration Guide

This document outlines how to build the distribution packages for **Zettel-Memory**, how to publish them, and how to use this library in other local projects.

## 1. Build (Compilation)

Since this is a Python project, "compilation" mainly means packaging the source code into distribution formats (Source Archive and Wheel).

### Prerequisites

Install build tools:

```bash
pip install build twine
```

### Build Command

Run the following command in the project root directory:

```bash
python -m build
```

This will generate a `dist/` directory containing:

- `zettel_memory-0.1.0.tar.gz` (Source Distribution)
- `zettel_memory-0.1.0-py3-none-any.whl` (Built Distribution / Wheel)

---

## 2. Deployment (Publishing to PyPI)

To make your library available via `pip install zettel-memory`, you need to upload it to the Python Package Index (PyPI).

### Steps

1. **Check the package** (Optional but recommended):

   ```bash
   twine check dist/*
   ```

2. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```
   _You will need a PyPI account and an API Token._

---

## 3. Local Integration (Using in Another Project)

If you have another project (e.g., `MyAgentBot`) on your machine and want to use `zettel-memory` without publishing it to PyPI, use **Editable Install** or **Local Path Install**.

### Method A: Editable Install (Recommended for Dev)

This creates a symlink-like reference. Any changes you make to the `zettel-memory` code will immediately trigger in your other project.

1. Navigate to your other project:
   ```bash
   cd ~/Develop/MyAgentBot
   source .venv/bin/activate
   ```
2. Install Zettel-Memory in editable mode:
   ```bash
   pip install -e /Users/arthur/Develop/project-zettel-memory
   ```

### Method B: Path Install (Stable)

This copies the files. Changes in `zettel-memory` won't affect the other project until you reinstall.

```bash
pip install /Users/arthur/Develop/project-zettel-memory
```

### Verification

In your other project's Python shell:

```python
import zettel_memory
print(zettel_memory.__file__)
# Should output: /Users/arthur/Develop/project-zettel-memory/zettel_memory/__init__.py
```
