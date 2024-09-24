#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Initialize a new Git repository
echo "Initializing a new Git repository..."
git init gitlab-flow-demo
cd gitlab-flow-demo
git branch -M main

# Create an empty initial commit on main branch
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

# Merge the feature branch back into 'main'
echo "Merging 'feature/login' into 'main'..."
git checkout main
git merge --no-ff feature/login -m "merge: integrate login feature"

# Create another feature branch (feature/payment)
echo "Creating another feature branch 'feature/payment'..."
git checkout -b feature/payment
git commit --allow-empty -m "feat: start working on payment feature"
git commit --allow-empty -m "feat: add payment gateway integration"
git commit --allow-empty -m "feat: finalize payment processing"

# Merge the payment feature into 'main'
echo "Merging 'feature/payment' into 'main'..."
git checkout main
git merge --no-ff feature/payment -m "merge: integrate payment feature"

# Simulate a release by merging 'main' into 'production'
echo "Simulating a release by merging 'main' into 'production'..."
git checkout production
git merge --no-ff main -m "release: deploy latest features to production"

# Create a hotfix branch (hotfix/payment-fix) from 'production'
echo "Creating a hotfix branch 'hotfix/payment-fix' from 'production'..."
git checkout -b hotfix/payment-fix
git commit --allow-empty -m "fix: resolve payment processing bug"

# Merge the hotfix into 'production'
echo "Merging 'hotfix/payment-fix' into 'production'..."
git checkout production
git merge --no-ff hotfix/payment-fix -m "merge: hotfix for payment processing issue"

# Merge the hotfix back into 'main' to keep branches in sync
echo "Merging 'hotfix/payment-fix' back into 'main'..."
git checkout main
git merge --no-ff hotfix/payment-fix -m "merge: integrate payment hotfix into main"

# Display the final git log for demonstration purposes
echo "GitLab Flow demonstration setup complete."
echo "Here's the final git log:"
git log --oneline --graph --all --decorate
