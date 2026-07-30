# parser.py (compact, attempts only allowed shapes)
import os, json, re
from dotenv import load_dotenv
import google.generativeai as genai
import inspect

load_dotenv()
KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.metta")

# try model object
MODEL = None
MODEL_IS_OBJ = False
if KEY:
    genai.configure(api_key=KEY)
    try:
        MODEL = genai.GenerativeModel(MODEL_NAME)
        MODEL_IS_OBJ = True
    except Exception:
        MODEL = "models/text-bison-001"

SCHEMA = ('Reply with ONLY one JSON object like: '
          '{"subject":<string|null>,"relation":"any"|"Friend"|"Colleague"|"Family"|"Neighbor"|"Classmate",'
          '"target_attribute":{"type":"Profession"|"Hobby","value":"<string>"},"max_depth":<int>}')

RELATIONS = ["Friend", "Colleague", "Family", "Neighbor", "Classmate"]
ATTRIBUTE_TYPES = ["Profession", "Hobby"]


def _load_known_terms():
    known_people = set()
    known_attributes = {attr_type: set() for attr_type in ATTRIBUTE_TYPES}

    if not os.path.exists(DATA_FILE):
        return known_people, known_attributes

    with open(DATA_FILE, "r") as f:
        for raw_line in f:
            match = re.match(r"^\(\s*([A-Za-z_]+)\s+([A-Za-z_]+)\s+([A-Za-z_]+)\s*\)", raw_line.strip())
            if not match:
                continue

            predicate, first, second = match.groups()
            if predicate in RELATIONS:
                known_people.update([first, second])
            elif predicate in ATTRIBUTE_TYPES:
                known_people.add(first)
                known_attributes[predicate].add(second)

    return known_people, known_attributes


KNOWN_PEOPLE, KNOWN_ATTRIBUTES = _load_known_terms()


def _find_known_value(text, values):
    matches = []
    for value in values:
        match = re.search(rf"\b{re.escape(value.lower())}\b", text)
        if match:
            matches.append((match.start(), value))
    if not matches:
        return None
    return sorted(matches)[0][1]


def _extract_max_depth(text):
    match = re.search(r"(?:within|up to|max(?:imum)? depth|depth|hops?)\D*(\d+)", text)
    if match:
        return max(1, min(5, int(match.group(1))))
    if any(word in text for word in ("direct", "close", "immediate")):
        return 1
    return 2


def _parse_question_locally(q, assumed_subject=None):
    text = q.lower()

    relation = "any"
    for rel in RELATIONS:
        rel_text = rel.lower()
        if re.search(rf"\b{rel_text}s?\b", text):
            relation = rel
            break

    subject = _find_known_value(text, KNOWN_PEOPLE) or assumed_subject

    if not subject:
        return None

    profession = _find_known_value(text, KNOWN_ATTRIBUTES["Profession"])
    hobby = _find_known_value(text, KNOWN_ATTRIBUTES["Hobby"])

    if "hobby" in text or "play" in text:
        attr_type, attr_value = "Hobby", hobby
    else:
        attr_type, attr_value = "Profession", profession or hobby
        if hobby and not profession:
            attr_type = "Hobby"

    if not attr_value:
        return None

    return {
        "subject": subject,
        "relation": relation,
        "target_attribute": {"type": attr_type, "value": attr_value},
        "max_depth": _extract_max_depth(text),
    }

def _call(prompt):
    last = None
    if not KEY:
        raise RuntimeError("GEMINI_API_KEY missing and the local parser could not understand this question")

    if MODEL_IS_OBJ:
        try:
            return MODEL.generate_content(prompt)
        except Exception as e:
            raise RuntimeError(f"Gemini generateContent failed for model {MODEL_NAME}: {e}") from e

    # fallback to function API if present
    if hasattr(genai, "generate_text"):
        text_model = MODEL if isinstance(MODEL, str) else MODEL_NAME
        for kwargs in (
            {"model": text_model, "prompt": prompt},
            {"model": text_model, "input": prompt},
        ):
            try:
                return genai.generate_text(**kwargs)
            except Exception as e:
                last = e
                continue

    raise RuntimeError("All call shapes failed. Last error: " + (str(last) if last else "none"))

def _txt(resp):
    if hasattr(resp, "candidates") and resp.candidates:
        c = resp.candidates[0]
        content = getattr(c, "content", None)
        if isinstance(content, str):
            return content
        if isinstance(content, (list, tuple)) and content:
            first = content[0]
            if isinstance(first, dict):
                return first.get("text") or first.get("content") or json.dumps(first)
            return getattr(first, "text", str(first))
    if hasattr(resp, "text"):
        return resp.text
    return str(resp)

def parse_question_to_json(q, assumed_subject):
    if not q or not q.strip():
        raise ValueError("Empty question")
    parsed = _parse_question_locally(q, assumed_subject=assumed_subject)
    if parsed:
        return parsed

    prompt = SCHEMA + "\n\nUser question: " + (f"(Assume subject: {assumed_subject}) " if assumed_subject else "") + q.strip()
    resp = _call(prompt)
    text = _txt(resp).strip()
    i, j = text.find("{"), text.rfind("}")
    if i == -1 or j == -1 or j <= i:
        raise ValueError("No JSON in model output:\n" + text)
    parsed = json.loads(text[i:j+1])
    parsed["subject"] = parsed.get("subject") or assumed_subject
    parsed["max_depth"] = max(1, min(5, int(parsed.get("max_depth", 1))))
    return parsed

if __name__ == "__main__":
    tests = [
        "Do I have Family who is a doctor in my network?",
        "Is there a nurse within 2 hops from me?"
    ]
    for q in tests:
        print("Q:", q)
        try:
            print(json.dumps(parse_question_to_json(q, assumed_subject="Alice"), indent=2))
        except Exception as e:
            print("Error:", e)
            # helpful debug: show generate_content signature if object exists
            if MODEL_IS_OBJ and hasattr(MODEL, "generate_content"):
                print("generate_content signature:", inspect.signature(MODEL.generate_content))
            if MODEL_IS_OBJ and hasattr(MODEL, "start_chat"):
                print("start_chat signature:", inspect.signature(MODEL.start_chat))
