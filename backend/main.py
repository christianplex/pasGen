import os
import random
import time
import unicodedata
from google.cloud import firestore
import functions_framework
from flask import jsonify

# Initialize Firestore
db = firestore.Client()
COLLECTION_WORDS = "diccionario_memorables"
COLLECTION_LIMITS = "solicitudes_reducidas"

# Rate limit configuration
MAX_REQUESTS_PER_HOUR = 5
WINDOW_SECONDS = 3600 

def remove_accents(input_str):
    """Normalizes string to remove accents and special characters (like ñ or á)."""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

@functions_framework.http
def generate_passphrase(request):
    # Enable CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}

    # 1. IP Rate Limit (5 per hour)
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    ip_ref = db.collection(COLLECTION_LIMITS).document(user_ip)
    ip_doc = ip_ref.get()
    now = time.time()
    recent_requests = []
    
    if ip_doc.exists:
        timestamps = ip_doc.to_dict().get('timestamps', [])
        recent_requests = [t for t in timestamps if now - t < WINDOW_SECONDS]
        if len(recent_requests) >= MAX_REQUESTS_PER_HOUR:
            next_reset = int((WINDOW_SECONDS - (now - recent_requests[0])) / 60)
            if next_reset <= 0: next_reset = 1
            return (jsonify({"error": f"Límite excedido. Intenta en {next_reset} min."}), 429, headers)

    # 2. Parameters: Target Length (6 to 16)
    try:
        target_length = int(request.args.get('length', 12))
    except:
        target_length = 12
    
    if target_length < 6: target_length = 6
    if target_length > 16: target_length = 16

    # 3. Generation Logic
    # Cost: 1 Dot (1) + 2 Numbers (2) = 3 total
    net_word_length = target_length - 3
    
    # We'll use 2 words if length allows (generally for target_length >= 11)
    use_two_words = net_word_length >= 8 

    try:
        final_words = []
        if use_two_words:
            # Split net_word_length into two parts
            # Example: 13 -> 6 and 7
            len1 = net_word_length // 2
            len2 = net_word_length - len1
            
            for l in [len1, len2]:
                query = db.collection(COLLECTION_WORDS).where('length', '==', l).stream()
                results = list(query)
                if results:
                    word = random.choice(results).to_dict().get('word', '')
                    final_words.append(remove_accents(word).capitalize())
                else:
                    # Fallback if no word of exact length (unlikely with BIP-0039)
                    final_words.append("Abcde"[:l].capitalize())
        else:
            # Single word
            query = db.collection(COLLECTION_WORDS).where('length', '==', net_word_length).stream()
            results = list(query)
            if results:
                word = random.choice(results).to_dict().get('word', '')
                final_words.append(remove_accents(word).capitalize())
            else:
                # Fallback
                final_words.append("Plexarian"[:net_word_length].capitalize())

        # numbers
        num_suffix = f"{random.randint(0, 9)}{random.randint(0, 9)}"

        # 4. Dot Placement
        items = final_words + [num_suffix]
        dot_pos = random.randint(1, len(items) - 1)
        
        passphrase = ""
        for i, item in enumerate(items):
            if i == dot_pos:
                passphrase += "."
            passphrase += item

        # 5. Final adjustment (ensuring exact length)
        # Sometimes normalization or capitalize might slightly change things
        passphrase = passphrase[:target_length]

        # 6. Update Limit
        recent_requests.append(now)
        ip_ref.set({"timestamps": recent_requests[-5:], "ip": user_ip})

        return (jsonify({"password": passphrase}), 200, headers)

    except Exception as e:
        return (jsonify({"error": str(e)}), 500, headers)
