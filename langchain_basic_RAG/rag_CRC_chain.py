import os
import sys
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

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

# 5. Create an LLM (set temperature to 0 for deterministic responses)
llm = OpenAI(temperature=0.3) # Set temperature to 0 for deterministic responses,

# 6. Create a ConversationBufferMemory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 7. Create a ConversationalRetrievalChain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory
)

# 8. Function to query the system
def ask_question(question):
    response = qa_chain.invoke({"question": question})
    return response["answer"]

# Example usage
if __name__ == "__main__":
    print("Welcome to the RAG system. Type 'quit' to exit.")
    while True:
        user_question = input("\nEnter your question: ")
        if user_question.lower() == 'quit':
            break
        answer = ask_question(user_question)
        print(f"\nAnswer: {answer}")

print("Thank you for using the RAG system. Goodbye!")