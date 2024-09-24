#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Initialize a new Git repository
echo "Initializing a new Git repository..."
git init gitlab-flow-demo
cd gitlab-flow-demo

# Create an empty initial commit on the main branch
echo "Creating an initial commit on the main branch..."
git commit --allow-empty -m "chore: initial commit on main branch"

# Create a 'production' branch from 'main'
echo "Creating the 'production' branch from 'main'..."
git checkout -b production
git commit --allow-empty -m "chore: initialize production branch"

# Switch back to 'main'
git checkout main

# Create a feature branch (feature/login)
echo "Creating a feature branch 'feature/login'..."
git checkout -b feature/login
git commit --allow-empty -m "feat: start working on login feature"
git commit --allow-empty -m "feat: add login form"
git commit --allow-empty -m "feat: add login functionality"

# Squash commits and rebase 'feature/login' onto 'main'
echo "Squashing and rebasing 'feature/login' onto 'main'..."
git checkout main
git merge --squash feature/login
git commit -m "merge: integrate login feature"

# Create another feature branch (feature/payment)
echo "Creating another feature branch 'feature/payment'..."
git checkout -b feature/payment
git commit --allow-empty -m "feat: start working on payment feature"
git commit --allow-empty -m "feat: add payment gateway integration"
git commit --allow-empty -m "feat: finalize payment processing"

# Squash commits and rebase 'feature/payment' onto 'main'
echo "Squashing and rebasing 'feature/payment' onto 'main'..."
git checkout main
git merge --squash feature/payment
git commit -m "merge: integrate payment feature"

# Simulate a release by rebasing 'main' onto 'production'
echo "Simulating a release by rebasing 'main' onto 'production'..."
git checkout production
git merge --squash main
git commit -m "release: deploy latest features to production"

# Create a hotfix branch (hotfix/payment-fix) from 'production'
echo "Creating a hotfix branch 'hotfix/payment-fix' from 'production'..."
git checkout -b hotfix/payment-fix
git commit --allow-empty -m "fix: resolve payment processing bug"

# Squash and rebase the hotfix into 'production'
echo "Squashing and rebasing 'hotfix/payment-fix' into 'production'..."
git checkout production
git merge --squash hotfix/payment-fix
git commit -m "merge: hotfix for payment processing issue"

# Squash and rebase the hotfix back into 'main' to keep branches in sync
echo "Squashing and rebasing 'hotfix/payment-fix' back into 'main'..."
git checkout main
git merge --squash hotfix/payment-fix
git commit -m "merge: integrate payment hotfix into main"

# Display the final git log for demonstration purposes
echo "GitLab Flow with squash and rebase demonstration setup complete."
echo "Here's the final git log:"
git log --oneline --graph --all --decorate
