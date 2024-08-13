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

with open("Approach4.txt", "a") as f:
    while True:
        mood_input = int(input("Enter 1 for Humor, 2 for Rudeness, or 3 for Flirtiness: "))
        rudeness_desc = "Not Rude"
        flirtiness_desc = "Not Flirty"
        humour_desc= "Not funny"
        if mood_input == 1:
            humour_score = int(input("Enter humor score (1-3): "))
            if humour_score == 1:
                humour_desc = "Try to be a bit funny."
            elif humour_score == 2:
                humour_desc = "Try to be decently funny, not too little, not too much."
            else:
                humour_desc = "Try to be very funny."
            rudeness_score = 0
            flirtiness_score = 0
        elif mood_input == 2:
            humour_score = 0
            rudeness_score = int(input("Enter rudeness score (1-3): "))
            if rudeness_score == 1:
                rudeness_desc = "Try to be a bit rude."
            elif rudeness_score == 2:
                rudeness_desc = "Try to be decently rude, not too little, not too much."
            else:
                rudeness_desc = "Try to be very rude."
            flirtiness_score = 0
        elif mood_input == 3:
            humour_score = 0
            rudeness_score = 0
            flirtiness_score = int(input("Enter flirtiness score (1-3): "))
            if flirtiness_score == 1:
                flirtiness_desc = "Try to be a bit flirty."
            elif flirtiness_score == 2:
                flirtiness_desc = "Try to be decently flirty, not too little, not too much."
            else:
                flirtiness_desc = "Try to be very flirty."
        else:
            print("Invalid input. Please try again.")
            continue

        user_input = input("User: ")
        if user_input.lower() == "exit":
            break

        start_time = time.time()
        docs = retriever.invoke(user_input)
        generation = rag_chain.invoke({"question": user_input, "context": docs, "humour": humour_desc, "rudeness": rudeness_desc, "flirtiness": flirtiness_desc})
        end_time = time.time()
        response_time = end_time - start_time
        f.write(f"Humour: {humour_desc}\n")
        f.write(f"Rudeness: {rudeness_desc}\n")
        f.write(f"Flirtiness: {flirtiness_desc}\n")
        f.write(f"User: {user_input}\n")
        f.write(f"Assistant: {generation}\n")
        f.write(f"Response time: {response_time:.2f} seconds\n\n")
        print(f"Assistant: {generation}")
