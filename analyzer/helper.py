import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import nltk
nltk.download('vader_lexicon')
nltk.download('brown')
# helper.py
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline, utils
import numpy as np
from collections import Counter
from collections import defaultdict

# Initialize SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

# Initialize the BART summarizer from Hugging Face
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def classify_sentiment_vader(review):
    """
    Classify sentiment of a review using VADER sentiment analysis.
    """
    score = sia.polarity_scores(review)['compound']
    if score > 0.05:
        return "Positive"
    elif score < -0.05:
        return "Negative"
    else:
        return "Neutral"


def sentiment_to_rating(compound_score):
    """
    Convert compound sentiment score to rating between 1 and 5 stars.
    """
    if compound_score >= 0.6:
        return 5
    elif compound_score >= 0.2:
        return 4
    elif compound_score > -0.2:
        return 3
    elif compound_score > -0.6:
        return 2
    else:
        return 1


def calculate_overall_rating(reviews):
    """
    Calculate the overall rating for a set of reviews.
    """
    ratings = []
    for review in reviews:
        sentiment_score = sia.polarity_scores(review)['compound']
        rating = sentiment_to_rating(sentiment_score)
        ratings.append(rating)

    overall_rating = round(np.mean(ratings), 2)
    return overall_rating, ratings


def extract_keywords_from_reviews(reviews, top_n=5):
    """
    Extract the top N keywords from reviews using TextBlob's noun phrase extraction.
    
    Args:
        reviews (list): A list of review strings.
        top_n (int): Number of top keywords to return.

    Returns:
        list: A list of top N keywords.
    """
    all_keywords = []
    
    # Extract keywords from each review
    for review in reviews:
        blob = TextBlob(review)
        keywords = list(set(blob.noun_phrases))  # Extract noun phrases and remove duplicates
        all_keywords.extend(keywords)
    
    # Count frequency of each keyword and get the top N
    keyword_counts = Counter(all_keywords)
    top_keywords = [keyword for keyword, _ in keyword_counts.most_common(top_n)]
    
    return top_keywords


def overall_summary_of_reviews(reviews, chunk_size=500):
    """
    Summarize a set of reviews by chunking and using BART model for summarization.
    """
    # Combine all reviews into a single string
    combined_text = " ".join(reviews)
    words = combined_text.split()

    # Split the combined text into chunks
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    # Summarize each chunk
    summaries = []
    for chunk in chunks:
        if chunk.strip():  # Check if the chunk is not empty
            summary = summarizer(chunk, max_length=150, min_length=40, do_sample=False)
            if summary:  # Ensure the summary list is not empty
                summaries.append(summary[0]['summary_text'])
            else:
                summaries.append("")  # Handle cases where summarizer doesn't return any result
        else:
            summaries.append("")  # If chunk is empty, append an empty summary

    # Combine the summaries and summarize again if there are multiple summaries
    if len(summaries) > 1:
        # Only combine and summarize again if we have more than one chunk
        combined_summaries = " ".join(summaries)
        if combined_summaries.strip():  # Ensure we have content to summarize
            final_summary = summarizer(combined_summaries, max_length=120, min_length=50, do_sample=False)
            return final_summary[0]['summary_text']
        else:
            return ""  # Return empty string if the combined summaries are empty
    else:
        return summaries[0] if summaries else ""  # Return first summary or empty string if no summaries



def fetch_reviews_from_url(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    regex = re.compile('.*comment.*')
    results = soup.find_all('p', {'class':regex})
    reviews = [result.text for result in results]
    return reviews


def analyze_url(url):
    """
    Analyze feedback for the provided Yelp URL, returning metrics and data.
    """
    # Fetch reviews from the Yelp URL (you need to implement actual fetching logic)
    reviews = fetch_reviews_from_url(url)
    # Final Verdict (hardcoded, but could be dynamically generated from reviews)
    verdict = overall_summary_of_reviews(reviews)

    # Overall Rating
    overall_rating, individual_ratings = calculate_overall_rating(reviews)

    ratings = defaultdict(int)


    for review in reviews:
        sentiment_score = sia.polarity_scores(review)['compound']
        rating = sentiment_to_rating(sentiment_score)
        ratings[f"{rating} stars"] += 1

    total_reviews = len(reviews)

    if total_reviews == 0:
        percent_ratings = {key: 0 for key in ratings}
    else:
        percent_ratings = {key: (value / total_reviews) * 100 for key, value in ratings.items()}

    # Top Reviews (just a placeholder for now)
    top_reviews = reviews[:3]  # Modify based on sentiment scores or other criteria

    # Keywords from reviews
    keywords = extract_keywords_from_reviews(reviews)

    # Returning all the data as a dictionary
    feedback_data = {
        "final_verdict": verdict,
        "overall_rating": overall_rating,
        "ratings": percent_ratings,
        "top_reviews": top_reviews,
        "keywords": keywords
    }

    return feedback_data

