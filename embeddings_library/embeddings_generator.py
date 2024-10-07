import os
from typing import List, Dict, Any, Callable
import importlib
import yaml
import argparse
import logging
from logging.handlers import RotatingFileHandler
import PyPDF2

from jsonschema import validate
from faiss_storage import FAISSStorage


# Update the logging setup
log_file = 'embedding_generator.log'
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# Configuration schema
config_schema = {
    "type": "object",
    "properties": {
        "faiss_index_path": {"type": "string"},
        "embedding_dimension": {"type": "integer"},
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
    "required": ["embedding", "faiss_index_path", "embedding_dimension", "input_paths"]
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


class EmbeddingProcessor:
    def __init__(self, embedding_generator: EmbeddingGenerator, storage: FAISSStorage):
        self.embedding_generator = embedding_generator
        self.storage = storage

    def process_input(self, input_path: str):
        if os.path.isfile(input_path):
            self.process_file(input_path)
        elif os.path.isdir(input_path):
            for root, _, files in os.walk(input_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.process_file(file_path)
        else:
            logger.warning(f"Invalid input path: {input_path}")

    def process_file(self, file_path: str):
        try:
            if file_path.lower().endswith('.pdf'):
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    content = ' '.join(page.extract_text() for page in reader.pages)
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
        
            embedding = self.embedding_generator.generate_embedding(content)
            self.storage.store_embedding(file_path, embedding)
            logger.info(f"Processed: {file_path}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")


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
        storage = FAISSStorage(config['faiss_index_path'], config['embedding_dimension'])
        processor = EmbeddingProcessor(embedding_generator, storage)

        input_paths = config['input_paths']
        for input_path in input_paths:
            processor.process_input(input_path)
        
        logger.info(f"Total embeddings stored: {len(storage)}")
    except Exception as e:
        logger.error(f"An error occurred during execution: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and store embeddings based on YAML configuration.")
    parser.add_argument("config", help="Path to the YAML configuration file")
    parser.add_argument("--log", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)", default="INFO")
    args = parser.parse_args()

    logger.setLevel(args.log.upper())

    main(args.config)
