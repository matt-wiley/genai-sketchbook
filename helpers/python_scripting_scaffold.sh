#!/bin/bash

# Define project name
PROJECT_NAME=$1

# Check if project name is provided
if [ -z "$PROJECT_NAME" ]; then
  echo "Usage: $0 <project_name>"
  exit 1
fi

# Create project directory
mkdir -p $PROJECT_NAME

# Navigate into project directory
cd $PROJECT_NAME

# Create main.py
cat <<EOL > main.py
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
EOL

# Create README.md
cat <<EOL > README.md
# $PROJECT_NAME

## Description
A Python scripting project.

## Usage
\`\`\`bash
python main.py
\`\`\`
EOL

# Create requirements.txt
touch requirements.txt

# Create tests directory and __init__.py
mkdir -p tests
touch tests/__init__.py

echo "Python project '$PROJECT_NAME' scaffolded successfully."