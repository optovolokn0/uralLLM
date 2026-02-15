from huggingface_hub import InferenceClient
from config import HUGGINGFACE_API_KEY, HUGGINGFACE_MODEL

SYSTEM_PROMPT = (
    "Ты пишешь посты для VK на русском языке. "
    "Следуй инструкциям строго, не добавляй служебные блоки и комментарии о правилах."
)


def generate_text(prompt: str, temperature=0.6) -> str:
    print(f"[DEBUG] generate_text called with temperature={temperature}")
    print(f"[DEBUG] Prompt preview: {prompt[:100]}...")
    print(f"[DEBUG] Calling Hugging Face API with model: {HUGGINGFACE_MODEL}")

    if not HUGGINGFACE_API_KEY:
        raise RuntimeError("HUGGINGFACE_API_KEY not found in environment variables. Please set it in your .env file.")

    try:
        client = InferenceClient(api_key=HUGGINGFACE_API_KEY)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        response = client.chat_completion(
            model=HUGGINGFACE_MODEL,
            messages=messages,
            max_tokens=700,
            temperature=temperature,
            top_p=0.9,
        )

        result = response.choices[0].message.content
        print(f"[DEBUG] Hugging Face returned {len(result)} characters")
        return result
    except Exception as e:
        print(f"[DEBUG] ERROR: Hugging Face API failed: {e}")
        raise RuntimeError(f"Hugging Face generation failed: {e}")
