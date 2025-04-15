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
                continue  # skip database-level entries
            table = table_names[table_id]
            schema_lines.setdefault(table, []).append(f"{col_name} {col_type}")

        # Final flat string
        flat_schema = "\n".join([f"{t}({', '.join(cols)})" for t, cols in schema_lines.items()])
        db_schemas[entry["db_id"]] = flat_schema
    return db_schemas

def build_spider_prompt(db_schemas, entry):
    db_id = entry["db_id"]
    question = entry["question"]
    schema_str = db_schemas.get(db_id, "")
    prompt = f"Given the schema:\n{schema_str}\nQuestion: {question}"
    return {
        "prompt": prompt.strip(),
        "output": entry["query"].strip()
    }

def preprocess_spider(train_file, tables_file, output_file):
    with open(train_file, "r") as f:
        entries = json.load(f)

    db_schemas = load_tables_schema(tables_file)
    results = [build_spider_prompt(db_schemas, ex) for ex in entries]

    with open(output_file, "w") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")

    print(f"Preprocessed {len(results)} examples to {output_file}")

if __name__ == "__main__":
    preprocess_spider(
        train_file="data/raw/spider/train_spider.json",
        tables_file="data/raw/spider/tables.json",
        output_file="data/pre_processed/spider_train_preprocessed.jsonl"
    )
