#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: worktree_bootstrap.sh [--target PATH] [--main PATH] [--no-reuse]

Bootstrap a linked Git worktree by optionally symlinking common local-only
environment assets from the main worktree.

Options:
  --target PATH   Worktree to bootstrap. Defaults to current directory.
  --main PATH     Main worktree to reuse from. Auto-detected by default.
  --no-reuse      Do not create symlinks; only report detected paths.
  -h, --help      Show this help.
EOF
}

target_path="$(pwd)"
main_worktree=""
reuse=1

while [ "$#" -gt 0 ]; do
    case "$1" in
        --target)
            target_path="${2:?missing value for --target}"
            shift 2
            ;;
        --main)
            main_worktree="${2:?missing value for --main}"
            shift 2
            ;;
        --no-reuse)
            reuse=0
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: this script must run inside a Git worktree." >&2
    exit 1
fi

target_path="$(cd "$target_path" && pwd -P)"

if [ -n "$main_worktree" ]; then
    main_worktree="$(cd "$main_worktree" && pwd -P)"
else
    common_git_dir="$(cd "$(git rev-parse --git-common-dir)" && pwd -P)"
    while IFS= read -r line; do
        case "$line" in
            worktree\ *)
                candidate="${line#worktree }"
                if [ -d "$candidate/.git" ] && [ "$(cd "$candidate/.git" && pwd -P)" = "$common_git_dir" ]; then
                    main_worktree="$candidate"
                    break
                fi
                ;;
        esac
    done < <(git worktree list --porcelain)
fi

if [ -z "$main_worktree" ]; then
    echo "Error: could not locate the main worktree for this repository." >&2
    exit 1
fi

echo "Main worktree: $main_worktree"
echo "Target worktree: $target_path"

if [ "$reuse" -eq 0 ]; then
    echo "Environment reuse disabled by --no-reuse."
    exit 0
fi

if [ "$target_path" = "$main_worktree" ]; then
    echo "Already in the main worktree; nothing to link."
    exit 0
fi

link_path() {
    local relative_path="$1"
    local source_path="$main_worktree/$relative_path"
    local target_link="$target_path/$relative_path"

    if [ ! -e "$source_path" ]; then
        echo "skip $relative_path: source does not exist"
        return 0
    fi

    if [ -L "$target_link" ]; then
        rm "$target_link"
    elif [ -e "$target_link" ]; then
        echo "skip $relative_path: target exists and is not a symlink"
        return 0
    fi

    mkdir -p "$(dirname "$target_link")"
    ln -s "$source_path" "$target_link"
    echo "linked $relative_path"
}

default_paths=(
    ".env"
    ".env.local"
    ".env.development"
    ".env.development.local"
    ".venv"
    "venv"
    "node_modules"
    "web/.env"
    "web/.env.local"
    "web/node_modules"
    "frontend/.env"
    "frontend/.env.local"
    "frontend/node_modules"
    "app/.env"
    "app/.env.local"
    "app/node_modules"
    "vendor/bundle"
    "vendor"
    ".gradle"
)

for relative_path in "${default_paths[@]}"; do
    link_path "$relative_path"
done
