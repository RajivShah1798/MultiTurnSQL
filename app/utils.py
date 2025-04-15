import json
import os

def save_schema_to_json(schema: dict, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(schema, f, indent=2)