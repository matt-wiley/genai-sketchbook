import os
import sys
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA


for i in ["OPENAI_API_KEY", "DOCUMENTS_DIR"]:
    if os.getenv(i) is None:
        raise ValueError(f"{i} environment variable must be set")
        sys.exit(1)

DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", None)

# 1. Load Markdown files from a directory
loader = DirectoryLoader(DOCUMENTS_DIR , glob="**/*.md")
documents = loader.load()

# 2. Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# 3. Create embeddings and store in vector database
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(texts, embeddings)

# 4. Create a retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 5. Create an LLM
llm = OpenAI(temperature=0)

# 6. Create a chain that uses the retriever and LLM
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
)

# 7. Function to query the system
def ask_question(question):
    response = qa_chain.invoke({"query": question})
    return response["result"]

# Example usage
if __name__ == "__main__":
    while True:
        user_question = input("Enter your question (or 'quit' to exit): ")
        if user_question.lower() == 'quit':
            break
        answer = ask_question(user_question)
        print(f"\nAnswer: {answer}\n")