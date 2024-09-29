import os
import sys
import uuid
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph

for i in ["OPENAI_API_KEY", "DOCUMENTS_DIR"]:
    if os.getenv(i) is None:
        raise ValueError(f"{i} environment variable must be set")
        sys.exit(1)

DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", None)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
BASE_K_RETRIEVAL = 6
TEMPERATURE = 0.5
MAX_TOKENS = 500


print("----------------------------------")

# 1. Load Markdown files from a directory

print(f"Loading documents from {DOCUMENTS_DIR}... ", end="")

start = time.time()
loader = DirectoryLoader(DOCUMENTS_DIR, glob="**/*.md")
documents = loader.load()
end = time.time()

print(f"done. {len(documents)} documents loaded in {end - start:.2f} seconds.")


# 2. Split documents into chunks

print("Splitting documents into chunks... ", end="")

start = time.time()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
texts = text_splitter.split_documents(documents)
end = time.time()

print(f"done. {len(texts)} text chunks created in {end - start:.2f} seconds.")

# 3. Create embeddings and store in vector database

print("Creating embeddings and storing in vector database... ", end="")
start = time.time()

embeddings = OpenAIEmbeddings()

# Calculate average vector of the document corpus
doc_vectors = [embeddings.embed_query(doc.page_content) for doc in texts]
average_vector = np.mean(doc_vectors, axis=0)

vectorstore = Chroma.from_documents(texts, embeddings)

end = time.time()
print(f"done. {len(texts)} vectors stored in vector database in {end - start:.2f} seconds.")


# 4. Create an adaptive retriever
def calculate_query_specificity(query, embeddings, average_vector):
    query_vector = embeddings.embed_query(query)
    similarity = cosine_similarity([query_vector], [average_vector])[0][0]
    specificity = 1 - similarity
    return specificity

def adaptive_retriever(query):
    specificity = calculate_query_specificity(query, embeddings, average_vector)
    adjusted_k = max(1, min(20, int(BASE_K_RETRIEVAL * (1 + specificity))))
    return vectorstore.similarity_search(query, k=adjusted_k)

print("Creating the RAG system ...", end="")
start = time.time()

# 5. Create an LLM (OpenAI)
model = OpenAI(temperature=TEMPERATURE, max_tokens=MAX_TOKENS)

# 6. Define the LangGraph workflow
workflow = StateGraph(state_schema=MessagesState)

# 7. Define the function that calls the model and retriever
def call_rag(state: MessagesState):
    human_message = state["messages"][-1]
    context = adaptive_retriever(human_message.content)
    context_str = "\n".join(doc.page_content for doc in context)
    
    messages = [
        HumanMessage(content=f"Context: {context_str}\n\nHuman: {human_message.content}")
    ]
    response = model.invoke(messages)
    
    return {"messages": [response]}

# 8. Define the graph structure
workflow.add_node("rag", call_rag)
workflow.add_edge(START, "rag")
workflow.add_edge("rag", END)

# 9. Compile the graph with memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

end = time.time()
print(f"done. RAG system created in {end - start:.2f} seconds.")
print("----------------------------------")

# 10. Function to interact with the RAG system
def ask_question(question, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    input_message = HumanMessage(content=question)
    
    for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
        response = event["messages"][-1].content
    
    return response

# Example usage
if __name__ == "__main__":
    print("Welcome to the Adaptive LangGraph RAG system. Type 'quit' to exit.")
    
    # Create a unique thread ID for this conversation
    thread_id = str(uuid.uuid4())
    
    while True:
        user_question = input("\nEnter your question: ")
        if user_question.lower() == 'quit':
            break
        
        answer = ask_question(user_question, thread_id)
        print(f"\nAnswer: {answer}")

print("Thank you for using the Adaptive LangGraph RAG system. Goodbye!")