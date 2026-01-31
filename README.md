# Pithos

**Pithos**, a repo template for experiments, scripts, tools, and ideas.

## Structure

- **`projects/`**: Self-contained mini-projects (e.g., `projects/react-test`).
- **`examples/`**: Minimal code examples (e.g., `examples/rust/async-demo`).
- **`scripts/`**: Single-file executables or automation scripts.
- **`libs/`**: Shared libraries (`libs/cpp`, `libs/go`, etc.).
- **`snippets/`**: Copy-paste reference material.
- **`notebooks/`**: Jupyter notebooks.
- **`ideas/`**: Docs/Notes.
- **`scratch/`**: Temporary files (git-ignored).

## Installation (Mac)

You need **Just** and the languages you plan to use.

```bash
# 1. Install the runner (Required)
brew install just

# 2. Run the setup script
./setup.sh

# 3. Activates environment
source activate.zsh
```

### Quick Start

Use `just` to create, build, run, and test anything.

```bash
# 1. Create
just new-project-cpp my-app      # demos a "Project" (complex)
just new-script my-script        # demos a "Script" (simple)

# 2. Build & Run
just run my-app          # Runs projects/my-app
just run my-script       # Runs scripts/my-script.py

# 3. Clean
just clean               # Wipes build/gen/venv artifacts
```

## Usage

### 1. Using IDLs
1.  Add your `.proto` file to `idl/` (e.g., `idl/common/user.proto`).
2.  Run `just gen-proto common/user.proto`.
3.  The code is generated into `gen/cpp`, `gen/go`, etc.
4.  **Importing**:
    -   **C++**: Add `../../gen/cpp` to include paths.
    -   **Go**: Import `pithos/gen/go/pithos/common` (Auto-wired via `go.work` by `just`).

### 2. Using Shared Libs
Code in `libs/` is meant to be shared.
-   **Python Usage**:
    -   **Simple Scripts**: Use the shared root environment automatically.
    -   **Projects**: Add a `pyproject.toml` to your project folder. The runner detects it and uses a **project-isolated** environment via `uv`.
-   **Go Usage**: `just new-project-go` automatically registers projects in `go.work`.

### 3. Example Demos
Check `examples/` for full examples that use **Protobuf** and **Shared Libraries**:

| Language | Project |
| :--- | :--- |
| **C++** | `examples/cpp/proto-demo` |
| **Go** | `examples/go/proto-demo` |
| **Python** | `examples/python/proto-demo` |

```bash
just run cpp/proto-demo
just run go/proto-demo
just run python/proto-demo
```

## Maintenance

### Keeping Updated
You can pull new features/fixes from the upstream template at any time.

```bash
just sync-template
```
*Auto-fetches from remote `upstream` and merges updates.*
*Note: For smooth updates, you should **Start with a Git Clone**. Updating from a ZIP download works but may cause "Add/Add" conflicts because history is missing.*
