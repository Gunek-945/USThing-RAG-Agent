# USThing-RAG-Agent

## Installation

It's recommended to set up a virtual environment for this project to keep the dependencies isolated from your system's global Python installation. Follow the steps below to get started:

### Create a Virtual Environment

1. Open a terminal or command prompt.
2. Navigate to the root directory of your project.
3. Create a new virtual environment using the following command: <br>
   ```python -m venv env ``` (Replce env with the name you want to give to your environment)

This will create a new directory called `env` in your project directory, which will contain the Python interpreter and all the installed packages.

4. Activate the virtual environment:

- On Windows:
  ```
  env\Scripts\activate
  ```
- On macOS or Linux:
  ```
  source env/bin/activate
  ```

You should see `(env)` at the beginning of your terminal prompt, indicating that the virtual environment is active.

### Install Dependencies

With the virtual environment active, you can install the [requirements.txt](https://github.com/Gunek-945/USThing-RAG-Agent/blob/main/requirements.txt) file given in the repository in the same project directory. Then run the following command-

   ```
   pip install -r requirements.txt
   ```

This will install all the packages listed in the `requirements.txt` file into your virtual environment.

### Enter necessary API keys

Create a `.env` file with the following variables:
```
PINECONE_API_KEY = [ENTER YOUR PINECONE API KEY HERE]
PINECONE_API_ENV = [ENTER YOUR PINECONE API ENVIRONMENT HERE]
```

Add your Groq API key while loading the llm in the program-

```
llm = ChatGroq(temperature=0.2, groq_api_key="GROQ_API_KEY", model="llama3-70b-8192")
```

## How to automate testing?
### Prepare data
WITHOUT namespace technique:
- Copy from Testing/template_json.json, fill in as needed. The field ```template_id``` refers to the index of template defined in templates.py. Index starts from 0. 
- In UST_RAG_AGENT_automate.py, under the main section, modify the file path as needed, the other bool argument is a small optimization trick when all user inputs in the file are the same (mainly useful for testing mood params). If ```True```, the retriever will only be invoked for the first question and the retrieved results will be reused for all subsequent reponses. If ```False```, the retriever will be invoked for each question. Run the file. 

