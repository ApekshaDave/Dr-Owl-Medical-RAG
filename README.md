🦉 Dr. Owl - Medical AI Assistant (RAG)

Dr. Owl is an intelligent Medical Assistant built using a **Retrieval-Augmented Generation (RAG)** architecture. It combines the speed of **Llama 3.2:1b** with a local medical dataset to provide accurate, context-aware health insights.

---

🌟 Features
* **Local RAG:** Searches a custom medical dataset (`.csv`) for precise answers.
* **Privacy-First:** Processes queries locally using Ollama.
* **Modern UI:** Clean, responsive React interface with Markdown support.
* **Source Tracking:** Displays the specific medical context retrieved for transparency.

---

🛠️ Prerequisites

Before you begin, ensure you have the following installed:

1. Ollama (The AI Engine)
  1. Download from [ollama.com](https://ollama.com).
  2. Install and run the Ollama application.
  3. Open your terminal and download the model:
    ```bash
    ollama pull llama3.2:1b

2. Python Environment
   Ensure you have Python 3.9 or higher. Install the required libraries:
   pip install fastapi uvicorn ollama sentence-transformers faiss-cpu numpy

3. Node.js Environment
   Ensure you have Node.js installed to run the React frontend:
   npm install react-markdown


🚀 How to Run the Project
Step 1: Prepare the Database
    Ensure your FAISS index files are in the backend directory:

    1.faiss_index.bin
    2.chunks.npy

Step 2: Start the Backend (API)
   Navigate to your project folder and run:
   python api.py
   
   The server will start at http://127.0.0.1:8000.

Step 3: Start the Frontend (React)
    Open a new terminal, navigate to your React project folder, and run:
    npm start
    
    The application will open automatically at http://localhost:3000.

📁 Project Structure

api.py: FastAPI server handling RAG logic and Ollama integration.

App.js: Main React component for the chat interface.

faiss_index.bin: Vector database for fast medical document retrieval.

chunks.npy: Stored text chunks from your medical dataset.

📊 The Knowledge Base
This AI is powered by a specialized medical dataset to ensure accuracy. 

* **Dataset Source:** [Medical Dataset from Kaggle]https://www.kaggle.com/datasets/thedevastator/comprehensive-medical-q-a-dataset
* **Total Records:** ~45,000 medical Q&A pairs.
* **Processing:** The raw `train.csv` was processed into semantic chunks and embedded using `all-MiniLM-L6-v2` for the RAG pipeline.

⚠️ Disclaimer
Dr. Owl is an AI, not a doctor. The information provided is for educational and informational purposes only. Always consult a qualified healthcare professional for medical advice.