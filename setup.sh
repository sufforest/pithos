#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Pithos Setup...${NC}"

# 1. Check Homebrew
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew detected."
fi

# 2. Install Mise (Tool Version Manager)
# This prevents polluting your global system with specific versions.
if ! command -v mise &> /dev/null; then
    echo -e "${GREEN}Installing Mise (for isolated tool management)...${NC}"
    # Install via Homebrew or curl
    brew install mise || curl https://mise.run | sh
    eval "$(mise activate bash)"
    # OPTIONAL: Prefer precompiled binaries for speed (avoids compiling Python from source)
    mise settings set python.compile false
fi

# 3. Install System Libraries (Libs needed for C++ linking)
# Mise is great for runtimes (Go, Node), but strict C++ libraries
# are best managed by Homebrew so CMake can find them easily.
echo -e "${GREEN}Installing system libraries...${NC}"
brew list protobuf &>/dev/null || brew install protobuf

# 4. Install Tools via Mise (Local to this repo/user)
echo -e "${GREEN}Installing isolated tools version via Mise...${NC}"
# This reads .tool-versions and installs tools into ~/.local/share/mise/installs
# It does NOT touch /usr/local or /opt/homebrew (except for mise itself)
mise install

# 4. Setup Go Workspace
echo -e "${GREEN}Setting up Go Workspace...${NC}"
if [ ! -f go.work ]; then
    go work init
    go work use .
    echo "Initialized go.work"
fi

# 5. Install Go Protobuf Plugins
echo -e "${GREEN}Installing Go Protobuf plugins...${NC}"
mise exec -- go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
mise exec -- go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# 6. Setup Python (using uv)
echo -e "${GREEN}Setting up Python...${NC}"
# uv is installed via mise (from .tool-versions)
# Create venv fast
mise exec -- uv venv .venv --allow-existing
source .venv/bin/activate
if [ -f requirements.txt ]; then
    echo "Installing dependencies with uv..."
    uv pip install -r requirements.txt
fi

# 7. Generate Autocompletion Script
echo -e "${GREEN}Generating autocompletion script...${NC}"
mkdir -p tools
mise exec -- just --completions zsh | sed '$d' > tools/just.zsh

echo -e "${GREEN}Setup Complete!${NC}"
echo "1. Run 'source activate.zsh' to enter the isolated environment."
echo "2. Run 'just' to start."
