# Pithos Environment Activator
# Usage: source activate.zsh

# 1. Ensure Mise is available
if ! command -v mise &> /dev/null; then
    # Fallback paths if not in global PATH
    export PATH="$HOME/.local/bin:$PATH"
    if ! command -v mise &> /dev/null; then
        echo "Error: 'mise' not found. Run ./setup.sh first."
        return 1
    fi
fi

# 2. Activate the Isolated Tools (Go, Python, Just, etc.)
eval "$(mise activate zsh)"

# 3. Load Project-Local Autocompletion for Just
# Method: Generate a Zsh-sourceable script (last line stripped), PATCH IT for dynamic args, and load it.
M_TOOLS_DIR="$(cd "$(dirname "$0")"; pwd)/tools"
COMP_FILE="$M_TOOLS_DIR/just.zsh"

# Custom Completion Function for Pithos Targets
_pithos_targets() {
    local -a targets
    local root="$(dirname "$0")"
    
    # 1. Projects (Basename only, e.g. "my-app")
    if [ -d "$root/projects" ]; then
        targets+=( "$root"/projects/*(/N:t) )
    fi

    # 2. Examples (Relative path from examples/, e.g. "python/proto-demo")
    # We want "cpp/proto-demo", "go/starter", etc.
    if [ -d "$root/examples" ]; then
        pushd "$root/examples" > /dev/null
        targets+=( */*(*N:t) ) # This globs layer/project and keeps trailing path? No.
        # zsh globbing is tricky for this inline.
        # Let's use simple glob and strip prefix? No.
        # Safest: Use globs relative to examples dir.
        # */* matches cpp/proto-demo
        targets+=( */*(/N) )
        popd > /dev/null
    fi

    # 3. Scripts (Basename without extension)
    if [ -d "$root/scripts" ]; then
        targets+=( "$root"/scripts/*(.N:t:r) )
    fi
    
    _describe 'pithos targets' targets
}

if [ ! -f "$COMP_FILE" ]; then
    mkdir -p "$M_TOOLS_DIR"
    if command -v just &> /dev/null; then
        echo "Generating just completions..."
        # 1. Generate (stripped)
        just --completions zsh | sed '$d' > "$COMP_FILE"
        
        # 2. Patch to use _pithos_targets for 'run', 'test', 'build'
        python3 -c "
import sys
path = '$COMP_FILE'
with open(path, 'r') as f:
    content = f.read()

# The injection point in default just completion
search = '_message \"\`just --show \$recipe\`\"'
replace = '''case \$recipe in
                    run|build|test|new-project*) _pithos_targets ;;
                    *) _message \"\`just --show \$recipe\`\" ;;
                esac'''

if search in content:
    content = content.replace(search, replace)
    with open(path, 'w') as f:
        f.write(content)
    print('Patched completion script for Pithos.')
else:
    print('Could not patch completion script (structure changed?).')
"
    fi
fi

if [ -f "$COMP_FILE" ]; then
    # 1. Initialize completion system if missing
    autoload -Uz compinit
    if ! type compdef > /dev/null; then
        compinit
    fi

    # 2. Source the function definition
    source "$COMP_FILE"

    # 3. Register it
    compdef _just just
    
    echo "Autocomplete loaded (Project-aware)."
else
    echo "Autocomplete skipped (just not found or generation failed)."
fi

echo "Pithos Environment Active."
