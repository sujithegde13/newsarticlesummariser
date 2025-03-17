from flask import Flask, render_template, request, jsonify
import logging
import os
import urllib.request
import json
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "news-analyzer-secret-key")

# List of popular companies for the dropdown
POPULAR_COMPANIES = [
    "Apple", "Google", "Microsoft", "Amazon", "Tesla", 
    "Meta", "Netflix", "Nvidia", "Intel", "IBM", 
    "Reliance Industries", "TCS", "Infosys", "HDFC Bank", "Adani"
]

# Mock data for demonstration
MOCK_DATA = {
    "apple": {
        "Company": "Apple",
        "Articles": [
            {
                "title": "Apple Reports Record Profits",
                "url": "https://example.com/apple-profits",
                "summary": "Apple announced record quarterly profits, exceeding market expectations.",
                "sentiment": {"label": "POSITIVE", "score": 0.92},
                "topics": ["Profits", "Earnings", "Stock Market"]
            },
            {
                "title": "Apple Faces Supply Chain Challenges",
                "url": "https://example.com/apple-supply",
                "summary": "Apple is experiencing supply chain disruptions affecting product availability.",
                "sentiment": {"label": "NEGATIVE", "score": 0.78},
                "topics": ["Supply Chain", "Manufacturing", "Logistics"]
            },
            {
                "title": "New iPhone Features Leaked",
                "url": "https://example.com/iphone-leak",
                "summary": "Details about upcoming iPhone features have been leaked online.",
                "sentiment": {"label": "NEUTRAL", "score": 0.65},
                "topics": ["iPhone", "Product Launch", "Technology"]
            }
        ],
        "Comparative_Sentiment_Score": {
            "Average_Score": 0.66,
            "Sentiment_Distribution": {
                "POSITIVE": 1,
                "NEUTRAL": 1,
                "NEGATIVE": 1
            }
        },
        "Final_Sentiment_Analysis": "Mixed sentiment with balanced positive, neutral, and negative coverage.",
        "Hindi_Text": "एप्पल को मिश्रित समाचार प्राप्त हुए, रिकॉर्ड लाभ की सूचना के साथ-साथ आपूर्ति श्रृंखला की चुनौतियों का सामना करना पड़ रहा है।",
        "Audio": ""
    }
}

@app.route('/')
def index():
    """Render the main page of the application"""
    return render_template('index.html', companies=POPULAR_COMPANIES)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Process the analysis request and return results"""
    company_name = request.form.get('company_name', '')
    
    if not company_name:
        return jsonify({'error': 'Please enter a company name'})
    
    try:
        # Use mock data for demonstration
        company_key = company_name.lower().replace(" ", "_")
        
        # For demo purposes, return Apple data for any company
        data = MOCK_DATA.get("apple", {})
        
        # Replace company name in the data
        if data:
            data["Company"] = company_name
        
        return jsonify({
            'status': 'completed',
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Error in analyze request: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)})

@app.route('/task-status/<task_id>')
def task_status(task_id):
    """Check the status of an analysis task (mock implementation)"""
    return jsonify({
        'status': 'completed',
        'task_id': task_id,
        'completed': True,
        'data': MOCK_DATA.get("apple", {})
    })

@app.route('/available-companies')
def available_companies():
    """Get list of companies that have been analyzed and cached"""
    return jsonify({'companies': POPULAR_COMPANIES})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)