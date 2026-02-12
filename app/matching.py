"""
Matching engine for lost and found items.
Uses text similarity, location proximity, and time difference.
"""
from app.models import Item, Match, db
from app.bati.utils import calculate_haversine_distance, calculate_text_similarity
from datetime import datetime, timedelta
from flask import current_app

def calculate_match_score(lost_item, found_item):
    """
    Calculate matching score between lost and found items.
    
    Returns:
        float: Score between 0 and 1
    """
    # Text similarity (50% weight)
    text_score = calculate_text_similarity(
        f"{lost_item.title} {lost_item.description or ''}",
        f"{found_item.title} {found_item.description or ''}"
    )
    
    # Location proximity (30% weight)
    distance = calculate_haversine_distance(
        lost_item.latitude, lost_item.longitude,
        found_item.latitude, found_item.longitude
    )
    threshold = current_app.config.get('LOCATION_PROXIMITY_THRESHOLD', 5000)
    location_score = max(0, 1 - (distance / threshold))
    
    # Time difference (20% weight)
    time_diff = abs((lost_item.reported_at - found_item.reported_at).total_seconds())
    # Normalize: 7 days = 0 score, 0 days = 1 score
    max_days = 7 * 24 * 3600  # 7 days in seconds
    time_score = max(0, 1 - (time_diff / max_days))
    
    # Weighted combination
    final_score = (0.5 * text_score) + (0.3 * location_score) + (0.2 * time_score)
    
    return final_score

def find_matches_for_item(item):
    """
    Find potential matches for a given item.
    
    Args:
        item: Item instance (lost or found)
    
    Returns:
        list: List of Match objects
    """
    matches = []
    threshold = current_app.config.get('MATCH_CONFIDENCE_THRESHOLD', 0.6)
    
    if item.status == 'lost':
        # Find matching found items
        found_items = Item.query.filter_by(status='found').all()
        for found_item in found_items:
            score = calculate_match_score(item, found_item)
            if score >= threshold:
                # Check if match already exists
                existing_match = Match.query.filter_by(
                    lost_item_id=item.id,
                    found_item_id=found_item.id
                ).first()
                
                if not existing_match:
                    match = Match(
                        lost_item_id=item.id,
                        found_item_id=found_item.id,
                        confidence_score=score
                    )
                    db.session.add(match)
                    matches.append(match)
                else:
                    # Update existing match score
                    existing_match.confidence_score = score
                    matches.append(existing_match)
    
    elif item.status == 'found':
        # Find matching lost items
        lost_items = Item.query.filter_by(status='lost').all()
        for lost_item in lost_items:
            score = calculate_match_score(lost_item, item)
            if score >= threshold:
                # Check if match already exists
                existing_match = Match.query.filter_by(
                    lost_item_id=lost_item.id,
                    found_item_id=item.id
                ).first()
                
                if not existing_match:
                    match = Match(
                        lost_item_id=lost_item.id,
                        found_item_id=item.id,
                        confidence_score=score
                    )
                    db.session.add(match)
                    matches.append(match)
                else:
                    # Update existing match score
                    existing_match.confidence_score = score
                    matches.append(existing_match)
    
    db.session.commit()
    return matches

def find_all_matches():
    """
    Recalculate all matches in the system.
    Useful for admin operations or periodic updates.
    """
    lost_items = Item.query.filter_by(status='lost').all()
    all_matches = []
    
    for lost_item in lost_items:
        matches = find_matches_for_item(lost_item)
        all_matches.extend(matches)
    
    return all_matches
