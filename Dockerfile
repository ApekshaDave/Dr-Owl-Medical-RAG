# Use a lightweight Python image
FROM python:3.10-slim

# Install system dependencies (needed for FAISS and general stability)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set up a new user 'user' with UID 1000 (Required by Hugging Face)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

# Set the working directory
WORKDIR /home/user/app

# Copy requirements first to leverage Docker cache
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the rest of your backend files
# (This includes api.py, chunks.npy, faiss_index.bin, etc.)
COPY --chown=user . .

# Hugging Face Spaces uses port 7860 by default
EXPOSE 7860

# Start the FastAPI app
# We use 'api:app' because your file is named api.py
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]