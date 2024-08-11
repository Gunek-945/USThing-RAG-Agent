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

load_dotenv()

# Prompt
template = """
You are an assistant for question-answering tasks for The Hong Kong University of Science and Technology.
Use the following pieces of retrieved context to answer the question. If you don't know the answer, your response should be only and only "I don't know".
You also have to cater to the user's emotional requirement while answering. Below you will find three emotions- Humor, Rudeness and Flirtiness with a score ranging 
from (0-10). As the number gets closer to 10, your answer catering to that particular emotion should also increase. For example, Humour-10 would mean that you have to joke
around a lot and make the conversation funnier and engaging while answering. Make sure to fully get into that emotion and do the most of it. DO NOT SHOW THE MOOD SCORES IN THE RESPONSE.

Also give the source from where you have retrieved the information (give the website link).. NOTE: THE SOURCE CANNOT BE OF .txt format if you don't know the source simply say ONLY and ONLY "why u no trust me". 

Humour: {humour}
Rudeness: {rudeness}
Flirtiness: {flirtiness}

Context: {context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

# LLM Chain
llm = ChatGroq(temperature=0.2, groq_api_key="ENTER_API_KEY", model="llama3-70b-8192")

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
    'data/student_organizations.txt'
]

documents = load_and_split_documents(file_paths)

embeddings = HuggingFaceEmbeddings()

# Create or load the Pinecone vector store
index_name = "usthing-rag-index"
vectorstore = Pinecone.from_documents(documents, embeddings, index_name=index_name)
retriever = vectorstore.as_retriever()

# Prompt-based Chain
rag_chain = prompt | llm | StrOutputParser()

# Prompt the user for random or specific mood
mood = input("Enter 'random' for a random mood or 'specific' for a specific mood: ")

# if mood.lower() == "random":
#     humour_score = random.randint(1, 10)
#     rudeness_score = random.randint(1, 10)
#     flirtiness_score = random.randint(1, 10)
# else:
#     humour_score = int(input("Enter humour score (1-10): "))
#     rudeness_score = int(input("Enter rudeness score (1-10): "))
#     flirtiness_score = int(input("Enter flirtiness score (1-10): "))

with open("Approach3.txt", "a") as f:
    while True:
        if mood.lower() == "random":
            humour_score = random.randint(1, 10)
            rudeness_score = random.randint(1, 10)
            flirtiness_score = random.randint(1, 10)
        else:
            humour_score = int(input("Enter humour score (1-10): "))
            rudeness_score = int(input("Enter rudeness score (1-10): "))
            flirtiness_score = int(input("Enter flirtiness score (1-10): "))
        
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break

        start_time = time.time()
        docs = retriever.invoke(user_input)
        generation = rag_chain.invoke({"question": user_input, "context": docs, "humour": humour_score, "rudeness": rudeness_score, "flirtiness": flirtiness_score})
        end_time = time.time()
        response_time = end_time - start_time
        f.write(f"Humour: {humour_score}\n")
        f.write(f"Rudeness:{rudeness_score}\n")
        f.write(f"Flirtiness: {flirtiness_score}\n")
        f.write(f"User: {user_input}\n")
        f.write(f"Assistant: {generation}\n")
        f.write(f"Response time: {response_time:.2f} seconds\n\n")
        print(f"Assistant: {generation}")
