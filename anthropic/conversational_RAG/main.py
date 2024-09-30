import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import markdown
import re
from flask import Flask, request, jsonify, render_template_string
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load models
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
chat_model_name = "gpt4" 
chat_tokenizer = AutoTokenizer.from_pretrained(chat_model_name)
chat_model = AutoModelForCausalLM.from_pretrained(chat_model_name)

def preprocess_markdown(text):
    html = markdown.markdown(text)
    text = re.sub('<[^<]+?>', '', html)
    text = ' '.join(text.split())
    return text

def embed_documents(directory):
    embeddings = []
    file_paths = []
    contents = []
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                content = file.read()
            preprocessed_content = preprocess_markdown(content)
            embedding = sentence_model.encode(preprocessed_content)
            embeddings.append(embedding)
            file_paths.append(file_path)
            contents.append(preprocessed_content)
    return np.array(embeddings), file_paths, contents

def search(query, embeddings, file_paths, contents, top_k=5):
    query_embedding = sentence_model.encode(query)
    similarities = cosine_similarity([query_embedding], embeddings)[0]
    top_results = np.argsort(similarities)[-top_k:][::-1]
    return [(file_paths[i], contents[i], similarities[i]) for i in top_results]

def generate_response(prompt, max_length=100):
    input_ids = chat_tokenizer.encode(prompt, return_tensors="pt")
    output = chat_model.generate(input_ids, max_length=max_length, num_return_sequences=1, no_repeat_ngram_size=2)
    return chat_tokenizer.decode(output[0], skip_special_tokens=True)

# Initialize Flask app
app = Flask(__name__)

# Global variables
directory = '/home/matt/repospace/com/github/matt-wiley/genai-sketchbook/.local/output/job_prospects/www_waterx_com'
embeddings, file_paths, contents = embed_documents(directory)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = search(query, embeddings, file_paths, contents)
        
        # Prepare context for the chat model
        context = f"Based on the following information:\n\n"
        for _, content, similarity in results:
            context += f"{content[:200]}...\n\n"
        context += f"Question: {query}\n\nAnswer:"
        
        # Generate response using the chat model
        response = generate_response(context)
        
        return render_template_string('''
            <h1>Research Assistant</h1>
            <form method="post">
                <input type="text" name="query" value="{{ query }}">
                <input type="submit" value="Ask">
            </form>
            <h2>Response:</h2>
            <p>{{ response }}</p>
            <h2>Relevant Documents:</h2>
            {% for file_path, _, similarity in results %}
                <p>{{ file_path }} (Similarity: {{ similarity:.4f }})</p>
            {% endfor %}
        ''', query=query, response=response, results=results)
    return render_template_string('''
        <h1>Research Assistant</h1>
        <form method="post">
            <input type="text" name="query">
            <input type="submit" value="Ask">
        </form>
    ''')

if __name__ == '__main__':
    app.run(debug=True)