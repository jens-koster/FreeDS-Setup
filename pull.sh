#!/bin/bash

# filepath: /Users/jens/src/FreeDS-Setup/pull.sh

# Base directory containing all repositories
BASE_DIR="/Users/jens/src"

# List of repositories to pull
REPOSITORIES=(
  "FreeDS"
  "myfreeds/the-free-data-stack"
  "myfreeds/freeds-config"
  "myfreeds/freeds-lab-jaffle-kafe"
  "jaffle-shop-generator"
  "FreeDS-Setup"
)

# Iterate through each repository and perform git pull
for REPO in "${REPOSITORIES[@]}"; do
  REPO_PATH="$BASE_DIR/$REPO"
  if [ -d "$REPO_PATH/.git" ]; then
    echo "Pulling latest changes in $REPO_PATH..."
    git -C "$REPO_PATH" pull
  else
    echo "Skipping $REPO_PATH: Not a git repository."
  fi
done

echo "Git pull completed for all repositories."