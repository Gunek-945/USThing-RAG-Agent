import os
import time
import random
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_API_ENV = os.getenv("PINECONE_API_ENV")
GROQ_API_KEY= os.getenv("GROQ_API_KEY")

# Prompt
template = """
You are an assistant for question-answering tasks for The Hong Kong University of Science and Technology.
Use the following pieces of retrieved context to answer the question. If you don't know the answer, your response should be only and only "I don't know".
You also have to cater to the user's emotional requirement while answering. Below you will find the emotion state the user has requested with a corresponding description. Make sure to fully get into that emotion and do the most of it. DO NOT SHOW THE MOOD SCORES IN THE RESPONSE.

Also give the source from where you have retrieved the information (give the website link).. NOTE: THE SOURCE CANNOT BE OF .txt format if you don't know the source simply say ONLY and ONLY "why u no trust me". 

Humour: {humour}
Rudeness: {rudeness}
Flirtiness: {flirtiness}

Context: {context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# LLM Chain
llm = ChatGroq(temperature=0.2, groq_api_key=GROQ_API_KEY, model="llama3-70b-8192")

def load_and_split_documents(file_paths):
    documents = []
    for file_path in file_paths:
        loader = TextLoader(file_path, encoding='utf-8')
        text_documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        documents.extend(text_splitter.split_documents(text_documents))
    return documents

file_paths = [
    'data/Academic regulations.txt',
    'data/student_organizations.txt',
    'data/Faculty/Department of Chemistry.txt',
    'data/Faculty/Department of Mathematics.txt',
    'data/Faculty/Department of Ocean Science.txt',
    'data/Faculty/Department of Physics.txt'
]

documents = load_and_split_documents(file_paths)

embeddings = HuggingFaceEmbeddings()

# Create or load the Pinecone vector store with namespaces
index_name = "usthing-rag-index"
namespaces = {
    "academic": ["data/Academic regulations.txt"],
    "student_life": ["data/student_organizations.txt"],
    "faculty": [
        "data/Faculty/Department of Chemistry.txt",
        "data/Faculty/Department of Mathematics.txt",
        "data/Faculty/Department of Ocean Science.txt",
        "data/Faculty/Department of Physics.txt"
    ]
}

vectorstore = Pinecone.from_documents(documents, embeddings, index_name=index_name)

# Create namespace-specific vectorstores
for namespace, files in namespaces.items():
    namespace_docs = load_and_split_documents(files)
    vectorstore.add_documents(namespace_docs, namespace=namespace)

retriever = vectorstore.as_retriever()

# Prompt-based Chain
rag_chain = prompt | llm | StrOutputParser()

def get_user_input():
    user_input = input("User: ")
    return user_input

def get_namespace_choice():
    print("\nWhat topic is your question related to?")
    print("1. Academic")
    print("2. Student Life")
    print("3. Faculty")
    print("4. All topics")
    choice = input("Enter your choice (1-4): ")
    if choice == '1':
        return "academic"
    elif choice == '2':
        return "student_life"
    elif choice == '3':
        return "faculty"
    else:
        return None

def get_mood_parameters():
    print("\nSet mood parameters (1-10):")
    humour = int(input("Humour score (1-10): "))
    rudeness = int(input("Rudeness score (1-10): "))
    flirtiness = int(input("Flirtiness score (1-10): "))
    return humour, rudeness, flirtiness

def generate_response(user_input, namespace=None, humour_score=5, rudeness_score=1, flirtiness_score=1):
    if namespace:
        docs = vectorstore.similarity_search(user_input, namespace=namespace)
    else:
        docs = retriever.invoke(user_input)
    
    generation = rag_chain.invoke({
        "question": user_input,
        "context": docs,
        "humour": humour_score,
        "rudeness": rudeness_score,
        "flirtiness": flirtiness_score
    })
    return generation

def main():
    print("Welcome to the HKUST RAG Agent!")
    mood = input("Enter 'random' for random mood or 'specific' for specific mood: ").lower()
    
    while True:
        user_input = get_user_input()
        if user_input.lower() == "exit":
            break

        if mood == "random":
            humour_score = random.randint(1, 10)
            rudeness_score = random.randint(1, 10)
            flirtiness_score = random.randint(1, 10)
        else:
            humour_score, rudeness_score, flirtiness_score = get_mood_parameters()

        namespace = None
        response = generate_response(user_input, namespace, humour_score, rudeness_score, flirtiness_score)
        print(f"Assistant: {response}")

        if "I don't know" in response:
            print("\nI apologize, but I couldn't provide an accurate answer. Let's try to narrow down the topic.")
            namespace = get_namespace_choice()
            if namespace:
                response = generate_response(user_input, namespace, humour_score, rudeness_score, flirtiness_score)
                print(f"Assistant: {response}")

        print("\n")

if __name__ == "__main__":
    main()
