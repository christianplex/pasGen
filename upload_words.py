import requests
from google.cloud import firestore
import random
import os

# Initialize Firestore
# Ensure GOOGLE_APPLICATION_CREDENTIALS is set or you're authenticated with gcloud
db = firestore.Client(project="plexarian-pass")

DICTIONARY_URL = "https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/spanish.txt"
COLLECTION_NAME = "diccionario_memorables"

def cleanup_word(word):
    """Basic cleanup to remove whitespace and ensuring lowercase."""
    return word.strip().lower()

def upload_words():
    print(f"Downloading dictionary from {DICTIONARY_URL}...")
    response = requests.get(DICTIONARY_URL)
    if response.status_code != 200:
        print("Error downloading dictionary.")
        return

    words = response.text.splitlines()
    print(f"Total words found: {len(words)}")

    batch = db.batch()
    count = 0
    total_uploaded = 0

    print("Uploading to Firestore...")
    for word in words:
        clean = cleanup_word(word)
        if not clean:
            continue
            
        # We assign a random float to each word for efficient random selection
        # Query: where('random_index', '>=', random.random()).limit(1)
        doc_ref = db.collection(COLLECTION_NAME).document(clean)
        batch.set(doc_ref, {
            "word": clean,
            "random_index": random.random(),
            "length": len(clean)
        })
        
        count += 1
        if count >= 400: # Firestore batch limit is 500
            batch.commit()
            total_uploaded += count
            print(f"Uploaded {total_uploaded} words...")
            batch = db.batch()
            count = 0

    if count > 0:
        batch.commit()
        total_uploaded += count

    print(f"Successfully uploaded {total_uploaded} words to '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    upload_words()
