import json
from embeddings.search import search_similar
from generation.validator import validate_vk_post
from generation.prompt_builder import (
    build_structure_prompt,
    build_generation_prompt,
    build_fix_prompt
)
from generation.llm import generate_text


MAX_RETRIES = 3


def generate_vk_post(
    topic: str,
    length: str = "5–8 предложений",
    top_k: int = 5
):

    print("[STEP 1] Generating structure...")
    structure_prompt = build_structure_prompt(topic)
    structure_raw = generate_text(structure_prompt, temperature=0.2)

    try:
        structure = json.loads(structure_raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON from model:\n{structure_raw}")

    print("[DEBUG] Structure parsed")

    required_fields = [
        "squad_name", "event", "post_type",
        "key_actions", "tone", "forbidden_topics"
    ]
    for field in required_fields:
        if field not in structure:
            raise RuntimeError(f"Missing field in structure: {field}")

    print("[STEP 2] Searching similar posts...")
    examples_data = search_similar(text_query=topic, top_k=top_k)
    examples = [item["text"] for item in examples_data]

    print("[STEP 3] Generating post...")
    generation_prompt = build_generation_prompt(
        structure=structure,
        examples=examples,
        length=length
    )

    text = generate_text(generation_prompt)

    for attempt in range(1, MAX_RETRIES + 1):
        soft_errors, hard_errors = validate_vk_post(text, structure)

        if not soft_errors and not hard_errors:
            print(f"[OK] Validation passed on attempt {attempt}")
            return text

        print(f"[WARN] Validation failed (attempt {attempt})")

        if hard_errors:
            print("[REGEN] Hard errors detected:")
            for e in hard_errors:
                print(" -", e)

            regen_prompt = build_generation_prompt(
                structure=structure,
                examples=examples,
                length=length,
                force_rules=True
            )

            text = generate_text(regen_prompt, temperature=0.8)
            continue

        print("[FIX] Soft errors detected:")
        for e in soft_errors:
            print(" -", e)

        fix_prompt = build_fix_prompt(
            original_text=text,
            errors=soft_errors,
            structure=structure
        )

        text = generate_text(fix_prompt, temperature=0.7)

    print("[FAIL] Returning best-effort result")
    return text
