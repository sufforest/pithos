#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_cmd(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)} in {cwd or '.'}")
    env = os.environ.copy()
    
    # Fix for macOS: Ensure SDKROOT is set so Clang finds <string>, <iostream>
    if sys.platform == "darwin" and "SDKROOT" not in env:
        try:
            sdk_path = subprocess.check_output(["xcrun", "--show-sdk-path"]).decode().strip()
            env["SDKROOT"] = sdk_path
        except:
             pass # Fallback to system default if xcrun fails

    try:
        subprocess.check_call(cmd, cwd=cwd, env=env)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

# --- Utils ---

def find_repo_root(start_path: Path) -> Path:
    current = start_path.absolute()
    while current != current.parent:
        if (current / "Justfile").exists():
            return current
        current = current.parent
    return start_path # Fallback (shouldn't happen in repo)

def check_tool(cmd_name, install_hint):
    """Lazy check: is the tool installed? If not, valid exit with hint."""
    import shutil
    if not shutil.which(cmd_name):
        print(f"Error: '{cmd_name}' is not installed or not in PATH.")
        print(f"Hint: {install_hint}")
        sys.exit(1)

# --- Language Handlers ---

class Handler:
    def build(self, path):
        print(f"Build command not implemented for {type(self).__name__} at {path}")
        sys.exit(1)
    def test(self, path):
        print(f"Test command not implemented for {type(self).__name__} at {path}")
        sys.exit(1)
    def run(self, path):
        print(f"Run command not implemented for {type(self).__name__} at {path}")
        sys.exit(1)

class CppHandler(Handler):
    def build(self, path):
        check_tool("cmake", "brew install cmake")
        build_dir = path / "build"
        build_dir.mkdir(exist_ok=True)
        
        cmake_cmd = ["cmake", "-S", ".", "-B", "build", "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"]
        
        # Explicitly set Sysroot on macOS to avoid "file not found" errors
        if sys.platform == "darwin":
            try:
                sdk_path = subprocess.check_output(["xcrun", "--show-sdk-path"]).decode().strip()
                cmake_cmd.append(f"-DCMAKE_OSX_SYSROOT={sdk_path}")
            except:
                pass

        run_cmd(cmake_cmd, cwd=path)

        # Symlink compile_commands.json to root for LSP support
        compile_commands = path / "build" / "compile_commands.json"
        target_link = path / "compile_commands.json"
        if compile_commands.exists():
            if target_link.exists() or target_link.is_symlink():
                target_link.unlink()
            try:
                target_link.symlink_to(compile_commands)
                print(f"Symlinked {compile_commands} -> {target_link}")
            except OSError as e:
                print(f"Warning: Failed to symlink compile_commands.json: {e}")
        run_cmd(["cmake", "--build", "build"], cwd=path)
    def test(self, path):
        check_tool("ctest", "brew install cmake")
        build_dir = path / "build"
        if build_dir.exists():
             run_cmd(["ctest", "--output-on-failure"], cwd=build_dir)
        else:
            print("Build directory not found. Run build first.")
            sys.exit(1)
    def run(self, path):
        # Always attempt to build before running (like cargo/go)
        # This fixes incremental builds and recovery from bad state
        self.build(path)
        
        build_dir = path / "build"
        # Find executable relative to build
        # Exclude CMake internals (CMakeFiles) and standard extensions
        for root, dirs, files in os.walk(build_dir):
             if "CMakeFiles" in dirs:
                 dirs.remove("CMakeFiles") # Don't visit
             
             for f in files:
                p = Path(root) / f
                if os.access(p, os.X_OK) and not p.name.endswith(".bin") and not p.suffix in ['.cmake', '.txt', '.o', '.dylib', '.a']:
                     run_cmd([str(p)], cwd=path)
                     return
        print("No executable found in build directory.")
        sys.exit(1)

