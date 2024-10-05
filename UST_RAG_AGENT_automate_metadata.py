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
from pinecone import Pinecone as PC
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
        #text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
        #text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
        documents.extend(text_splitter.split_documents(text_documents))
    return documents

file_paths = [ #NOTE: REMEMBER TO MAKE A NEW PINECONE INDEX IF THIS IS CHANGED
    "data/Faculty/Department of Chemistry.txt",
    "data/Faculty/Department of Mathematics.txt",
    "data/Faculty/Department of Physics.txt",
    "data/Faculty/Department of Ocean Science.txt", 
    "data/Academic regulations.txt",  #comment out for replication-faculty
    "data/student_organizations.txt", #comment out for replication-faculty
] #NOTE: REALLY MAKE SURE TO MAKE A NEW PINECONE INDEX IF THIS IS CHANGED

topics_metadata = {
    "data/Faculty/Department of Chemistry.txt":"faculty",
    "data/Faculty/Department of Mathematics.txt":"faculty",
    "data/Faculty/Department of Physics.txt":"faculty",
    "data/Faculty/Department of Ocean Science.txt":"faculty",
    "data/Academic regulations.txt":"academic",
    "data/student_organizations.txt":"student_life"
}

documents = load_and_split_documents(file_paths)

for doc in documents:
    doc.metadata["topic"]= topics_metadata[doc.metadata['source']]
    #print(doc.metadata)

embeddings = HuggingFaceEmbeddings()

# Create or load the Pinecone vector store
#index_name = "usthing-rag-index" 
#index_name = "faculty" #replication-faculty
#index_name ="regulations-faculty" #replication-all-content. #chunk_size=1000, chunk_overlap=20
#index_name ="regulations-faculty-large" #chunk_size=4000, chunk_overlap=200
index_name ="regulations-faculty-medium" #chunk_size=2000, chunk_overlap=100
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

pc = PC(api_key=PINECONE_API_KEY)
existing_indexes = [
    index_info["name"] for index_info in pc.list_indexes()
]
if index_name in existing_indexes:
    text_field= "text"
    index = pc.Index(index_name)
    # initialize the vector store object
    vectorstore = Pinecone(
        index, embeddings, text_field
    )
else:
    vectorstore = Pinecone.from_documents(documents, embeddings, index_name=index_name)
# Create namespace-specific vectorstores
"""
for namespace, files in namespaces.items():
    namespace_docs = load_and_split_documents(files)
    vectorstore.add_documents(namespace_docs, namespace=namespace)
"""


retriever = vectorstore.as_retriever()

def get_relevant_docs(user_input, topic_filter):
    user_input= remove_stopwords(user_input)
    if topic_filter:
        print(f"Filtering for topic: {topic_filter}")
        #retriever1 = vectorstore.as_retriever(search_kwargs={"filter":{"topic": topic_filter}})
        #docs = retriever1.invoke(user_input)
        filter_criteria = {"topic": topic_filter}
        
        # Use the retriever with the filter
        #docs = retriever.invoke(user_input, search_kwargs={"filter": filter_criteria})
        docs= vectorstore.similarity_search(user_input, filter={
        "topic": {"$eq": topic_filter}
    })
        print(user_input)
        for doc in docs:
            print(doc.metadata)

    else:
        docs = retriever.invoke(user_input)
    return docs

def remove_stopwords(text):
    stopwords = ["the", "a", "an", "is", "are", "was", "were", "of", "in", "on", "at", "to", "from", "by", "with", "and", "or", "for", "as", "this", "that", "these", "those", "it", "its", "they", "their", "them", "he", "she", "his", "her", "him", "we", "our", "us", "you", "your", "i", "my", "me", "mine", "am", "be", "being", "been", "have", "has", "having", "do", "does", "doing", "did", "will", "would", "shall", "should", "can", "could", "may", "might", "must", "ought", "about", "above", "across", "after", "against", "along", "among", "around", "as", "at", "before", "behind", "below", "beneath", "beside", "between", "beyond", "but", "by", "down", "during", "except", "for", "from", "in", "inside", "into", "like", "near", "next", "off", "on", "onto", "out", "outside", "over", "past", "since", "through", "throughout", "till", "to", "toward", "under", "underneath", "until", "up", "upon", "without", "within", "yet", "hkust", "HKUST"]
    text = text.lower()
    text = text.split()
    text = [word for word in text if word not in stopwords]
    text = " ".join(text)
    return text
#use_provided_topic means using the topic provided in the json file, different for each question
#provided_docs is the relevant docs for the first question, to avoid repeated calls to the retriever
#when providing docs, we don't care about the use_provided_topic flag
def get_reponse(convo_entry:dict, provided_docs, use_provided_topic):
    template_id= convo_entry['template_id']
    prompt = ChatPromptTemplate.from_template(templates[template_id])
    # Prompt-based Chain
    rag_chain = prompt | llm | StrOutputParser()
    start_time = time.time()
    user_input=convo_entry['user_input']
    if not provided_docs:
        if use_provided_topic:
            topic= convo_entry['topic']
        else:
            topic=None
        docs = get_relevant_docs(user_input, topic)
    else:
        docs= provided_docs
    generation = rag_chain.invoke({"question": user_input, "context": docs, "humour": convo_entry['humour_score'], "rudeness": convo_entry['rudeness_score'], "flirtiness": convo_entry['flirtiness_score']})
    #generation = rag_chain.invoke({"question": user_input, "context": docs, "humour": convo_entry['humour_score'], "rudeness": convo_entry['rudeness_score'], "sophistication": convo_entry['sophistication_score']})
    end_time = time.time()
    response_time = end_time - start_time
    return generation, response_time, docs

def process_docs_for_json(docs):
    processed_docs= []
    for doc in docs:
        #processed_docs.append({"metadata": doc.metadata, "page_content": doc.page_content})
        processed_docs.append({"metadata": doc.metadata})
    return processed_docs

def test_with_json(json_file_path, same_question, use_provided_topic=False):
    with open(json_file_path, 'r+') as file:
        data = json.load(file)
        conversations_list = data['conversations']
        if same_question:
            if use_provided_topic:
                topic= conversations_list[0]['topic']
            else:
                topic=None
            provided_docs = get_relevant_docs(conversations_list[0]['user_input'], topic) #only retrieve once to avoid repeated calls 
        else:
            provided_docs= None
        for convo in conversations_list:
            try: 
                generation, response_time,docs= get_reponse(convo, provided_docs, use_provided_topic)
                convo['ref_docs']= process_docs_for_json(docs)
                convo['response']= generation
                convo['Response time']= round(response_time,2)
                print(f"generating question {convo['test_id']} took {convo['Response time']} seconds")
            except Exception as e:
                #print(f"Error in generating question {convo['test_id']}: {e}")
                convo['response']= "ERROR"
                convo['Response time'] =-1
            
        # Move the file pointer back to the beginning
        file.seek(0)

        # Write the updated data back to the file
        json.dump(data, file, indent=4)

        # Truncate the file to the current position of the file pointer
        file.truncate()

if __name__=="__main__":
    #test_with_json(r"Testing\test.json", False, False)
    test_with_json(r"Testing\filter_test_filter.json", False, use_provided_topic=True)


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