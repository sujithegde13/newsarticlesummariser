"""
Script to prepare the project for GitHub submission.
This will list all the important files that should be included in your GitHub repository.
"""

import os
import json

# Define important file patterns to include
IMPORTANT_FILES = [
    "*.py",           # Python files
    "*.html",         # HTML templates
    "*.css",          # CSS files
    "*.js",           # JavaScript files
    "*.md",           # Markdown documentation
    "*.txt",          # Text files
    "requirements.*", # Requirements files
]

def list_important_files():
    """List all important files to include in GitHub repository."""
    all_files = []
    
    # Walk through directories
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue
                
            # Check if file matches important patterns
            file_path = os.path.join(root, file)
            # Remove leading ./ if present
            if file_path.startswith('./'):
                file_path = file_path[2:]
                
            # Skip this script itself
            if file_path == "prepare_for_github.py":
                continue
                
            # Check for important file extensions
            for pattern in IMPORTANT_FILES:
                if pattern.startswith('*'):
                    # Pattern is for extension
                    ext = pattern[1:]
                    if file.endswith(ext):
                        all_files.append(file_path)
                        break
                else:
                    # Pattern is for specific filename
                    if file == pattern:
                        all_files.append(file_path)
                        break
    
    return sorted(all_files)

def create_dependency_list():
    """Create a list of Python dependencies."""
    try:
        # Try to read from pyproject.toml first
        import toml
        with open('pyproject.toml', 'r') as f:
            data = toml.load(f)
            # Extract dependencies
            dependencies = data.get('project', {}).get('dependencies', [])
            return dependencies
    except Exception:
        # Fallback to listing installed packages
        return [
            "flask>=2.0.0",
            "gunicorn>=20.1.0",
            "email-validator",
            "flask-sqlalchemy",
            "psycopg2-binary",
            "trafilatura"
        ]

def main():
    """Main function to prepare GitHub submission."""
    print("Preparing project for GitHub submission...")
    
    # List important files
    important_files = list_important_files()
    
    # Print files to include
    print("\n=== FILES TO INCLUDE IN GITHUB REPOSITORY ===")
    for file in important_files:
        print(f"- {file}")
    
    # Generate dependency list
    dependencies = create_dependency_list()
    
    # Print dependency info
    print("\n=== DEPENDENCIES TO INCLUDE IN requirements.txt ===")
    for dep in dependencies:
        print(f"- {dep}")
    
    # Project structure for README
    print("\n=== PROJECT STRUCTURE FOR README ===")
    project_structure = {}
    for file in important_files:
        parts = file.split('/')
        current = project_structure
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # This is a file
                current[part] = None
            else:
                # This is a directory
                if part not in current:
                    current[part] = {}
                current = current[part]
    
    def print_structure(structure, indent=0):
        for key, value in sorted(structure.items()):
            print(' ' * indent + ('└── ' if indent > 0 else '') + key)
            if value is not None:  # It's a directory
                print_structure(value, indent + 4)
    
    print_structure(project_structure)
    
    print("\nDon't forget to include a README.md with setup instructions and project documentation!")
    print("Happy coding!")

if __name__ == "__main__":
    main()