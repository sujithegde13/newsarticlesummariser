import os
import logging
import asyncio
import re
import json
from typing import Dict, List, Any, Tuple, Optional
import urllib.parse
import requests
import feedparser
from bs4 import BeautifulSoup
import trafilatura
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

# NLP Libraries
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from keybert import KeyBERT
from googletrans import Translator
import torch

# TTS Library
from TTS.api import TTS
import numpy as np
import soundfile as sf
import tempfile
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize models with caching mechanism
@lru_cache(maxsize=1)
def get_sentiment_model():
    """Initialize and cache sentiment analysis model"""
    logger.info("Loading sentiment analysis model...")
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    sentiment_model = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name)
    return sentiment_model

@lru_cache(maxsize=1)
def get_summarization_model():
    """Initialize and cache summarization model"""
    logger.info("Loading summarization model...")
    model_name = "sshleifer/distilbart-cnn-12-6"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return model, tokenizer

@lru_cache(maxsize=1)
def get_keyword_model():
    """Initialize and cache KeyBERT model"""
    logger.info("Loading keyword extraction model...")
    keyword_model = KeyBERT()
    return keyword_model

@lru_cache(maxsize=1)
def get_tts_model():
    """Initialize and cache TTS model for Hindi"""
    logger.info("Loading TTS model...")
    tts_model = TTS(model_name="tts_models/hi/coqui/vits", progress_bar=False)
    return tts_model

# Initialize translator
translator = Translator()

