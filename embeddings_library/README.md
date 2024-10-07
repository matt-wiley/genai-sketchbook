# Embedding Generation and Storage System

## Overview
This project provides a flexible system for generating and storing text embeddings. It's designed to support various embedding models and efficient similarity search, making it suitable for Retrieval-Augmented Generation (RAG) systems.

Key features:
- Configurable embedding generation using a factory pattern
- YAML configuration with JSON schema validation
- Efficient storage and retrieval using FAISS (Facebook AI Similarity Search)
- Support for processing multiple input paths (files and directories)
  - Support document types: txt, markdown, PDF
- Extensible architecture for easy addition of new embedding models

## Getting Started

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```
   git clone [your-repo-url]
   cd [your-repo-name]
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Configuration

1. Copy `config.example.yaml` to `config.yaml`
2. Modify `config.yaml` to suit your needs:
   - Set input paths
   - Choose embedding function
   - Configure FAISS storage

### Running the System

Execute the main script:
```
python embeddings_generator.py --config config.yaml
```

## External Dependencies

- PyYAML: YAML file parsing
- jsonschema: JSON schema validation
- faiss-cpu: Efficient similarity search
- scikit-learn: TF-IDF embedding generation
- numpy: Numerical operations
- PyPDF2: PDF file processing

## Adding New Embedding Functions

1. Create a new Python file (e.g., `new_embedding.py`) in the project directory.
2. Define your embedding function:

   ```python
   def generate_new_embedding(text, param1, param2):
       # Your embedding logic here
       return embedding_vector
   ```

3. Update `config.yaml`:

   ```yaml
   embedding:
     module: "new_embedding"
     function: "generate_new_embedding"
     params:
       param1: value1
       param2: value2
   ```

4. The system will automatically load and use your new function.

## Project Structure

- `embeddings_generator.py`: Main script
- `faiss_storage.py`: FAISS-based storage module
- `tfidf_embeddings.py`: Example embedding function
- `config.yaml`: Configuration file
- `config_schema.json`: JSON schema for config validation

## Logging

The system logs information and errors to `embedding_generator.log`.

## Contributing

[Add your contribution guidelines here]

## License

[Specify your project's license]
