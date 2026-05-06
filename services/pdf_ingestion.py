import os
import json
import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from django.conf import settings

# Vector store ko save karne ka raasta
VECTOR_STORE_DIR = os.path.join(settings.BASE_DIR, 'vector_store')
FAISS_INDEX_PATH = os.path.join(VECTOR_STORE_DIR, 'faiss_index.bin')
CHUNKS_JSON_PATH = os.path.join(VECTOR_STORE_DIR, 'chunks.json')

def extract_text_from_pdf(pdf_path):
    """PDF file se text nikalta hai."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def chunk_text(text, chunk_size=600, overlap=100):
    """Bade text ko chote paragraphs (chunks) mein todta hai."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def process_and_save_pdf(pdf_path):
    """Main function jo PDF ko FAISS mein store karta hai."""
    print(f"Reading PDF: {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)
    
    print("Creating chunks...")
    chunks = chunk_text(text)
    
    print("Loading Embedding Model (yeh pehli dafa thora time lega)...")
    # Yeh model text ko 384 numbers (vectors) mein badal deta hai
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Embedding {len(chunks)} chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    
    # FAISS Index create karo (384 dimensions)
    index = faiss.IndexFlatL2(384)
    index.add(embeddings)
    
    # Folder banao agar nahi hai
    if not os.path.exists(VECTOR_STORE_DIR):
        os.makedirs(VECTOR_STORE_DIR)
        
    # Vectors aur text ko save karo
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    with open(CHUNKS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Success! {len(chunks)} chunks FAISS index mein save ho gaye hain.")