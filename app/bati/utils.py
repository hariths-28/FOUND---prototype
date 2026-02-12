"""
Utility functions for business logic.
"""
import math
import re
from collections import Counter

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
    
    Returns:
        float: Distance in meters
    """
    # Earth radius in meters
    R = 6371000
    
    # Convert to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

def calculate_text_similarity(text1, text2):
    """
    Calculate text similarity using TF-IDF-like approach.
    Simple word-based cosine similarity.
    
    Args:
        text1, text2: Text strings to compare
    
    Returns:
        float: Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Normalize and tokenize
    def tokenize(text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.split()
    
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    
    if not tokens1 or not tokens2:
        return 0.0
    
    # Create word frequency vectors
    vec1 = Counter(tokens1)
    vec2 = Counter(tokens2)
    
    # Get all unique words
    all_words = set(vec1.keys()) | set(vec2.keys())
    
    if not all_words:
        return 0.0
    
    # Calculate cosine similarity
    dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in all_words)
    
    magnitude1 = math.sqrt(sum(vec1.get(word, 0) ** 2 for word in all_words))
    magnitude2 = math.sqrt(sum(vec2.get(word, 0) ** 2 for word in all_words))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    similarity = dot_product / (magnitude1 * magnitude2)
    return similarity

def allowed_file(filename, allowed_extensions):
    """
    Check if file extension is allowed.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions
    
    Returns:
        bool: True if extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
