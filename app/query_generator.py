from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import textwrap

class SQLQueryGenerator:
    def __init__(self, model_name="Salesforce/codet5-small"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.generator = pipeline("text2text-generation", 
                                  model=self.model, tokenizer=self.tokenizer)
        
    def generate_prompt(self, user_input, schema=None, chat_history=None):
        schema_str = "\n".join([
            f"TABLE {table}:\n" + ", ".join([col['name'] + " " + col['type'] for col in meta['columns']])
            for table, meta in schema.items()
        ]) if schema else ""
        
        history_str = "\n".join([f"User: {turn['user']}\nSQL: {turn['sql']}" for turn in chat_history]) if chat_history else ""
        prompt = textwrap.dedent(f"""
            You are an assistant that converts natural language to SQL queries.
            The database schema is:
            {schema_str}

            {history_str}
            User question: {user_input}

            Generate a SQL query to answer the user question.
        """)
        return prompt.strip()
    
    def generate_query(self, user_input, schema=None, chat_history=None, max_tokens=128):
        prompt = self.generate_prompt(user_input, schema, chat_history)
        output = self.generator(prompt, max_length=max_tokens, do_sample=False)[0]["generated_text"]
        return output.strip()
    
    
if __name__ == "__main__":
    import json

    with open("data/demo_retail_schema_extract.json") as f:
        schema = json.load(f)

    generator = SQLQueryGenerator(model_name="Salesforce/codet5-base")
    
    user_input = "Get names and emails of all customers"
    sql = generator.generate_query(user_input, schema)
    
    print("Generated SQL:\n", sql)
        
        