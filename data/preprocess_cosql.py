import json

def load_tables_schema(tables_file):
    with open(tables_file, "r") as f:
        data = json.load(f)

    db_schemas = {}
    for entry in data:
        table_names = entry["table_names_original"]
        columns = entry["column_names_original"]
        column_types = entry["column_types"]

        schema_lines = {}
        for (table_id, col_name), col_type in zip(columns, column_types):
            if table_id == -1:
                continue
            table = table_names[table_id]
            schema_lines.setdefault(table, []).append(f"{col_name} {col_type}")

        flat_schema = "\n".join([f"{t}({', '.join(cols)})" for t, cols in schema_lines.items()])
        db_schemas[entry["db_id"]] = flat_schema
    return db_schemas

def extract_dialog_prompts(data, db_schemas):
    all_examples = []

    for dialog in data.values():
        db_id = dialog["db_id"]
        schema = db_schemas.get(db_id, "")
        turns = dialog["turns"]

        context = []
        for turn in turns:
            if turn.get("isUser", False):
                context.append(f"User: {turn['text'].strip()}")
            elif turn.get("isSql", False) and "rawSql" in turn:
                prompt = f"Given the schema:\n{schema}\nDialogue:\n" + "\n".join(context)
                output = turn["rawSql"].strip()
                all_examples.append({
                    "prompt": prompt.strip(),
                    "output": output
                })
    return all_examples

def preprocess_cosql(cosql_file, tables_file, output_file):
    with open(cosql_file, "r") as f:
        dialogs = json.load(f)

    db_schemas = load_tables_schema(tables_file)
    prompts = extract_dialog_prompts(dialogs, db_schemas)

    with open(output_file, "w") as f:
        for item in prompts:
            f.write(json.dumps(item) + "\n")

    print(f"Processed {len(prompts)} examples into {output_file}")


if __name__ == "__main__":
    preprocess_cosql(
        cosql_file="data/raw/cosql/cosql_all_info_dialogs.json",
        tables_file="data/raw/cosql/tables.json",
        output_file="data/pre_processed/cosql_preprocessed.jsonl"
    )
