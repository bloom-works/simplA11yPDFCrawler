#!/usr/bin/env bash

OUTPUT="llm-context.txt"

{
  echo "===== DIRECTORY MAP ====="
  find . \
    \( -name '.git' -o -name 'env' -o -name 'node_modules' -o -name 'out' -o -name 'crawled_files' -o -name '__pycache__' \) -prune -o \
    ! -name 'llm-context.txt' \
    ! -name 'export-context.sh' \
    -print | sort

  echo
  echo "===== FILE CONTENTS ====="

  find . \
    \( -name '.git' -o -name 'env' -o -name 'node_modules' -o -name 'out' -o -name 'crawled_files' -o -name '__pycache__' \) -prune -o \
    ! -name 'llm-context.txt' \
    ! -name 'export-context.sh' \
    \( \
      -name '*.py' -o \
      -name '*.js' -o \
      -name '*.mjs' -o \
      -name '*.cjs' -o \
      -name '*.json' -o \
      -name '*.md' -o \
      -name '*.txt' -o \
      -name '*.sh' -o \
      -name '*.yml' -o \
      -name '*.yaml' -o \
      -name '*.html' -o \
      -name '*.css' -o \
      -name '*.csv' -o \
      -name '*.xml' -o \
      -name '*.toml' -o \
      -name '*.ini' -o \
      -name '*.cfg' -o \
      -name 'requirements.txt' -o \
      -name 'package.json' -o \
      -name 'package-lock.json' -o \
      -name 'README.md' -o \
      -name 'LICENSE' \
    \) -type f -print | sort | while read -r f; do
      echo
      echo "===== FILE: $f ====="
      cat "$f"
      echo
    done
} > "$OUTPUT"