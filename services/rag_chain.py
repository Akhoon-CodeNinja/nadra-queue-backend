import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

VECTOR_STORE_DIR = os.path.join(settings.BASE_DIR, 'vector_store')
FAISS_INDEX_PATH = os.path.join(VECTOR_STORE_DIR, 'faiss_index.bin')
CHUNKS_JSON_PATH = os.path.join(VECTOR_STORE_DIR, 'chunks.json')

embedder = SentenceTransformer('all-MiniLM-L6-v2')

try:
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(CHUNKS_JSON_PATH, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
except Exception as e:
    index = None
    chunks = []
    print("Warning: FAISS index load nahi hua.")

def get_rag_answer(user_query):
    if not index:
        return "System error: NADRA rules database is offline."

    # =========================================================
    # STEP 1: SEMANTIC QUERY ANALYSIS (Intent Extraction)
    # =========================================================
    analysis_prompt = (
        "You are a Semantic Query Analyzer for NADRA Pakistan. "
        "Extract the core intent from the user's query and output ONLY 3 to 4 highly relevant search keywords in English. "
        "Translate layman terms to official terms (e.g., 'smart card' -> 'Smart NIC', 'b-form' -> 'Child Registration Certificate', 'gum' -> 'lost'). "
        "Do not write full sentences, just comma-separated keywords."
    )
    
    try:
        analyzed_keywords = client.chat.completions.create(
            messages=[
                {"role": "system", "content": analysis_prompt},
                {"role": "user", "content": user_query}
            ],
            model="llama-3.1-8b-instant", # Fast model for intent
            temperature=0.1
        ).choices[0].message.content.strip()
    except Exception as e:
        print(f"Analyzer Error: {e}")
        analyzed_keywords = user_query # Fallback to original query

    print(f"Original Query: {user_query}")
    print(f"Semantic Keywords for Search: {analyzed_keywords}")

    # =========================================================
    # STEP 2: COSINE SIMILARITY SEARCH (FAISS)
    # =========================================================
    query_vector = embedder.encode([analyzed_keywords])
    query_vector = np.array(query_vector).astype('float32')

    k = 5
    distances, indices = index.search(query_vector, k)
    
    # LOCK 2: Thresholding (Out of Domain filter)
    # Agar cosine distance 1.5 se zyada hai, toh iska matlab irrelevant sawal hai
    best_score = distances[0][0]
    if best_score > 1.5:  
        return "Maaf kijiye, main sirf NADRA aur identity documents se mutaaliq sawalaat ke jawab de sakta hoon."

    context_texts = [chunks[i] for i in indices[0]]
    context_block = "\n\n---\n\n".join(context_texts)

    # =========================================================
    # STEP 3: FINAL GENERATION (Strict Locks + Table Parsing)
    # =========================================================
    system_prompt = (
        "You are a highly professional and confident official NADRA Pakistan virtual assistant. "
        "Your ONLY source of knowledge is the provided context. "
        "RULE 1: If the answer is perfectly clear in the context, provide it CONFIDENTLY directly. DO NOT apologize or say you cannot do something if you are actively providing the information. "
        "RULE 2: Only if the answer is completely missing from the context, say exactly: 'Maaf kijiye, mere paas iski maloomat nahi hai.' "
        "RULE 3: Under NO circumstances should you use outside knowledge, guess, or hallucinate. "
        "RULE 4: Do not offer advice that is not explicitly written in the context. "
        "RULE 5: The context contains fee tables formatted as raw text. Extract numbers intelligently (e.g., 'Normal 750, Urgent 1500'). "
        "Respond entirely in clear, natural Roman Urdu without unnecessary apologies."
        f"\n\nContext:\n{context_block}"
    )

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.0, # LOCK 1: Zero Temperature (No creativity/guessing)
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLaMA Error: {e}")
        return "Backend par AI generate karne mein masla pesh aaya hai."