class NewsAnalyzer:
    def __init__(self):
        """Initialize the NewsAnalyzer with required models"""
        self.sentiment_model = get_sentiment_model()
        self.summarization_model, self.summarization_tokenizer = get_summarization_model()
        self.keyword_model = get_keyword_model()
        self.tts_model = get_tts_model()
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def get_google_news_urls(self, company_name: str, max_results: int = 15) -> List[str]:
        """
        Fetch news article URLs from Google News RSS feed for a given company
        
        Args:
            company_name: Name of the company to search for
            max_results: Maximum number of URLs to return
            
        Returns:
            List of news article URLs
        """
        try:
            # Encode company name for URL
            encoded_query = urllib.parse.quote(company_name)
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            # Parse the RSS feed
            logger.info(f"Fetching news for {company_name} from {rss_url}")
            feed = feedparser.parse(rss_url)
            
            # Extract URLs
            urls = []
            for entry in feed.entries[:max_results]:
                # The link in Google News RSS redirects to the actual article
                redirect_url = entry.link
                
                # Make a request to follow the redirect
                try:
                    response = requests.get(redirect_url, allow_redirects=True, timeout=5)
                    if response.status_code == 200:
                        final_url = response.url
                        urls.append(final_url)
                except Exception as e:
                    logger.warning(f"Failed to follow redirect for {redirect_url}: {e}")
            
            logger.info(f"Found {len(urls)} news articles for {company_name}")
            return urls
        except Exception as e:
            logger.error(f"Error fetching Google News for {company_name}: {e}")
            return []
    
    def extract_article_content(self, url: str) -> Dict[str, Any]:
        """
        Extract content from a news article URL using Trafilatura
        
        Args:
            url: URL of the news article
            
        Returns:
            Dictionary containing extracted article data
        """
        try:
            logger.info(f"Extracting content from {url}")
            
            # Download and extract content
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return {"title": "", "text": "", "url": url, "error": "Failed to download page"}
            
            # Extract text content
            text = trafilatura.extract(downloaded)
            
            # Use BeautifulSoup to extract title if trafilatura doesn't
            soup = BeautifulSoup(downloaded, 'html.parser')
            title = soup.title.string if soup.title else ""
            
            # Clean up title
            title = title.strip() if title else ""
            
            return {
                "title": title,
                "text": text,
                "url": url
            }
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return {"title": "", "text": "", "url": url, "error": str(e)}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Perform sentiment analysis on text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment label and score
        """
        try:
            # Limit text length for the model
            text = text[:1024] if text else ""
            if not text:
                return {"label": "NEUTRAL", "score": 0.5}
            
            # Get sentiment
            result = self.sentiment_model(text)[0]
            
            # Map the label to Positive/Negative/Neutral
            label_mapping = {
                "LABEL_0": "NEGATIVE",
                "LABEL_1": "NEUTRAL",
                "LABEL_2": "POSITIVE"
            }
            
            sentiment = {
                "label": label_mapping.get(result["label"], result["label"]),
                "score": result["score"]
            }
            
            return sentiment
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {"label": "NEUTRAL", "score": 0.5}
    
    def summarize_text(self, text: str, max_length: int = 150) -> str:
        """
        Summarize text using distilbart model
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        try:
            # Limit input text length
            text = text[:1024] if text else ""
            if not text:
                return ""
            
            # Prepare inputs
            inputs = self.summarization_tokenizer([text], max_length=1024, return_tensors="pt", truncation=True)
            
            # Generate summary
            summary_ids = self.summarization_model.generate(
                inputs.input_ids, 
                max_length=max_length,
                min_length=30,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            
            summary = self.summarization_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """
        Extract key topics from text using KeyBERT
        
        Args:
            text: Text to extract keywords from
            top_n: Number of keywords to extract
            
        Returns:
            List of extracted keywords/topics
        """
        try:
            # Limit text length
            text = text[:2048] if text else ""
            if not text:
                return []
            
            # Extract keywords
            keywords = self.keyword_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n)
            
            # Return only the keywords, not the scores
            return [keyword[0].capitalize() for keyword in keywords]
        except Exception as e:
            logger.error(f"Error in keyword extraction: {e}")
            return []
    
    def translate_to_hindi(self, text: str) -> str:
        """
        Translate text to Hindi using Google Translate
        
        Args:
            text: Text to translate
            
        Returns:
            Translated Hindi text
        """
        try:
            # Limit text length
            text = text[:1500] if text else ""
            if not text:
                return ""
            
            # Translate to Hindi
            result = translator.translate(text, dest='hi')
            return result.text
        except Exception as e:
            logger.error(f"Error in translation: {e}")
            return text
    
    def generate_tts(self, hindi_text: str) -> str:
        """
        Generate Hindi TTS audio from text
        
        Args:
            hindi_text: Hindi text to convert to speech
            
        Returns:
            Base64 encoded audio data
        """
        try:
            # Limit text length for TTS
            hindi_text = hindi_text[:500] if hindi_text else ""
            if not hindi_text:
                return ""
            
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Generate speech
            self.tts_model.tts_to_file(text=hindi_text, file_path=temp_path)
            
            # Read audio file and encode in base64
            with open(temp_path, 'rb') as audio_file:
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
            
            # Clean up temp file
            os.remove(temp_path)
            
            return audio_data
        except Exception as e:
            logger.error(f"Error in TTS generation: {e}")
            return ""
    
    def perform_comparative_analysis(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comparative sentiment analysis across articles
        
        Args:
            articles: List of analyzed articles
            
        Returns:
            Dictionary with comparative analysis results
        """
        try:
            # Count sentiment distribution
            sentiment_count = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            for article in articles:
                sentiment = article.get("sentiment", {}).get("label", "NEUTRAL")
                sentiment_count[sentiment] += 1
            
            # Collect all topics
            all_topics = {}
            topic_article_map = {}
            
            for i, article in enumerate(articles):
                topics = article.get("topics", [])
                for topic in topics:
                    if topic not in all_topics:
                        all_topics[topic] = 0
                        topic_article_map[topic] = []
                    all_topics[topic] += 1
                    topic_article_map[topic].append(i)
            
            # Find common and unique topics
            common_topics = [topic for topic, count in all_topics.items() if count > 1]
            
            # Generate comparison insights
            comparisons = []
            if len(articles) >= 2:
                # Compare the first few articles for demonstration
                for i in range(min(3, len(articles))):
                    for j in range(i+1, min(4, len(articles))):
                        if i != j and "sentiment" in articles[i] and "sentiment" in articles[j]:
                            sentiment_i = articles[i]["sentiment"]["label"]
                            sentiment_j = articles[j]["sentiment"]["label"]
                            
                            if sentiment_i != sentiment_j:
                                comparison = {
                                    "Comparison": f"Article {i+1} has a {sentiment_i.lower()} sentiment, while Article {j+1} has a {sentiment_j.lower()} sentiment.",
                                    "Impact": f"This shows varying perspectives in the news coverage about the company."
                                }
                                comparisons.append(comparison)
            
            # Generate final sentiment assessment
            positive_ratio = sentiment_count["POSITIVE"] / len(articles) if articles else 0
            negative_ratio = sentiment_count["NEGATIVE"] / len(articles) if articles else 0
            
            if positive_ratio > 0.6:
                final_sentiment = "mostly positive"
                expectation = "Potential positive impact expected."
            elif negative_ratio > 0.6:
                final_sentiment = "mostly negative"
                expectation = "Potential challenges might be ahead."
            else:
                final_sentiment = "mixed"
                expectation = "The situation appears complex with both positive and negative aspects."
            
            # Create the comparative analysis result
            result = {
                "Sentiment Distribution": sentiment_count,
                "Coverage Differences": comparisons,
                "Topic Overlap": {
                    "Common Topics": common_topics,
                    "Topic Distribution": {topic: count for topic, count in all_topics.items()}
                },
                "Final Sentiment Analysis": f"The company's latest news coverage is {final_sentiment}. {expectation}"
            }
            
            return result
        except Exception as e:
            logger.error(f"Error in comparative analysis: {e}")
            return {"error": str(e)}
    
    async def process_article(self, url: str) -> Dict[str, Any]:
        """
        Process a single article: extract content, analyze sentiment, summarize, etc.
        
        Args:
            url: URL of the article
            
        Returns:
            Dictionary with processed article data
        """
        try:
            # Extract content
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(self.executor, self.extract_article_content, url)
            
            if not content.get("text") or content.get("error"):
                logger.warning(f"Could not extract content from {url}")
                return {"url": url, "error": content.get("error", "No content extracted")}
            
            # Summarize
            summary = await loop.run_in_executor(self.executor, self.summarize_text, content["text"])
            
            # Sentiment analysis
            sentiment = await loop.run_in_executor(self.executor, self.analyze_sentiment, content["text"])
            
            # Keyword extraction
            topics = await loop.run_in_executor(self.executor, self.extract_keywords, content["text"])
            
            # Prepare result
            result = {
                "title": content["title"],
                "summary": summary,
                "sentiment": sentiment,
                "topics": topics,
                "url": url
            }
            
            return result
        except Exception as e:
            logger.error(f"Error processing article {url}: {e}")
            return {"url": url, "error": str(e)}
    
    async def analyze_company_news(self, company_name: str) -> Dict[str, Any]:
        """
        Main method to analyze news for a company
        
        Args:
            company_name: Name of the company to analyze
            
        Returns:
            Complete analysis results including comparative analysis and TTS
        """
        try:
            # Get news URLs
            urls = self.get_google_news_urls(company_name)
            
            if not urls:
                return {
                    "Company": company_name,
                    "error": "No news articles found for this company"
                }
            
            # Process articles (limit to 10)
            urls = urls[:10]
            tasks = [self.process_article(url) for url in urls]
            articles = await asyncio.gather(*tasks)
            
            # Filter out failed articles
            valid_articles = [article for article in articles if "error" not in article]
            
            if not valid_articles:
                return {
                    "Company": company_name,
                    "error": "Could not process any articles for this company"
                }
            
            # Perform comparative analysis
            comparative_analysis = self.perform_comparative_analysis(valid_articles)
            
            # Create Hindi summary for TTS
            final_sentiment = comparative_analysis.get("Final Sentiment Analysis", "")
            tts_text = f"{company_name} के बारे में समाचार विश्लेषण: {final_sentiment}"
            
            # Translate to Hindi
            loop = asyncio.get_event_loop()
            hindi_text = await loop.run_in_executor(self.executor, self.translate_to_hindi, tts_text)
            
            # Generate TTS
            audio_data = await loop.run_in_executor(self.executor, self.generate_tts, hindi_text)
            
            # Prepare final result
            result = {
                "Company": company_name,
                "Articles": valid_articles,
                "Comparative Sentiment Score": comparative_analysis,
                "Final Sentiment Analysis": final_sentiment,
                "Hindi Text": hindi_text,
                "Audio": audio_data
            }
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing company news for {company_name}: {e}")
            return {
                "Company": company_name,
                "error": str(e)
            }
