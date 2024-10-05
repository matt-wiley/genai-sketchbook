import os
import sqlite3
from typing import List, Dict, Any, Callable
import importlib
import yaml
import argparse
import logging
from jsonschema import validate

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration schema
config_schema = {
    "type": "object",
    "properties": {
        "embedding": {
            "type": "object",
            "properties": {
                "module": {"type": "string"},
                "function": {"type": "string"},
                "params": {"type": "object"}
            },
            "required": ["module", "function"]
        },
        "database_path": {"type": "string"},
        "input_paths": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        }
    },
    "required": ["embedding", "database_path", "input_paths"]
}

class EmbeddingGenerator:
    def __init__(self, generate_func: Callable[[str], List[float]]):
        self.generate_func = generate_func

    def generate_embedding(self, text: str) -> List[float]:
        return self.generate_func(text)

class EmbeddingFactory:
    @staticmethod
    def create_embedding_generator(config: Dict[str, Any]) -> EmbeddingGenerator:
        module_name = config['module']
        function_name = config['function']
        params = config.get('params', {})

        try:
            module = importlib.import_module(module_name)
            func = getattr(module, function_name)
        except ImportError:
            logger.error(f"Failed to import module: {module_name}")
            raise
        except AttributeError:
            logger.error(f"Function {function_name} not found in module {module_name}")
            raise

        def generate_func(text: str) -> List[float]:
            return func(text, **params)

        return EmbeddingGenerator(generate_func)

class SQLiteStorage:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS embeddings
        (file_path TEXT PRIMARY KEY, embedding BLOB)
        ''')

    def store_embedding(self, file_path: str, embedding: List[float]):
        self.conn.execute('INSERT OR REPLACE INTO embeddings VALUES (?, ?)',
                          (file_path, str(embedding)))
        self.conn.commit()

class EmbeddingProcessor:
    def __init__(self, embedding_generator: EmbeddingGenerator, storage: SQLiteStorage):
        self.embedding_generator = embedding_generator
        self.storage = storage

    def process_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            embedding = self.embedding_generator.generate_embedding(content)
            self.storage.store_embedding(file_path, embedding)
            logger.info(f"Processed: {file_path}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")

    def process_directory(self, directory_path: str):
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.process_file(file_path)

    def process_input(self, input_path: str):
        if os.path.isfile(input_path):
            self.process_file(input_path)
        elif os.path.isdir(input_path):
            self.process_directory(input_path)
        else:
            logger.warning(f"Invalid input path: {input_path}")

def load_config(config_path: str) -> Dict[str, Any]:
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
        validate(instance=config, schema=config_schema)
        return config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {str(e)}")
        raise
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Config validation error: {str(e)}")
        raise

def main(config_path: str):
    try:
        config = load_config(config_path)
        embedding_generator = EmbeddingFactory.create_embedding_generator(config['embedding'])
        storage = SQLiteStorage(config['database_path'])
        processor = EmbeddingProcessor(embedding_generator, storage)

        input_paths = config['input_paths']
        for input_path in input_paths:
            processor.process_input(input_path)
    except Exception as e:
        logger.error(f"An error occurred during execution: {str(e)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and store embeddings based on YAML configuration.")
    parser.add_argument("config", help="Path to the YAML configuration file")
    parser.add_argument("--log", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)", default="INFO")
    args = parser.parse_args()

    logging.getLogger().setLevel(args.log.upper())

    main(args.config)
