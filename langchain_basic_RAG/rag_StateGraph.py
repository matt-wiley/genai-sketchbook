import os
import sys
import uuid
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

# 1. Load Markdown files from a directory
loader = DirectoryLoader(DOCUMENTS_DIR, glob="**/*.md")
documents = loader.load()

# 2. Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# 3. Create embeddings and store in vector database
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(texts, embeddings)

# 4. Create a retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 5. Create an LLM (Claude)
model = OpenAI(temperature=0)

# 6. Define the LangGraph workflow
workflow = StateGraph(state_schema=MessagesState)

# 7. Define the function that calls the model and retriever
def call_rag(state: MessagesState):
    human_message = state["messages"][-1]
    context = retriever.invoke(human_message.content)
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

# 10. Function to interact with the RAG system
def ask_question(question, thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    input_message = HumanMessage(content=question)
    
    for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
        response = event["messages"][-1].content
    
    return response

# Example usage
if __name__ == "__main__":
    print("Welcome to the LangGraph RAG system. Type 'quit' to exit.")
    
    # Create a unique thread ID for this conversation
    thread_id = str(uuid.uuid4())
    
    while True:
        user_question = input("\nEnter your question: ")
        if user_question.lower() == 'quit':
            break
        
        answer = ask_question(user_question, thread_id)
        print(f"\nAnswer: {answer}")

print("Thank you for using the LangGraph RAG system. Goodbye!")