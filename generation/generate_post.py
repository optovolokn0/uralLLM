import json
import re
from embeddings.search import search_similar
from generation.validator import validate_vk_post
from generation.prompt_builder import (
    build_structure_prompt,
    build_generation_prompt,
    build_fix_prompt
)
from generation.llm import generate_text


MAX_RETRIES = 3


def _extract_json_payload(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        raise RuntimeError("Model returned empty response for structure JSON")

    # Remove markdown fences if model wrapped JSON in ```json ... ```
    if "```" in text:
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    # If there is any extra prose around JSON, extract first object block.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError(f"Model response does not contain JSON object:\n{text}")

    return text[start:end + 1]


def _normalize_structure(structure: dict) -> dict:
    if "season_or_date" not in structure and "season" in structure:
        structure["season_or_date"] = structure.get("season")

    defaults = {
        "squad_name": "ССО «Урал»",
        "event": "Событие отряда",
        "post_type": "отчет",
        "key_actions": [],
        "tone": "тёплый",
        "forbidden_topics": [],
    }

    for key, value in defaults.items():
        if key not in structure or structure[key] in (None, ""):
            structure[key] = value

    if not isinstance(structure["key_actions"], list):
        structure["key_actions"] = [str(structure["key_actions"])]

    if not isinstance(structure["forbidden_topics"], list):
        structure["forbidden_topics"] = [str(structure["forbidden_topics"])]

    return structure


def generate_vk_post(
    topic: str,
    length: str = "5–8 предложений",
    top_k: int = 5
):

    print("[STEP 1] Generating structure...")
    structure_prompt = build_structure_prompt(topic)
    structure_raw = generate_text(structure_prompt, temperature=0.2)

    try:
        structure_json = _extract_json_payload(structure_raw)
        structure = json.loads(structure_json)
    except Exception as exc:
        raise RuntimeError(f"Invalid JSON from model:\n{structure_raw}") from exc

    structure = _normalize_structure(structure)
    print("[DEBUG] Structure parsed")

    print("[STEP 2] Searching similar posts...")
    examples = search_similar(text_query=topic, top_k=top_k)

    if not examples:
        print("[WARN] RAG context not found, generating without archive examples")
        examples = [{"score": 0.0, "text": "Контекст не найден. Пиши по теме запроса без ссылок на конкретные прошлые посты."}]

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
