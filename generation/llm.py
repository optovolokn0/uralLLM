import subprocess
from config import OLLAMA_MODEL

def generate_text(prompt: str, temperature=0.7) -> str:
    print(f"[DEBUG] generate_text called with temperature={temperature}")
    print(f"[DEBUG] Prompt preview: {prompt[:100]}...")
    print(f"[DEBUG] Calling: ollama run {OLLAMA_MODEL}")
    
    try:
        process = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"[DEBUG] Ollama process returncode: {process.returncode}")

        if process.returncode != 0:
            print(f"[DEBUG] Error from Ollama: {process.stderr}")
            raise RuntimeError(f"Ollama error: {process.stderr}")

        result = process.stdout.strip()
        print(f"[DEBUG] Ollama returned {len(result)} characters")
        return result
    except subprocess.TimeoutExpired:
        print("[DEBUG] ERROR: Ollama process timed out after 300 seconds")
        raise RuntimeError("Ollama generation timed out")
    except FileNotFoundError:
        print("[DEBUG] ERROR: Ollama executable not found. Make sure Ollama is installed and in PATH")
        raise RuntimeError("Ollama not found in PATH")
