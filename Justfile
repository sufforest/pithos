# Justfile for Pithos

default:
    @just --list

# Create a new C++ project in projects/
new-project-cpp name:
    mkdir -p projects/{{name}}
    cp templates/cpp/CMakeLists.txt projects/{{name}}/
    echo '#include <iostream>\n\nint main() {\n    std::cout << "Hello from {{name}}!" << std::endl;\n    return 0;\n}' > projects/{{name}}/main.cpp
    @echo "Created C++ project at projects/{{name}}"

# Create a new C++ library in libs/cpp/
new-lib-cpp name:
    mkdir -p libs/cpp/{{name}}
    echo 'cmake_minimum_required(VERSION 3.14)\nproject({{name}} CXX)\n\nadd_library({{name}} STATIC {{name}}.cpp)\ntarget_include_directories({{name}} PUBLIC .)' > libs/cpp/{{name}}/CMakeLists.txt
    echo '#pragma once\n\nvoid hello_{{name}}();' > libs/cpp/{{name}}/{{name}}.h
    echo '#include "{{name}}.h"\n#include <iostream>\n\nvoid hello_{{name}}() {\n    std::cout << "Hello from lib {{name}}!" << std::endl;\n}' > libs/cpp/{{name}}/{{name}}.cpp
    @echo "Created C++ library at libs/cpp/{{name}}"

# Create a new Python project (Isolated Env) in projects/
new-project-python name:
    mkdir -p projects/{{name}}
    echo 'import sys\n\ndef main():\n    print("Hello from {{name}} (Isolated Ent)")\n\nif __name__ == "__main__":\n    main()' > projects/{{name}}/main.py
    echo '[project]\nname = "{{name}}"\nversion = "0.1.0"\nrequires-python = ">=3.11"\ndependencies = []' > projects/{{name}}/pyproject.toml
    @echo "Created Python project at projects/{{name}} (with pyproject.toml)"

# Create a new Python library in libs/python/
new-lib-python name:
    mkdir -p libs/python/{{name}}
    echo 'def hello():\n    return "Hello from {{name}}"' > libs/python/{{name}}/__init__.py
    @echo "Created Python library at libs/python/{{name}}"

# Create a new Python script in scripts/ (Simple, Shared Env)
new-script name:
    echo '#!/usr/bin/env python3\n\ndef main():\n    print("Hello from {{name}}")\n\nif __name__ == "__main__":\n    main()' > scripts/{{name}}.py
    chmod +x scripts/{{name}}.py
    @echo "Created Python script at scripts/{{name}}.py"

# Create a new Go module in projects/
new-project-go name:
    mkdir -p projects/{{name}}
    cd projects/{{name}} && go mod init {{name}}
    echo 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello from {{name}}")\n}' > projects/{{name}}/main.go
    go work use projects/{{name}}
    @echo "Created Go project at projects/{{name}} and added to go.work"

# Create a new Go library in libs/go/
new-lib-go name:
    mkdir -p libs/go/{{name}}
    cd libs/go/{{name}} && go mod init pithos/libs/go/{{name}}
    echo 'package {{name}}\n\nfunc Hello() string {\n\treturn "Hello from {{name}}"\n}' > libs/go/{{name}}/{{name}}.go
    go work use libs/go/{{name}}
    @echo "Created Go library at libs/go/{{name}} and added to go.work"

# Create a new Go script/tool in scripts/go/
new-script-go name:
    mkdir -p scripts/go/{{name}}
    cd scripts/go/{{name}} && go mod init pithos/scripts/go/{{name}}
    echo 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Running script {{name}}...")\n}' > scripts/go/{{name}}/main.go
    go work use scripts/go/{{name}}
    @echo "Created Go script at scripts/go/{{name}} and added to go.work"

# Create a new Rust project in projects/
new-project-rust name:
    cd projects && cargo new {{name}}
    @echo "Created Rust project at projects/{{name}}"

# Generate Protobuf code
# Usage: just gen-proto <file.proto>
gen-proto file:
    @echo "Generating {{file}}..."
    mkdir -p gen/cpp gen/go gen/python
    # Ensure nested directories exist (e.g., gen/python/test/ for test/nested.proto)
    mkdir -p gen/cpp/$(dirname {{file}})
    mkdir -p gen/python/$(dirname {{file}})
    # Go protoc plugin creates directories based on option go_package, but we need the module root.
    mkdir -p gen/go
    if [ ! -f gen/go/go.mod ]; then \
        cd gen/go && go mod init pithos/gen/go; \
    fi
    protoc -I=idl \
        --cpp_out=gen/cpp \
        --go_out=gen/go --go_opt=module=pithos/gen/go \
        --python_out=gen/python \
        idl/{{file}}
    @echo "Generated code in gen/"

# --- Unified CLI ---
# Usage: just build <project_name>
build target:
    ./tools/pithos_runner.py build {{target}}

# Usage: just run <project_name>
run target:
    ./tools/pithos_runner.py run {{target}}

# Usage: just test <project_name>
test target:
    ./tools/pithos_runner.py test {{target}}

# Clean all generated artifacts
clean:
    rm -rf gen/
    rm -rf projects/*/build
    rm -rf projects/*/dist
    rm -rf projects/*/__pycache__
    rm -rf libs/*/*/__pycache__
    rm -rf .venv
    rm -rf projects/*/.venv
    @echo "Cleaned all build artifacts and environments."


