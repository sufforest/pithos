#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from multiprocessing import Pool

# Colors
GREEN = '\033[0;32m'
NC = '\033[0m'

def run_cmake_configure(project_path_str):
    """Run CMake configure for a single project/lib to generate compile_commands.json."""
    project_path = Path(project_path_str)
    build_dir = project_path / "build"
    
    # We want to be quiet generally, unless error
    cmd = [
        "cmake", 
        "-S", ".", 
        "-B", "build", 
        "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
    ]
    
    # macOS sysroot fix
    if sys.platform == "darwin":
        try:
             # Fast check, assume xcode-select is set up
             # We could cache this but multiprocessing makes it tricky without manager
            sdk = subprocess.check_output(["xcrun", "--show-sdk-path"]).decode().strip()
            cmd.append(f"-DCMAKE_OSX_SYSROOT={sdk}")
        except:
            pass

    try:
        # Capture output to avoid spamming the console
        subprocess.check_output(cmd, cwd=project_path, stderr=subprocess.STDOUT)
        
        json_path = build_dir / "compile_commands.json"
        if json_path.exists():
            return json_path
    except subprocess.CalledProcessError as e:
        print(f"Failed to configure {project_path.name}:\n{e.output.decode()}")
    return None

def main():
    parser = argparse.ArgumentParser(description="Generate global compile_commands.json for Pithos")
    args = parser.parse_args()

    root = Path.cwd()
    print(f"{GREEN}Scanning for C++ projects...{NC}")

    # Find all CMakeLists.txt files
    # We look in projects/, libs/cpp/, and examples/cpp/
    candidates = []
    
    # Helper to scan dir
    def scan(d):
        if not d.exists(): return
        for p in d.rglob("CMakeLists.txt"):
            # Exclude build directories or generated code
            if "build" in p.parts or "gen" in p.parts:
                continue
            candidates.append(p.parent)

    scan(root / "projects")
    scan(root / "libs" / "cpp")
    scan(root / "examples" / "cpp")
    
    # Deduplicate
    candidates = sorted(list(set(candidates)))
    print(f"Found {len(candidates)} C++ projects.")

    # Run CMake in parallel
    print(f"{GREEN}Configuring projects in parallel...{NC}")
    compilation_db_files = []
    
    with Pool() as pool:
        # Using map for simplicity. 
        # map returns results in order, but we filter None afterwards.
        # We pass string paths because Path objects pickles fine but let's be safe/simple
        results = pool.map(run_cmake_configure, [str(p) for p in candidates])
        
        for res in results:
            if res:
                compilation_db_files.append(Path(res))

    print(f"{GREEN}Merging {len(compilation_db_files)} compilation databases...{NC}")
    
    global_db = []
    for db_path in compilation_db_files:
        try:
            with open(db_path, 'r') as f:
                data = json.load(f)
                # Important: Entries in compile_commands.json usually have "directory" field.
                # Since we run from subdirs, we should double check if paths are absolute.
                # CMake usually generates absolute paths in "directory" and "file".
                global_db.extend(data)
        except Exception as e:
            print(f"Error reading {db_path}: {e}")

    # Write to root
    output_path = root / "compile_commands.json"
    with open(output_path, 'w') as f:
        json.dump(global_db, f, indent=2)

    print(f"{GREEN}Success! Global compilation database written to:{NC} {output_path}")

if __name__ == "__main__":
    main()
