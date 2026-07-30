# chatbot/utils.py
import json
import os
import re
from collections import deque, defaultdict

# --- Basic parser for the simple data.metta format ---
DATA_PAT = re.compile(r'^\(\s*([A-Za-z_]+)\s+([A-Za-z_]+)(?:\s+([A-Za-z_]+))?\s*\)\s*$')

RELATIONS = ["Friend", "Colleague", "Family", "Neighbor", "Classmate"]

# Load file once at import
data_file_path = os.path.join(os.path.dirname(__file__), 'data.metta')


def _parse_data_file(path):
    """
    Parse the simple .metta file into:
      - graph: relation -> {src: set(dests)}
      - attributes: attr_type -> {person: set(values)}
    Ignores commented lines starting with ';' and blank lines.
    """
    graph = {r: defaultdict(set) for r in RELATIONS}
    attributes = defaultdict(lambda: defaultdict(set))

    if not os.path.exists(path):
        raise FileNotFoundError(f"data file not found: {path}")

    with open(path, 'r') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith(';'):
                continue
            m = DATA_PAT.match(line)
            if not m:
                # ignore other lines
                continue
            pred, a, b = m.group(1), m.group(2), m.group(3)
            if pred in RELATIONS and b:
                graph[pred][a].add(b)
            elif b:
                # treat as attribute fact: (Profession Alice Engineer) -> attr_type=Profession, person=Alice, value=Engineer
                attributes[pred][a].add(b)
            else:
                # unmatched pattern (shouldn't happen with our grammar)
                pass

    return graph, attributes


_graph, _attributes = _parse_data_file(data_file_path)


def _normalize_relation_list(relation):
    if relation is None:
        return RELATIONS
    if isinstance(relation, str) and relation.lower() == "any":
        return RELATIONS
    # accept single relation name or list
    if isinstance(relation, str):
        return [relation]
    return list(relation)


def _bfs_find(subject, allowed_relations, attr_type, attr_value, max_depth):
    """
    BFS from subject following only relations in allowed_relations,
    returns dict person -> minimal depth (depths start at 1 for direct neighbors).
    """
    allowed = [r for r in allowed_relations if r in _graph]
    if not allowed:
        return {}

    # visited to avoid revisiting same node at same/greater depth
    seen = {}  # person -> minimal depth seen
    q = deque()

    # seed queue with direct neighbors (depth 1)
    for rel in allowed:
        for dest in _graph[rel].get(subject, []):
            q.append((dest, 1))
            # don't mark seen yet — let processing mark minimal depth

    # BFS
    while q:
        person, depth = q.popleft()
        # if we've already seen this person at an equal or smaller depth, skip
        if person in seen and seen[person] <= depth:
            continue

        # record minimal depth
        seen[person] = depth

        # check attribute match (we will filter by attribute after BFS)
        # but still expand neighbors if depth < max_depth
        if depth < max_depth:
            # expand neighbors via all allowed relations
            for rel in allowed:
                for nxt in _graph[rel].get(person, []):
                    # enqueue for depth+1 if not already seen at smaller depth
                    if nxt not in seen or seen[nxt] > depth + 1:
                        q.append((nxt, depth + 1))

    # Filter seen by attribute type/value
    results = {}
    attr_map = _attributes.get(attr_type, {})
    for person, depth in seen.items():
        vals = attr_map.get(person, set())
        if attr_value in vals:
            results[person] = depth

    return results


def find_by_json(json_input):
    """
    Accepts a JSON string or dict describing the query.
    Returns a list of (person, depth) sorted by depth ascending, then name.
    Example input dict:
      {
        "subject": "Alice",
        "relation": "any",              # or "Family", "Friend", ...
        "target_attribute": {"type":"Profession", "value":"doctor"},
        "max_depth": 2
      }
    """
    if isinstance(json_input, str):
        data = json.loads(json_input)
    else:
        data = json_input

    subject = data["subject"]
    relation = data.get("relation", "any")
    attr_type = data["target_attribute"]["type"]
    attr_value = data["target_attribute"]["value"].strip().title()
    max_depth = int(data.get("max_depth", 1))
    if max_depth < 1:
        raise ValueError("max_depth must be >= 1")

    allowed_relations = _normalize_relation_list(relation)

    found = _bfs_find(subject, allowed_relations, attr_type, attr_value, max_depth)

    # convert to sorted list
    results = sorted(found.items(), key=lambda x: (x[1], x[0]))
    return results


# --- Example usage/tests (run this file as a script) ---
if __name__ == "__main__":
    examples = [
        # depth=1, any Doctor -> Bob and Liam are direct doctors
        {
            "subject": "Alice",
            "relation": "any",
            "target_attribute": {"type": "Profession", "value": "doctor"},
            "max_depth": 1
        },
        # depth=2, any Nurse -> Emma and Karen should be found at depth 2 from Alice
        {
            "subject": "Alice",
            "relation": "any",
            "target_attribute": {"type": "Profession", "value": "nurse"},
            "max_depth": 2
        },
        # depth=3 example (will return depth1/2/3 matches if they exist)
        {
            "subject": "Alice",
            "relation": "any",
            "target_attribute": {"type": "Profession", "value": "nurse"},
            "max_depth": 3
        },
    ]

    for ex in examples:
        print("=== Query ===")
        print(json.dumps(ex, indent=2))
        res = find_by_json(ex)
        print("=> Results (person, depth):", res)
        print()
