import subprocess
import sys
import os

REQUIRED_MODELS = ["llama3.2:1b", "moondream"]

def check_and_install_models():
    print("🔍 Checking system requirements...")
    
    # 1. Check if Ollama is installed on the computer
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        print("❌ CRITICAL ERROR: Ollama is not installed on this computer!")
        print("💡 Please download and install it from https://ollama.com")
        sys.exit(1)

    # 2. Check for required models
    installed_models = result.stdout
    for model in REQUIRED_MODELS:
        if model in installed_models:
            print(f"✅ Model '{model}' is already installed.")
        else:
            print(f"⏳ Model '{model}' is missing. Downloading now (this may take a few minutes)...")
            subprocess.run(['ollama', 'pull', model], check=True)
            print(f"🎉 Successfully downloaded '{model}'.")

    print("\n🚀 All systems go! Starting the backend server...")
    
    # 3. Start your backend API here (We will build this in Step 2)
    # os.system("uvicorn api:app --reload")

if __name__ == "__main__":
    print("--- Medical RAG Auto-Setup ---")
    check_and_install_models()