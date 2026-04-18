import os
import io
import sys
import numpy as np
import faiss
from groq import Groq  # Swapped Ollama for Groq
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# --- Windows Encoding Fix ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

app = FastAPI(title="Dr. Owl Medical AI")

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load Knowledge Base ---
print("--- Loading Knowledge Base ---")
try:
    # Use the flag 'faiss.IO_FLAG_MMAP' to save RAM on the cloud
    model = SentenceTransformer('all-MiniLM-L6-v2')
    index = faiss.read_index("faiss_index.bin", faiss.IO_FLAG_MMAP)
    chunks = np.load("chunks.npy", allow_pickle=True)
    print("System Ready: Medical Data Loaded.")
except Exception as e:
    print(f"Initialization Error: {e}")
    sys.exit(1)

# --- Data Models ---
class ChatRequest(BaseModel):
    message: str

# --- Helper Logic ---
def get_relevance_label(score):
    if score >= 75: return "High"
    if score >= 45: return "Medium"
    return "Low"

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        query = request.message
        
        # 1. Vector Search
        query_embedding = model.encode([query])
        distances, indices = index.search(np.array(query_embedding).astype("float32"), k=3)
        
        # 2. Process Sources
        sources = []
        context_text = ""
        total_score = 0
        
        for i, idx in enumerate(indices[0]):
            dist = float(distances[0][i])
            raw_score = max(0, min(100, int((1 - (dist / 2)) * 100)))
            
            chunk_content = str(chunks[idx])
            context_text += f"\n---\n{chunk_content}\n"
            
            sources.append({
                "rank": i + 1,
                "text": chunk_content,
                "score": raw_score,
                "label": get_relevance_label(raw_score),
                "distance": f"{dist:.2f}"
            })
            total_score += raw_score

        overall_relevance = int(total_score / len(sources)) if sources else 0

        # 3. Generate AI Response with Groq (Llama 3.3 70B)
        prompt = f"""
        You are Dr. Owl, a professional medical AI. Use the provided clinical context to answer the user's question.
        If the answer isn't in the context, use your medical knowledge but note that it's general information.
        
        Context: {context_text}
        Question: {query}
        
        Instructions: Use markdown formatting. Be concise, empathetic, and professional.
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Ultra-fast Groq model
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant."},
                {"role": "user", "content": prompt}
            ],
        )

        # 4. Return structured JSON
        return {
            "answer": completion.choices[0].message.content,
            "context": context_text,
            "sources": sources,
            "overall_score": overall_relevance
        }

    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Port 7860 is mandatory for Hugging Face Spaces
    uvicorn.run(app, host="0.0.0.0", port=7860)