import sqlparse
from sqlparse.sql import Identifier, Parenthesis
from sqlparse.tokens import Keyword

from utils import save_schema_to_json

def is_create_table(statement):
    return statement.get_type() == 'CREATE'

def extract_columns_and_constraints(token):
    columns = []
    constraints = []

    if isinstance(token, Parenthesis):
        raw_defs = token.value.strip('()').split(',')

        for raw_def in raw_defs:
            line = raw_def.strip()

            if not line:
                continue

            if line.upper().startswith("PRIMARY KEY") or line.upper().startswith("FOREIGN KEY"):
                constraints.append(line)
                continue

            parts = line.split()
            if len(parts) >= 2:
                col_name = parts[0]
                col_type = parts[1]
                col_constraints = ' '.join(parts[2:]) if len(parts) > 2 else ''
                columns.append({
                    "name": col_name,
                    "type": col_type,
                    "constraints": col_constraints
                })

    return columns, constraints

def parse_schema(sql_text):
    parsed = sqlparse.parse(sql_text)
    schema = {}

    for stmt in parsed:
        if is_create_table(stmt):
            tokens = [t for t in stmt.tokens if not t.is_whitespace]
            table_name = None
            column_info = []
            table_constraints = []

            for i, token in enumerate(tokens):
                if token.ttype is Keyword and token.value.upper() == "TABLE":
                    table_token = tokens[i + 1]
                    table_name = table_token.get_name() if isinstance(table_token, Identifier) else table_token.value
                elif isinstance(token, Parenthesis):
                    column_info, table_constraints = extract_columns_and_constraints(token)

            if table_name:
                schema[table_name] = {
                    "columns": column_info,
                    "constraints": table_constraints
                }

    return schema


if __name__ == "__main__":
    with open("data/demo_retail_schema.sql", "r") as f:
        sql_text = f.read()

    parsed_schema = parse_schema(sql_text)
    save_schema_to_json(parsed_schema, "data/demo_retail_schema_extract.json")
    print(parsed_schema)