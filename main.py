import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, CrossEncoder
from google import genai
import re
import os
from dotenv import load_dotenv

# =========================
# CONFIGURATION
# =========================
# Load the hidden variables from the .env file
load_dotenv(override=True)

# Now it grabs the secret key safely without showing it!
API_KEY = os.getenv("GEMINI_API_KEY")

# Let's print just the first 10 characters to prove which key it is using
print(f"🕵️ DEBUG: The key being used starts with: {str(API_KEY)[:10]}...")

# Initialize the 2026 SDK Client
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"

# =========================
# STEP 1 & 2: DATA LOAD & CLEAN
# =========================

def load_data():
    texts = []
    # Load PDFs/Txt from data folder
    if os.path.exists("data"):
        for file in os.listdir("data"):
            if file.endswith(".txt"):
                with open(os.path.join("data", file), "r", encoding="utf-8") as f:
                    texts.append(f.read())
    
    # Load CSV (Looking for your train.csv)
    if os.path.exists("train.csv"):
        try:
            df = pd.read_csv("train.csv")
            # Checking your specific columns
            if "Question" in df.columns and "Answer" in df.columns:
                texts.extend((df["Question"].astype(str) + " " + df["Answer"].astype(str)).tolist())
            else:
                print(f"⚠️ 'Question/Answer' columns not found. Using: {df.columns[0]} and {df.columns[1]}")
                texts.extend((df.iloc[:, 0].astype(str) + " " + df.iloc[:, 1].astype(str)).tolist())
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            
    return texts

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9.,()\n\- ]+', ' ', text)
    return text.strip()

def detect_type(text):
    t = text.lower()
    if any(word in t for word in ["condition", "refers to", "defined as"]): return "definition"
    if any(word in t for word in ["symptom", "sign", "pain"]): return "symptoms"
    if any(word in t for word in ["treat", "therapy", "surgery", "medication"]): return "treatment"
    return "general"

# =========================
# STEP 4: ENHANCED CHUNKING
# =========================

def chunk_text(text, chunk_size=600, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append({
            "text": chunk.strip(),
            "type": detect_type(chunk)
        })
        start += (chunk_size - overlap)
    return chunks

# =========================
# STEP 6: BUILD INDEX
# =========================

def build_index(all_texts):
    print("🚀 Building Medical Index...")
    all_chunks = []
    for text in all_texts:
        cleaned = clean_text(text)
        all_chunks.extend(chunk_text(cleaned))

    unique_chunks = list({c["text"]: c for c in all_chunks}.values())
    
    print("🧠 Embedding data (this may take a minute)...")
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    texts = [c["text"] for c in unique_chunks]
    embeddings = embed_model.encode(texts, normalize_embeddings=True).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, "faiss_index.bin")
    np.save("chunks.npy", np.array(unique_chunks, dtype=object))
    print(f"✅ Indexed {len(unique_chunks)} chunks successfully!")

# =========================
# STEP 9: QUERY SYSTEM
# =========================

def query_system():
    if not os.path.exists("faiss_index.bin"):
        print("❌ No index found. Please run Option 1 first!")
        return

    index = faiss.read_index("faiss_index.bin")
    chunks = np.load("chunks.npy", allow_pickle=True)
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("🔄 Loading Reranker...")
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    while True:
        query = input("\n🩺 Medical Question (or 'exit'): ")
        if query.lower() == "exit": break

        # 1. Vector Search
        query_emb = embed_model.encode([query], normalize_embeddings=True).astype("float32")
        _, indices = index.search(query_emb, 10)
        
        retrieved = [chunks[i] for i in indices[0] if i != -1]
        
        # 2. Reranking for Accuracy
        pairs = [[query, c["text"]] for c in retrieved]
        scores = reranker.predict(pairs)
        ranked = sorted(zip(retrieved, scores), key=lambda x: x[1], reverse=True)
        top_chunks = [c["text"] for c, _ in ranked[:3]] 

        context = "\n---\n".join(top_chunks)

        # 3. Generation with NEW Gemini SDK
        prompt = f"""You are a professional medical assistant. Use the provided context to answer the question.
        If the answer isn't in the context, say you don't know based on the provided data.
        
        CONTEXT:
        {context}
        
        QUESTION:
        {query}
        
        ANSWER:"""

        try:
            # Updated call for 2026 SDK
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            print("\n🔍 AI RESPONSE:\n", response.text)
        except Exception as e:
            print(f"❌ Error: {e}")

# =========================
# MAIN EXECUTION
# =========================

if __name__ == "__main__":
    print("--- Medical RAG System (2026) ---")
    print("1. Build/Update Index (Run this if you added new data)")
    print("2. Ask Questions")
    choice = input("Choice: ")
    
    if choice == "1":
        data = load_data()
        if data:
            build_index(data)
        else:
            print("❌ No data found in 'data/' folder or 'train.csv'")
    elif choice == "2":
        query_system()
    else:
        print("❌ Invalid choice. Please choose 1 or 2.")