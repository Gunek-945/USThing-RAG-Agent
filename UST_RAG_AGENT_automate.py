import os
import time
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore

from templates import templates

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_API_ENV = os.getenv("PINECONE_API_ENV")

load_dotenv()



# LLM Chain
llm = ChatGroq(temperature=0.2, groq_api_key=os.getenv("GROQ_API_KEY"), model="llama3-70b-8192")

def load_and_split_documents(file_paths):
    documents = []
    for file_path in file_paths:
        loader = TextLoader(file_path, encoding='utf-8')
        text_documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        documents.extend(text_splitter.split_documents(text_documents))
    return documents

file_paths = [
    'Academic regulations.txt', #correct path 
    'student_organizations.txt' #correct path
]

documents = load_and_split_documents(file_paths)

embeddings = HuggingFaceEmbeddings()

# Create or load the Pinecone vector store
index_name = "usthing-rag-index"
vectorstore = Pinecone.from_documents(documents, embeddings, index_name=index_name)
retriever = vectorstore.as_retriever()


def get_reponse(convo_entry:dict, provided_docs):
    template_id= convo_entry['template_id']
    prompt = ChatPromptTemplate.from_template(templates[template_id])
    # Prompt-based Chain
    rag_chain = prompt | llm | StrOutputParser()
    start_time = time.time()
    user_input=convo_entry['user_input']
    if not provided_docs:
        docs = retriever.invoke(user_input)
    else:
        docs= provided_docs
    generation = rag_chain.invoke({"question": user_input, "context": docs, "humour": convo_entry['humour_score'], "rudeness": convo_entry['rudeness_score'], "flirtiness": convo_entry['flirtiness_score']})
    #generation = rag_chain.invoke({"question": user_input, "context": docs, "humour": convo_entry['humour_score'], "rudeness": convo_entry['rudeness_score'], "sophistication": convo_entry['sophistication_score']})
    end_time = time.time()
    response_time = end_time - start_time
    return generation, response_time

def test_with_json(json_file_path, same_question):
    with open(json_file_path, 'r+') as file:
        data = json.load(file)
        conversations_list = data['conversations']
        if same_question:
            provided_docs= retriever.invoke(conversations_list[0]['user_input']) #only retrieve once to avoid repeated calls 
        else:
            provided_docs= None
        for convo in conversations_list:
            generation, response_time= get_reponse(convo, provided_docs)
            convo['response']= generation
            convo['Response time']= round(response_time,2)
            print(f"generating question {convo['test_id']} took {convo['Response time']} seconds")
            
        # Move the file pointer back to the beginning
        file.seek(0)

        # Write the updated data back to the file
        json.dump(data, file, indent=4)

        # Truncate the file to the current position of the file pointer
        file.truncate()

if __name__=="__main__":
    test_with_json(r"Testing\combo2.json", True)


"""
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
"""