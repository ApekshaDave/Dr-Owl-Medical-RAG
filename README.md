## 🧠 About Dr. Owl
Dr. Owl is a production-grade **Retrieval-Augmented Generation (RAG)** system designed to bridge the gap between static medical datasets and real-time AI reasoning. 

### 🏗️ Architecture Overview
Unlike standard LLM chatbots, Dr. Owl uses a **decoupled architecture**:
- **The Brain:** Groq LPU™ Inference Engine running `Llama-3.3-70b-versatile` for sub-second reasoning.
- **The Memory:** A local FAISS index containing over **45,000 medical records**, enabling the model to cite real clinical data instead of hallucinating.
- **The Infrastructure:** A containerized FastAPI backend hosted on **Hugging Face Spaces** (16GB RAM) and a React frontend on **Vercel**.

### 🛠️ Technical Highlights
- **Semantic Search:** Uses `all-MiniLM-L6-v2` embeddings to transform user queries into high-dimensional vectors.
- **Memory Optimization:** Implements `faiss.IO_FLAG_MMAP` for efficient disk-based vector retrieval on cloud environments.
- **Hardware Acceleration:** Leverages Groq's specialized hardware to achieve near-instant response times for 70B parameter models.
