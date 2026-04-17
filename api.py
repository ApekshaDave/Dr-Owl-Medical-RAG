from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import ollama
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

app = FastAPI()

# --- 1. CONFIGURATION ---
# Note: llama3.2:1b is text-only. 
# If you want image support later, change this to "moondream"
MODEL_NAME = "llama3.2:1b"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. LOAD DATABASE ---
try:
    embed_model = SentenceTransformer('all-MiniLM-L6-v2') 
    index = faiss.read_index("faiss_index.bin")
    chunks = np.load("chunks.npy", allow_pickle=True)
    print(f"✅ Medical Database Loaded: {len(chunks)} chunks ready.")
    print(f"✅ Active Model: {MODEL_NAME}")
except Exception as e:
    print(f"❌ Error loading database files: {e}")
    index = None

class ChatRequest(BaseModel):
    question: str
    image: Optional[str] = None # Base64 string from React

@app.post("/chat")
def chat_with_medical_ai(req: ChatRequest):
    if index is None:
        raise HTTPException(status_code=500, detail="Database files missing on server.")

    try:
        # --- 3. RETRIEVAL (Search) ---
        query_vector = embed_model.encode([req.question]).astype('float32')
        distances, indices = index.search(query_vector, k=3) # Top 3 matches
        
        retrieved_docs = []
        context_text = ""
        
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1:
                raw_chunk = chunks[idx]
                
                # Critical fix: Ensure raw_chunk is converted to string correctly
                if isinstance(raw_chunk, dict):
                    content = str(raw_chunk.get('text', raw_chunk))
                else:
                    content = str(raw_chunk)

                retrieved_docs.append({
                    "document_name": "Medical_Dataset.csv",
                    "score": f"{1 / (1 + dist):.2f}",
                    "text": content
                })
                context_text += content + "\n\n"

        # --- 4. GENERATION ---
        system_instruction = (
            "You are Dr. Owl, a professional medical AI assistant. "
            "Use the provided context to answer the user's question accurately. "
            "Be detailed and helpful. If you don't know the answer from the context, "
            "use your general knowledge but mention that it's general info."
        )
        
        user_prompt = f"CONTEXT:\n{context_text}\n\nUSER QUESTION: {req.question}"

        # Prepare the message payload
        message = {'role': 'user', 'content': user_prompt}

        # Handle Image (Only if model supports it)
        # Note: llama3.2:1b will likely ignore this, but it keeps your code robust.
        if req.image:
            # Clean base64 string if header is present
            img_data = req.image.split(",")[-1] 
            message['images'] = [img_data]

        response = ollama.chat(model=MODEL_NAME, messages=[
            {'role': 'system', 'content': system_instruction},
            message
        ])

        # --- 5. RESPONSE EXTRACTION ---
        if hasattr(response, 'message'):
            actual_answer = response.message.content
        elif isinstance(response, dict) and 'message' in response:
            actual_answer = response['message']['content']
        else:
            actual_answer = str(response)

        return {
            "answer": actual_answer,
            "sources": retrieved_docs 
        }

    except Exception as e:
        print(f"❌ Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Running on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)