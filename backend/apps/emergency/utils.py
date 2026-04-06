"""
Emergency Keyword Detection Utility
=====================================
This module scans message text for keywords that indicate
a user may be in a mental health crisis.

HOW IT WORKS:
  1. Normalize text (lowercase, strip punctuation)
  2. Check against tiered keyword lists
  3. Return (is_emergency: bool, keywords_found: list)

TIERS:
  CRITICAL  → Immediate danger (suicidal intent)
  HIGH      → Serious distress
  MODERATE  → Worth monitoring

IMPORTANT ETHICAL NOTE:
  This is NOT a replacement for professional help.
  It's a safety net to route users to resources.
  Always err on the side of caution.
"""

import re

# ─────────────────────────────────────────────────────────────────
# EMERGENCY KEYWORD LISTS
# Organized by severity tier
# ─────────────────────────────────────────────────────────────────

CRITICAL_KEYWORDS = [
    # Direct suicidal ideation
    'suicide', 'suicidal', 'kill myself', 'end my life', 'take my life',
    'want to die', 'wanna die', 'rather be dead', 'better off dead',
    'don\'t want to live', 'dont want to live', 'no reason to live',
    'can\'t go on', 'cant go on', 'planning to die',
    # Self-harm
    'cut myself', 'hurt myself', 'harm myself', 'self harm', 'self-harm',
    'overdose', 'od on', 'take all the pills',
]

HIGH_KEYWORDS = [
    'hopeless', 'worthless', 'meaningless', 'no point', 'give up',
    'can\'t take it anymore', 'cant take it anymore', 'nothing to live for',
    'everyone would be better without me', 'nobody cares',
    'disappeared', 'run away forever', 'escape everything',
    'ending it all', 'making it stop',
]

MODERATE_KEYWORDS = [
    'so depressed', 'extremely anxious', 'panic attack', 'breaking down',
    'falling apart', 'losing my mind', 'can\'t breathe', 'drowning',
    'trapped', 'suffocating', 'overwhelmed',
]


def normalize_text(text):
    """
    Prepare text for keyword matching.
    Lowercase, remove punctuation except spaces and apostrophes.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s']", ' ', text)  # Keep letters, numbers, spaces, apostrophes
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def detect_emergency_keywords(text):
    """
    Scan message text for emergency keywords.
    
    Args:
        text (str): The message to scan
        
    Returns:
        tuple: (is_emergency: bool, keywords_found: list)
        
    Examples:
        detect_emergency_keywords("I want to die") 
        → (True, ['want to die'])
        
        detect_emergency_keywords("I feel a bit sad today")
        → (False, [])
    """
    normalized = normalize_text(text)
    keywords_found = []

    # Check all keyword tiers
    all_keywords = CRITICAL_KEYWORDS + HIGH_KEYWORDS + MODERATE_KEYWORDS

    for keyword in all_keywords:
        # Use word boundary matching to avoid false positives
        # e.g., "hopeless" matches but "hopefully" does not
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, normalized):
            keywords_found.append(keyword)

    is_emergency = len(keywords_found) > 0
    return is_emergency, keywords_found


def get_severity(keywords_found):
    """
    Determine severity level based on which keywords were found.
    
    Returns: 'critical', 'high', 'moderate', or 'none'
    """
    if not keywords_found:
        return 'none'

    for kw in keywords_found:
        if kw in CRITICAL_KEYWORDS:
            return 'critical'

    for kw in keywords_found:
        if kw in HIGH_KEYWORDS:
            return 'high'

    return 'moderate'


# Helpline resources (India-focused + international)
HELPLINE_RESOURCES = [
    {
        'name': 'iCall (India)',
        'number': '9152987821',
        'description': 'Professional psychological counseling',
        'available': 'Mon-Sat, 8am-10pm IST',
        'website': 'https://icallhelpline.org'
    },
    {
        'name': 'Vandrevala Foundation',
        'number': '1860-2662-345',
        'description': 'Free mental health support',
        'available': '24/7',
        'website': 'https://www.vandrevalafoundation.com'
    },
    {
        'name': 'NIMHANS Helpline',
        'number': '080-46110007',
        'description': 'National mental health helpline',
        'available': '24/7',
        'website': 'https://nimhans.ac.in'
    },
    {
        'name': 'Snehi India',
        'number': '+91-44-24640050',
        'description': 'Emotional support helpline',
        'available': '24/7',
        'website': None
    },
    {
        'name': 'International Association for Suicide Prevention',
        'number': None,
        'description': 'Find crisis centers worldwide',
        'available': '24/7',
        'website': 'https://www.iasp.info/resources/Crisis_Centres/'
    },
]
