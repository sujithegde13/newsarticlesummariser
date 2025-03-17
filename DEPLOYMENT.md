# Deployment Guide for News Analysis Application

## GitHub Deployment

### Prerequisites
- Python 3.8 or higher
- Git

### Required Dependencies
These dependencies need to be installed in your environment:
```
flask>=2.0.0
gunicorn>=20.1.0
email-validator
flask-sqlalchemy
psycopg2-binary
trafilatura
```

### Steps for GitHub Deployment

1. **Create a GitHub Repository**
   - Log in to your GitHub account
   - Click the "+" icon in the top right and select "New repository"
   - Name your repository (e.g., "news-analysis-app")
   - Select appropriate visibility settings
   - Click "Create repository"

2. **Initialize Git in Your Project Directory**
   ```
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Connect to GitHub Repository**
   ```
   git remote add origin https://github.com/yourusername/news-analysis-app.git
   git branch -M main
   git push -u origin main
   ```

4. **Setup GitHub Pages (Optional)**
   - Go to repository settings
   - Scroll down to "GitHub Pages"
   - Select the branch to deploy from (usually "main")
   - Click "Save"

## Hugging Face Spaces Deployment
As mentioned in the assignment requirements, you can also deploy to Hugging Face Spaces:

1. **Sign up/Log in to Hugging Face**
   - Visit https://huggingface.co/

2. **Create a new Space**
   - Navigate to https://huggingface.co/spaces
   - Click on "Create a new Space"
   - Choose "Flask" as your SDK
   - Name your space (e.g., "news-analysis-app")
   - Set up the repository visibility

3. **Push Your Code to Hugging Face**
   - Follow the git commands provided in the Hugging Face UI
   - Make sure to include a requirements.txt file with the dependencies listed above

4. **Update the README**
   - Update the README to include information about how to use the application

## Local Deployment
For testing purposes, you can run the application locally:

1. **Install dependencies**
   ```
   pip install flask gunicorn email-validator flask-sqlalchemy psycopg2-binary trafilatura
   ```

2. **Run the application**
   ```
   python main.py
   ```
   or
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

3. **Access the application**
   - Open a browser and navigate to http://localhost:5000

## Documentation Links
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Hugging Face Spaces Documentation](https://huggingface.co/docs/hub/spaces-overview)