class RustHandler(Handler):
    def build(self, path): 
        check_tool("cargo", "brew install rustup-init/rust OR curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
        run_cmd(["cargo", "build"], cwd=path)
    def test(self, path): 
        check_tool("cargo", "brew install rust")
        run_cmd(["cargo", "test"], cwd=path)
    def run(self, path): 
        check_tool("cargo", "brew install rust")
        run_cmd(["cargo", "run"], cwd=path)

# --- Proto Generation ---
def ensure_protos(root, lang):
    """Lazy generation: Check if idl/*.proto is newer than gen/{lang}."""
    idl_dir = root / "idl"
    gen_dir = root / "gen" / lang
    
    if not idl_dir.exists(): return

    # Gather all proto files (recursive)
    protos = list(idl_dir.rglob("*.proto"))
    if not protos: return

    should_gen = False
    
    # If gen dir missing, must gen
    if not gen_dir.exists():
        should_gen = True
    else:
        # Check timestamps
        # Simple heuristic: if ANY proto is newer than the gen dir itself (or a marker), regen.
        latest_proto = max(p.stat().st_mtime for p in protos)
        gen_mtime = gen_dir.stat().st_mtime
        if latest_proto > gen_mtime:
            should_gen = True

    if should_gen:
        print(f"IDLs changed. Regenerating {lang} code...")
        # running 'just gen-proto' (requires just to be installed)
        # We invoke it for each file.
        for p in protos:
            # We assume 'just' is in path (it is if using mise/activate)
            # If not, we skip with warning
            try:
                # Pass path relative to idl/ dir so Justfile construct correct path
                rel_path = p.relative_to(idl_dir)
                subprocess.check_call(["just", "gen-proto", str(rel_path)], cwd=root, stdout=subprocess.DEVNULL)
            except (OSError, subprocess.CalledProcessError):
                print("Warning: Could not auto-generate protos. Ensure 'just' is in PATH.")
                break # Don't spam errors

class GoHandler(Handler):
    def build(self, path): 
        ensure_protos(find_repo_root(path), "go")
        check_tool("go", "brew install go")
        run_cmd(["go", "build", "."], cwd=path)
    def test(self, path): 
        ensure_protos(find_repo_root(path), "go")
        check_tool("go", "brew install go")
        run_cmd(["go", "test", "./..."], cwd=path)
    def run(self, path): 
        ensure_protos(find_repo_root(path), "go")
        check_tool("go", "brew install go")
        run_cmd(["go", "run", "."], cwd=path)

class PythonHandler(Handler):
    def run(self, path):
        root = find_repo_root(path)
        ensure_protos(root, "python")
        
        # We prefer 'uv run' if available, as it handles venvs/dependencies automatically.
        # Otherwise fallback to 'python3'.
        use_uv = False
        import shutil
        if shutil.which("uv"):
            use_uv = True
        else:
             check_tool("python3", "brew install python3")
        
        # Setup PYTHONPATH context
        env = os.environ.copy()
        python_libs = root / "libs" / "python"
        python_gen = root / "gen" / "python"
        
        # Force UV to use our root .venv if it exists, BUT ONLY if the project
        # doesn't have its own configuration (pyproject.toml).
        has_project_config = (path / "pyproject.toml").exists()
        
        if not has_project_config:
            venv_path = root / ".venv"
            if venv_path.exists():
                env["VIRTUAL_ENV"] = str(venv_path)
                # Add venv/bin to PATH to ensure we use correct python executable if invoked directly
                env["PATH"] = str(venv_path / "bin") + os.pathsep + env.get("PATH", "")
        
        # PYTHONPATH is still needed even with uv to find our monorepo libs/gen

        extra_paths = []
        if python_libs.exists(): extra_paths.append(str(python_libs))
        if python_gen.exists(): extra_paths.append(str(python_gen))
        current_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = os.pathsep.join(extra_paths + [current_path]) if current_path else os.pathsep.join(extra_paths)

        if use_uv:
            # uv run automatically picks up the .venv in root or creates an ephemeral one
            cmd_prefix = ["uv", "run"]
        else:
            cmd_prefix = [sys.executable]

        if path.is_file():
             # Run script
             subprocess.check_call(cmd_prefix + [str(path.name)], cwd=path.parent, env=env)
        elif (path / "main.py").exists():
             # Run project main.py
             subprocess.check_call(cmd_prefix + ["main.py"], cwd=path, env=env)
        else:
            print("No main.py found. Point to a specific script file to run it.")
            sys.exit(1)

    def test(self, path):
        root = find_repo_root(path)
        ensure_protos(root, "python")
        
        use_uv = shutil.which("uv") is not None
        if not use_uv:
            check_tool("python3", "brew install python3")
        
        # Setup PYTHONPATH
        env = os.environ.copy()
        python_libs = root / "libs" / "python"
        python_gen = root / "gen" / "python"
        extra_paths = []
        if python_libs.exists(): extra_paths.append(str(python_libs))
        if python_gen.exists(): extra_paths.append(str(python_gen))
        current_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = os.pathsep.join(extra_paths + [current_path]) if current_path else os.pathsep.join(extra_paths)

        if use_uv:
             subprocess.check_call(["uv", "run", "-m", "unittest", "discover"], cwd=path, env=env)
        else:
             subprocess.check_call([sys.executable, "-m", "unittest", "discover"], cwd=path, env=env)

class NodeHandler(Handler):
    def build(self, path): 
        check_tool("npm", "brew install node")
        run_cmd(["npm", "install"], cwd=path)
    def test(self, path): 
        check_tool("npm", "brew install node")
        run_cmd(["npm", "test"], cwd=path)
    def run(self, path): 
        check_tool("npm", "brew install node")
        run_cmd(["npm", "start"], cwd=path)

# --- Registry ---

def detect_handler(path: Path) -> Handler:
    if (path / "CMakeLists.txt").exists(): return CppHandler()
    if (path / "Cargo.toml").exists(): return RustHandler()
    if (path / "go.mod").exists(): return GoHandler()
    if (path / "package.json").exists(): return NodeHandler() # Added Node/TS support
    # Add Haskell: if (path / "stack.yaml").exists(): return HaskellHandler()
    # Add OCaml: if (path / "dune-project").exists(): return OCamlHandler()
    
    if (path / "__init__.py").exists() or list(path.glob("*.py")) or path.suffix == ".py":
        return PythonHandler()
    return None

def main():
    parser = argparse.ArgumentParser(description="Pithos Unified Runner")
    parser.add_argument("command", choices=["build", "test", "run"])
    parser.add_argument("target", help="Target name")
    args = parser.parse_args()

    # Resolve target path
    cwd = Path.cwd()
    target_path = cwd / args.target
    
    # Search order: projects -> examples -> root -> scripts
    # We check projects first to avoid shadowing (e.g., project "tools" vs root "tools/" dir)
    search_paths = [
        cwd / "projects" / args.target,
        cwd / "examples" / args.target,
        cwd / args.target,
        cwd / "scripts" / args.target,
        cwd / "scripts" / (args.target + ".py")
    ]

    found = False
    for p in search_paths:
        if p.exists():
            target_path = p
            found = True
            break
    
    if not found:
        print(f"Error: Target '{args.target}' not found.")
        sys.exit(1)

    handler = detect_handler(target_path)
    if not handler:
        print(f"Unknown project type at {target_path}. No CMake/Cargo/Go/package.json found.")
        sys.exit(1)
    
    print(f"Detected {type(handler).__name__} for {target_path}")
    
    if args.command == "build": handler.build(target_path)
    elif args.command == "test": handler.test(target_path)
    elif args.command == "run": handler.run(target_path)

if __name__ == "__main__":
    main()
