import os
import gradio as gr
import asyncio
import aiohttp
import json
import base64
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}"

# List of popular companies for the dropdown
POPULAR_COMPANIES = [
    "Apple", "Google", "Microsoft", "Amazon", "Tesla", 
    "Meta", "Netflix", "Nvidia", "Intel", "IBM", 
    "Reliance Industries", "TCS", "Infosys", "HDFC Bank", "Adani"
]

async def get_cached_companies():
    """Get list of companies already analyzed and available in cache"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/available-companies") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("companies", [])
                else:
                    logger.error(f"Failed to fetch cached companies: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Error fetching cached companies: {e}")
        return []

async def analyze_company(company_name, progress=gr.Progress()):
    """
    Analyze news for a company and return the results
    
    Args:
        company_name: Name of the company to analyze
        progress: Gradio progress indicator
        
    Returns:
        Tuple containing (JSON results, HTML display, Audio data)
    """
    if not company_name:
        return (
            json.dumps({"error": "Please enter a company name"}, indent=2),
            "<div class='alert alert-danger'>Please enter a company name</div>",
            None
        )
    
    try:
        # Call the API to start analysis
        async with aiohttp.ClientSession() as session:
            # Step 1: Start the analysis
            progress(0.1, desc="Starting analysis...")
            payload = {"company_name": company_name}
            async with session.post(f"{API_URL}/analyze-company", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return (
                        json.dumps({"error": f"API error: {error_text}"}, indent=2),
                        f"<div class='alert alert-danger'>API error: {error_text}</div>",
                        None
                    )
                
                start_response = await response.json()
                task_id = start_response.get("task_id")
                
                if not task_id:
                    return (
                        json.dumps({"error": "No task ID received from API"}, indent=2),
                        "<div class='alert alert-danger'>No task ID received from API</div>",
                        None
                    )
                
                # If data is already available in cache
                if start_response.get("data"):
                    result = start_response["data"]
                    return process_results(result)
            
            # Step 2: Poll for results
            progress_value = 0.2
            max_attempts = 30  # Maximum polling attempts
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                progress_value = min(0.9, progress_value + 0.05)
                progress(progress_value, desc=f"Processing news analysis (attempt {attempt}/{max_attempts})...")
                
                async with session.get(f"{API_URL}/task-status/{task_id}") as status_response:
                    if status_response.status != 200:
                        error_text = await status_response.text()
                        return (
                            json.dumps({"error": f"API status error: {error_text}"}, indent=2),
                            f"<div class='alert alert-danger'>API status error: {error_text}</div>",
                            None
                        )
                    
                    status_data = await status_response.json()
                    
                    # Check if task is completed
                    if status_data.get("completed", False):
                        result = status_data.get("data", {})
                        if "error" in result:
                            return (
                                json.dumps({"error": result["error"]}, indent=2),
                                f"<div class='alert alert-danger'>Analysis error: {result['error']}</div>",
                                None
                            )
                        
                        progress(1.0, desc="Analysis complete!")
                        return process_results(result)
                
                # Wait before polling again
                await asyncio.sleep(2)
            
            # If we reach here, task took too long
            return (
                json.dumps({"error": "Analysis timed out"}, indent=2),
                "<div class='alert alert-danger'>Analysis timed out. Please try again later.</div>",
                None
            )
    except Exception as e:
        logger.error(f"Error in analyze_company: {e}")
        return (
            json.dumps({"error": str(e)}, indent=2),
            f"<div class='alert alert-danger'>Error: {str(e)}</div>",
            None
        )

def process_results(result):
    """
    Process and format the analysis results
    
    Args:
        result: Raw analysis results from API
        
    Returns:
        Tuple containing (JSON results, HTML display, Audio data)
    """
    # Create JSON output
    json_output = json.dumps(result, indent=2, ensure_ascii=False)
    
    # Create HTML display
    html_output = create_html_display(result)
    
    # Get audio data
    audio_data = None
    if "Audio" in result and result["Audio"]:
        audio_data = process_audio(result["Audio"])
    
    return json_output, html_output, audio_data

def process_audio(audio_base64):
    """Process and return audio data"""
    try:
        # Create temporary file to store the audio
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"/tmp/tts_audio_{timestamp}.wav"
        
        # Decode base64 and write to file
        audio_bytes = base64.b64decode(audio_base64)
        with open(filename, "wb") as f:
            f.write(audio_bytes)
        
        return filename
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        return None

def create_html_display(result):
    """
    Create a formatted HTML display of the analysis results
    
    Args:
        result: Analysis results dictionary
        
    Returns:
        HTML string for display
    """
    if "error" in result:
        return f"<div class='alert alert-danger'>Error: {result['error']}</div>"
    
    company = result.get("Company", "Unknown Company")
    articles = result.get("Articles", [])
    comparative = result.get("Comparative Sentiment Score", {})
    final_sentiment = result.get("Final Sentiment Analysis", "")
    hindi_text = result.get("Hindi Text", "")
    
    # Start building HTML
    html = f"""
    <div class='container'>
        <div class='row mt-4 mb-4'>
            <div class='col-12'>
                <div class='card'>
                    <div class='card-header bg-primary text-white'>
                        <h2 class='mb-0'>{company} - News Analysis Report</h2>
                    </div>
                    <div class='card-body'>
                        <div class='alert alert-info'>
                            <strong>Final Sentiment Analysis:</strong> {final_sentiment}
                        </div>
                        
                        <div class='mb-3'>
                            <strong>Hindi Summary:</strong> 
                            <p>{hindi_text}</p>
                        </div>
    """
    
    # Add sentiment distribution
    sentiment_dist = comparative.get("Sentiment Distribution", {})
    if sentiment_dist:
        positive = sentiment_dist.get("POSITIVE", 0)
        negative = sentiment_dist.get("NEGATIVE", 0)
        neutral = sentiment_dist.get("NEUTRAL", 0)
        total = positive + negative + neutral
        
        # Calculate percentages
        if total > 0:
            pos_pct = (positive / total) * 100
            neg_pct = (negative / total) * 100
            neu_pct = (neutral / total) * 100
        else:
            pos_pct = neg_pct = neu_pct = 0
        
        html += f"""
        <div class='card mb-4'>
            <div class='card-header'>
                <h3>Sentiment Distribution</h3>
            </div>
            <div class='card-body'>
                <div class='row'>
                    <div class='col-md-8'>
                        <div class='progress' style='height: 30px;'>
                            <div class='progress-bar bg-success' role='progressbar' style='width: {pos_pct}%' 
                                aria-valuenow='{pos_pct}' aria-valuemin='0' aria-valuemax='100'>
                                Positive ({positive})
                            </div>
                            <div class='progress-bar bg-warning' role='progressbar' style='width: {neu_pct}%' 
                                aria-valuenow='{neu_pct}' aria-valuemin='0' aria-valuemax='100'>
                                Neutral ({neutral})
                            </div>
                            <div class='progress-bar bg-danger' role='progressbar' style='width: {neg_pct}%' 
                                aria-valuenow='{neg_pct}' aria-valuemin='0' aria-valuemax='100'>
                                Negative ({negative})
                            </div>
                        </div>
                    </div>
                    <div class='col-md-4'>
                        <div class='card'>
                            <div class='card-body text-center'>
                                <div class='h4'>Total Articles</div>
                                <div class='display-4'>{total}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    # Add comparison insights
    comparisons = comparative.get("Coverage Differences", [])
    if comparisons:
        html += """
        <div class='card mb-4'>
            <div class='card-header'>
                <h3>Coverage Comparison Insights</h3>
            </div>
            <div class='card-body'>
                <div class='list-group'>
        """
        
        for comp in comparisons:
            comparison = comp.get("Comparison", "")
            impact = comp.get("Impact", "")
            
            html += f"""
            <div class='list-group-item'>
                <div class='d-flex w-100 justify-content-between'>
                    <h5 class='mb-1'>Insight</h5>
                </div>
                <p class='mb-1'>{comparison}</p>
                <small class='text-muted'>Impact: {impact}</small>
            </div>
            """
        
        html += """
                </div>
            </div>
        </div>
        """
    
    # Add topic overlap
    topic_overlap = comparative.get("Topic Overlap", {})
    if topic_overlap:
        common_topics = topic_overlap.get("Common Topics", [])
        topic_dist = topic_overlap.get("Topic Distribution", {})
        
        html += """
        <div class='card mb-4'>
            <div class='card-header'>
                <h3>Topic Analysis</h3>
            </div>
            <div class='card-body'>
        """
        
        if common_topics:
            html += """
            <div class='mb-3'>
                <h4>Common Topics:</h4>
                <div class='d-flex flex-wrap'>
            """
            
            for topic in common_topics:
                html += f"<span class='badge bg-primary me-2 mb-2 p-2'>{topic}</span>"
            
            html += """
                </div>
            </div>
            """
        
        if topic_dist:
            html += """
            <div>
                <h4>All Topics:</h4>
                <div class='d-flex flex-wrap'>
            """
            
            for topic, count in topic_dist.items():
                html += f"<span class='badge bg-secondary me-2 mb-2 p-2'>{topic} ({count})</span>"
            
            html += """
                </div>
            </div>
            """
        
        html += """
            </div>
        </div>
        """
    
    # Add article cards
    if articles:
        html += """
        <h3 class='mb-3'>Articles Analysis</h3>
        <div class='row'>
        """
        
        for i, article in enumerate(articles):
            title = article.get("title", f"Article {i+1}")
            summary = article.get("summary", "No summary available")
            sentiment = article.get("sentiment", {}).get("label", "NEUTRAL")
            topics = article.get("topics", [])
            url = article.get("url", "#")
            
            # Determine card color based on sentiment
            card_class = "bg-light"
            if sentiment == "POSITIVE":
                card_class = "border-success"
            elif sentiment == "NEGATIVE":
                card_class = "border-danger"
            
            html += f"""
            <div class='col-md-6 mb-4'>
                <div class='card h-100 {card_class}'>
                    <div class='card-header d-flex justify-content-between'>
                        <h5 class='mb-0'>Article {i+1}</h5>
                        <span class='badge {"bg-success" if sentiment == "POSITIVE" else "bg-danger" if sentiment == "NEGATIVE" else "bg-warning"}'>
                            {sentiment}
                        </span>
                    </div>
                    <div class='card-body'>
                        <h5 class='card-title'>{title}</h5>
                        <p class='card-text'>{summary}</p>
                        
                        <div class='mt-3'>
                            <strong>Topics:</strong>
                            <div class='mt-1'>
            """
            
            for topic in topics:
                html += f"<span class='badge bg-info me-1 mb-1'>{topic}</span>"
            
            html += f"""
                            </div>
                        </div>
                    </div>
                    <div class='card-footer'>
                        <a href='{url}' target='_blank' class='btn btn-sm btn-primary'>Read Original</a>
                    </div>
                </div>
            </div>
            """
        
        html += """
        </div>
        """
    
    # Close the main containers
    html += """
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return html

# Create Gradio Interface
async def create_interface():
    # Get cached companies to add to the dropdown
    cached = await get_cached_companies()
    companies_list = list(set(POPULAR_COMPANIES + cached))
    companies_list.sort()
    
    with gr.Blocks(css="""
    .gradio-container {
        max-width: 100% !important;
    }
    .output-html {
        height: 800px;
        overflow-y: auto;
    }
    """) as app:
        gr.Markdown("""
        # News Analyzer with Sentiment Analysis and Hindi TTS
        
        This application extracts news articles related to a company, performs sentiment analysis, and generates a Hindi text-to-speech summary.
        
        ## How to use:
        1. Select or type a company name
        2. Click "Analyze" to start the analysis
        3. View the structured report and listen to the Hindi summary
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                # Input components
                company_input = gr.Dropdown(
                    choices=companies_list,
                    label="Company Name",
                    info="Select a company or type a custom name",
                    allow_custom_value=True
                )
                
                analyze_btn = gr.Button("Analyze", variant="primary")
                
                # Audio output
                audio_output = gr.Audio(label="Hindi Summary (Audio)", type="filepath")
            
            with gr.Column(scale=2):
                # Output tabs
                with gr.Tabs():
                    with gr.TabItem("Visual Report"):
                        html_output = gr.HTML(label="Analysis Results", elem_classes=["output-html"])
                    
                    with gr.TabItem("JSON Data"):
                        json_output = gr.JSON(label="Raw JSON Data")
        
        # Set up the event
        analyze_btn.click(
            fn=analyze_company,
            inputs=[company_input],
            outputs=[json_output, html_output, audio_output]
        )
    
    return app

# Launch the app
if __name__ == "__main__":
    # Create and launch the interface
    loop = asyncio.get_event_loop()
    interface = loop.run_until_complete(create_interface())
    interface.launch(server_name="0.0.0.0", server_port=5000)
