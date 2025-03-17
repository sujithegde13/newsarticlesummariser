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

# Mock data for different companies
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
    },
    "tesla": {
        "Company": "Tesla",
        "Articles": [
            {
                "title": "Tesla's New Model Breaks Sales Records",
                "url": "https://example.com/tesla-sales",
                "summary": "Tesla's latest electric vehicle model has broken all previous sales records in the first quarter.",
                "sentiment": {"label": "POSITIVE", "score": 0.95},
                "topics": ["Sales", "Electric Vehicles", "Growth"]
            },
            {
                "title": "Tesla Self-Driving Technology Under Regulatory Scrutiny",
                "url": "https://example.com/tesla-regulation",
                "summary": "Regulators have raised concerns about the safety of Tesla's self-driving technology.",
                "sentiment": {"label": "NEGATIVE", "score": 0.82},
                "topics": ["Regulation", "Self-Driving", "Safety"]
            },
            {
                "title": "Elon Musk Announces New Tesla Factory",
                "url": "https://example.com/tesla-factory",
                "summary": "Tesla CEO Elon Musk announced plans for a new gigafactory to increase production capacity.",
                "sentiment": {"label": "POSITIVE", "score": 0.88},
                "topics": ["Manufacturing", "Expansion", "Elon Musk"]
            },
            {
                "title": "Tesla Reaches New Production Milestone",
                "url": "https://example.com/tesla-production",
                "summary": "Tesla has achieved a new production milestone, manufacturing 10,000 vehicles in a single week.",
                "sentiment": {"label": "POSITIVE", "score": 0.91},
                "topics": ["Production", "Manufacturing", "Milestone"]
            },
            {
                "title": "Tesla Stock Surges After Earnings Report",
                "url": "https://example.com/tesla-stock",
                "summary": "Tesla's stock price jumped 15% after the company reported better-than-expected quarterly earnings.",
                "sentiment": {"label": "POSITIVE", "score": 0.93},
                "topics": ["Stock", "Earnings", "Investors"]
            },
            {
                "title": "New Battery Technology Announced by Tesla",
                "url": "https://example.com/tesla-battery",
                "summary": "Tesla unveiled a new battery technology that increases range by 30% and reduces production costs.",
                "sentiment": {"label": "POSITIVE", "score": 0.89},
                "topics": ["Battery", "Technology", "Innovation"]
            },
            {
                "title": "Tesla Faces Production Delays on New Model",
                "url": "https://example.com/tesla-delays",
                "summary": "Supply chain issues have caused production delays for Tesla's upcoming vehicle model.",
                "sentiment": {"label": "NEGATIVE", "score": 0.77},
                "topics": ["Delays", "Production", "Supply Chain"]
            },
            {
                "title": "Tesla Expands Supercharger Network Globally",
                "url": "https://example.com/tesla-superchargers",
                "summary": "Tesla has announced plans to double its global Supercharger network over the next two years.",
                "sentiment": {"label": "POSITIVE", "score": 0.85},
                "topics": ["Supercharger", "Infrastructure", "Expansion"]
            },
            {
                "title": "Competition Intensifies in EV Market as Tesla Maintains Lead",
                "url": "https://example.com/tesla-competition",
                "summary": "Despite increasing competition from traditional automakers, Tesla maintains its lead in the EV market.",
                "sentiment": {"label": "NEUTRAL", "score": 0.60},
                "topics": ["Competition", "Market Share", "Industry"]
            },
            {
                "title": "Tesla's Solar Roof Installations Growing Rapidly",
                "url": "https://example.com/tesla-solar",
                "summary": "Tesla's solar roof installations have increased by 70% year-over-year as demand for renewable energy grows.",
                "sentiment": {"label": "POSITIVE", "score": 0.87},
                "topics": ["Solar", "Renewable Energy", "Growth"]
            },
            {
                "title": "Tesla Autopilot Receives Software Update",
                "url": "https://example.com/tesla-autopilot",
                "summary": "Tesla has rolled out a significant software update to its Autopilot system, adding new safety features.",
                "sentiment": {"label": "POSITIVE", "score": 0.84},
                "topics": ["Autopilot", "Software", "Safety"]
            },
            {
                "title": "Tesla Opens New Showroom in India",
                "url": "https://example.com/tesla-india",
                "summary": "Tesla has opened its first showroom in India, signaling entry into the world's second-most populous market.",
                "sentiment": {"label": "POSITIVE", "score": 0.86},
                "topics": ["Expansion", "International", "India"]
            },
            {
                "title": "Lawsuit Filed Against Tesla Over Workplace Conditions",
                "url": "https://example.com/tesla-lawsuit",
                "summary": "Former employees have filed a lawsuit against Tesla alleging poor workplace conditions and discrimination.",
                "sentiment": {"label": "NEGATIVE", "score": 0.84},
                "topics": ["Lawsuit", "Workplace", "Legal"]
            },
            {
                "title": "Tesla Cybertruck Production Ramps Up",
                "url": "https://example.com/tesla-cybertruck",
                "summary": "Tesla has increased production of its Cybertruck to meet high demand following its launch.",
                "sentiment": {"label": "POSITIVE", "score": 0.90},
                "topics": ["Cybertruck", "Production", "Demand"]
            },
            {
                "title": "Environmental Impact of Tesla Factories Under Scrutiny",
                "url": "https://example.com/tesla-environment",
                "summary": "Environmental groups are questioning the ecological impact of Tesla's manufacturing facilities.",
                "sentiment": {"label": "NEGATIVE", "score": 0.69},
                "topics": ["Environment", "Manufacturing", "Sustainability"]
            },
            {
                "title": "Tesla Partners with Major Mining Company for Battery Materials",
                "url": "https://example.com/tesla-mining",
                "summary": "Tesla has formed a partnership with a major mining company to secure sustainable battery materials.",
                "sentiment": {"label": "POSITIVE", "score": 0.82},
                "topics": ["Mining", "Partnership", "Supply Chain"]
            },
            {
                "title": "Tesla Unveils New AI Chip for Self-Driving",
                "url": "https://example.com/tesla-ai",
                "summary": "Tesla has developed a new AI chip that significantly improves processing power for its self-driving systems.",
                "sentiment": {"label": "POSITIVE", "score": 0.92},
                "topics": ["AI", "Hardware", "Self-Driving"]
            },
            {
                "title": "Tesla's Market Share in China Decreases",
                "url": "https://example.com/tesla-china",
                "summary": "Tesla's market share in China has decreased as local competitors introduce new electric vehicle models.",
                "sentiment": {"label": "NEGATIVE", "score": 0.73},
                "topics": ["China", "Market Share", "Competition"]
            },
            {
                "title": "Tesla Energy Division Reports Record Growth",
                "url": "https://example.com/tesla-energy",
                "summary": "Tesla's energy division, which includes Powerwall and utility-scale batteries, has reported record growth.",
                "sentiment": {"label": "POSITIVE", "score": 0.89},
                "topics": ["Energy", "Growth", "Powerwall"]
            },
            {
                "title": "Tesla Recalls 50,000 Vehicles Over Safety Concern",
                "url": "https://example.com/tesla-recall",
                "summary": "Tesla has issued a recall for 50,000 vehicles due to a potential safety issue with the braking system.",
                "sentiment": {"label": "NEGATIVE", "score": 0.80},
                "topics": ["Recall", "Safety", "Quality Control"]
            }
        ],
        "Comparative_Sentiment_Score": {
            "Average_Score": 0.83,
            "Sentiment_Distribution": {
                "POSITIVE": 13,
                "NEUTRAL": 1,
                "NEGATIVE": 6
            }
        },
        "Final_Sentiment_Analysis": "Overall strongly positive sentiment (65% positive) with strong financial and production performance, balanced by some regulatory and environmental concerns.",
        "Hindi_Text": "टेस्ला का समग्र प्रदर्शन सकारात्मक रहा है, जिसमें रिकॉर्ड तोड़ बिक्री, उत्पादन में वृद्धि और शेयर मूल्य में उछाल शामिल है। नई बैटरी तकनीक और AI चिप के विकास से इनोवेशन में प्रगति दिखाई दे रही है। हालांकि, नियामकों की ओर से सेल्फ-ड्राइविंग टेक्नोलॉजी पर चिंताएं, उत्पादन में देरी और चीन में बाजार हिस्सेदारी में कमी जैसी चुनौतियां भी हैं। कंपनी की भारत में प्रवेश और सुपरचार्जर नेटवर्क का विस्तार इसके वैश्विक विकास का संकेत देता है।",
        "Audio": ""
    },
    "google": {
        "Company": "Google",
        "Articles": [
            {
                "title": "Google Unveils New AI Features for Search",
                "url": "https://example.com/google-ai",
                "summary": "Google has announced new AI-powered features for its search engine at the annual developer conference.",
                "sentiment": {"label": "POSITIVE", "score": 0.90},
                "topics": ["AI", "Search Engine", "Technology"]
            },
            {
                "title": "Google Faces Antitrust Lawsuit",
                "url": "https://example.com/google-antitrust",
                "summary": "Regulators have filed an antitrust lawsuit against Google over alleged monopolistic practices.",
                "sentiment": {"label": "NEGATIVE", "score": 0.85},
                "topics": ["Antitrust", "Legal", "Regulation"]
            },
            {
                "title": "Google's Cloud Business Shows Strong Growth",
                "url": "https://example.com/google-cloud",
                "summary": "Google Cloud division reported better-than-expected revenue growth in the latest quarterly results.",
                "sentiment": {"label": "POSITIVE", "score": 0.87},
                "topics": ["Cloud Computing", "Revenue", "Growth"]
            }
        ],
        "Comparative_Sentiment_Score": {
            "Average_Score": 0.64,
            "Sentiment_Distribution": {
                "POSITIVE": 2,
                "NEUTRAL": 0,
                "NEGATIVE": 1
            }
        },
        "Final_Sentiment_Analysis": "Mostly positive coverage focusing on innovation and growth, with some regulatory challenges.",
        "Hindi_Text": "गूगल ने सर्च इंजन के लिए नई एआई सुविधाएं पेश कीं। कंपनी एंटीट्रस्ट मुकदमे का सामना कर रही है। गूगल क्लाउड व्यवसाय में मजबूत वृद्धि दिखाई दे रही है।",
        "Audio": ""
    },
    "microsoft": {
        "Company": "Microsoft",
        "Articles": [
            {
                "title": "Microsoft's Azure Cloud Revenue Surges",
                "url": "https://example.com/microsoft-azure",
                "summary": "Microsoft reported strong growth in its Azure cloud services, exceeding analyst expectations.",
                "sentiment": {"label": "POSITIVE", "score": 0.91},
                "topics": ["Azure", "Cloud Computing", "Revenue"]
            },
            {
                "title": "Microsoft Acquires AI Startup",
                "url": "https://example.com/microsoft-acquisition",
                "summary": "Microsoft has announced the acquisition of an AI startup to enhance its artificial intelligence capabilities.",
                "sentiment": {"label": "POSITIVE", "score": 0.88},
                "topics": ["Acquisition", "AI", "Business Strategy"]
            },
            {
                "title": "Windows Security Vulnerability Discovered",
                "url": "https://example.com/windows-security",
                "summary": "Security researchers have identified a critical vulnerability in Windows operating system.",
                "sentiment": {"label": "NEGATIVE", "score": 0.79},
                "topics": ["Security", "Windows", "Vulnerability"]
            }
        ],
        "Comparative_Sentiment_Score": {
            "Average_Score": 0.69,
            "Sentiment_Distribution": {
                "POSITIVE": 2,
                "NEUTRAL": 0,
                "NEGATIVE": 1
            }
        },
        "Final_Sentiment_Analysis": "Predominantly positive coverage with strong financial performance and strategic acquisitions, tempered by some security concerns.",
        "Hindi_Text": "माइक्रोसॉफ्ट के एज़ूर क्लाउड राजस्व में वृद्धि हुई है। कंपनी ने एक एआई स्टार्टअप का अधिग्रहण किया है। विंडोज में एक महत्वपूर्ण सुरक्षा कमजोरी की पहचान की गई है।",
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
        # Convert the company name to a key format
        company_key = company_name.lower().split()[0]  # Use first word of company name as key
        
        # Find the corresponding data or use a fallback
        data = None
        
        # Try exact match first
        if company_key in MOCK_DATA:
            data = MOCK_DATA[company_key]
        else:
            # For companies not in our mock data, find closest match
            # For example, 'Tata Motors' would fall back to 'tesla' as both start with T
            for key in MOCK_DATA:
                if key[0] == company_key[0]:  # Simple matching by first letter
                    data = MOCK_DATA[key].copy()  # Copy to avoid modifying original
                    data["Company"] = company_name  # Update company name
                    break
            
            # If still no match, default to apple
            if not data:
                data = MOCK_DATA["apple"].copy()
                data["Company"] = company_name
        
        # Create a task ID for the front end to track
        task_id = f"task_{company_key}_{hash(company_name) % 10000}"
        
        return jsonify({
            'status': 'completed',
            'task_id': task_id,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Error in analyze request: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)})

@app.route('/task-status/<task_id>')
def task_status(task_id):
    """Check the status of an analysis task (mock implementation)"""
    # Extract company from task_id (format: task_company_hash)
    parts = task_id.split('_')
    company_key = "apple"  # Default fallback
    
    if len(parts) > 1:
        # Get the company part from the task_id
        company_key = parts[1]
    
    # Get appropriate company data
    data = MOCK_DATA.get(company_key, MOCK_DATA["apple"]).copy()
    
    return jsonify({
        'status': 'completed',
        'task_id': task_id,
        'completed': True,
        'data': data
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