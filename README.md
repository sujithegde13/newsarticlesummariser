# News Analyzer with Sentiment Analysis and Hindi TTS

This application extracts news articles related to a given company, performs sentiment analysis, conducts a comparative analysis, and generates a text-to-speech (TTS) output in Hindi. The tool allows users to input a company name and receive a structured sentiment report along with an audio output.

## Features

- **News Extraction**: Extracts titles, summaries, and metadata from multiple news articles related to the given company
- **Sentiment Analysis**: Performs sentiment analysis on article content (positive, negative, neutral)
- **Comparative Analysis**: Conducts comparative sentiment analysis across articles to derive insights
- **Keyword Extraction**: Identifies key topics from each article
- **Text-to-Speech**: Converts summarized content into Hindi speech
- **Responsive UI**: Interactive web interface with visual reports and audio playback

## Project Structure

```
news-analyzer/
├── api.py              # FastAPI backend with API endpoints
├── app.py              # Gradio UI implementation (alternative interface)
├── main.py             # Flask web application entry point
├── utils.py            # Core functionality and ML models
├── requirements.txt    # Project dependencies
├── templates/          # Flask HTML templates
│   └── index.html      # Main UI template
├── static/             # Static assets
│   ├── css/            # CSS stylesheets
│   │   └── styles.css  # Custom styles
│   └── js/             # JavaScript files
│       └── app.js      # Client-side functionality
└── README.md           # Project documentation
```

## Technology Stack

- **Backend**:
  - Python 3.11
  - FastAPI for API endpoints
  - Flask for web server
  - Gradio for alternative UI (optional)

- **Machine Learning**:
  - Hugging Face Transformers for sentiment analysis and summarization
  - KeyBERT for keyword extraction
  - Coqui TTS for Hindi speech synthesis

- **Frontend**:
  - HTML5, CSS3, JavaScript
  - Bootstrap 5 for responsive design
  - Font Awesome for icons

- **Web Scraping**:
  - Trafilatura for content extraction
  - BeautifulSoup for HTML parsing
  - Feedparser for RSS feed parsing

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/news-analyzer.git
   cd news-analyzer
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables (optional):
   ```bash
   export API_HOST=localhost
   export API_PORT=8000
   ```

### Running the Application

1. Start the API server:
   ```bash
   python api.py
   ```

2. In a separate terminal, start the web server:
   ```bash
   python main.py
   ```

3. Access the application:
   - Web interface: http://localhost:5000
   - API documentation: http://localhost:8000/docs

## API Documentation

The application exposes the following API endpoints:

### POST /analyze-company

Initiates a news analysis task for a specified company.

**Request Body**:
```json
{
  "company_name": "Tesla"
}
```

**Response**:
```json
{
  "status": "processing",
  "task_id": "task_tesla",
  "message": "Analysis started for Tesla",
  "data": null
}
```

### GET /task-status/{task_id}

Checks the status of an analysis task.

**Response**:
```json
{
  "status": "completed",
  "task_id": "task_tesla",
  "completed": true,
  "data": {
    "Company": "Tesla",
    "Articles": [...],
    "Comparative_Sentiment_Score": {...},
    "Final_Sentiment_Analysis": "...",
    "Hindi_Text": "...",
    "Audio": "base64-encoded-audio-data"
  }
}
```

### GET /available-companies

Returns a list of companies that have been analyzed and cached.

**Response**:
```json
{
  "companies": ["Tesla", "Apple", "Google"]
}
```

## Models Used

1. **Sentiment Analysis**: `cardiffnlp/twitter-roberta-base-sentiment`
   - RoBERTa-based model fine-tuned for sentiment classification
   - Classifies text as Positive, Negative, or Neutral

2. **Text Summarization**: `sshleifer/distilbart-cnn-12-6`
   - Distilled BART model trained on CNN articles
   - Generates concise, coherent summaries

3. **Keyword Extraction**: KeyBERT
   - Uses BERT embeddings to extract keywords/topics
   - Identifies most relevant terms in each article

4. **Text-to-Speech**: Coqui TTS (Hindi model)
   - Neural text-to-speech system supporting Hindi
   - Converts translated text to natural-sounding speech

## Troubleshooting

### Common Issues

1. **Models fail to load**: Ensure you have sufficient memory and disk space for the ML models.

2. **News extraction issues**: Some websites may block scraping. The application attempts to extract content from multiple sources to mitigate this.

3. **API connection errors**: Verify that both the FastAPI and Flask servers are running on the correct ports.

4. **TTS generation failures**: Hindi text translation or TTS generation might fail due to text length or format. The application includes error handling to provide graceful fallbacks.

### Debugging

- Check the application logs for detailed error messages
- For API debugging, use the Swagger UI at http://localhost:8000/docs
- Client-side issues can be debugged using browser developer tools

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Hugging Face for providing pre-trained models
- Coqui for the TTS framework
- The open-source community for the various libraries used in this project