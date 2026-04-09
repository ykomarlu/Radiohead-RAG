import os
from dotenv import load_dotenv, find_dotenv
import argparse

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# the purpose of this file: to query the vector database created in create_database.py based on the 
# prompt provided by the user for relevant documents. Then use the LLM to answer the question
# based on the context of the relevant documents. It also documents the sources used to answer the question.

_ = load_dotenv(find_dotenv())
my_api_key = os.environ['OPENAI_API_KEY']
CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = """
Answer the question using only the following context:
{context}
-------------------------------------------------------------
Answer this question based on the context above: {question} 
"""

def chatbot_response():
    # purpose of method: it retrieves the prompt from the user, isolate the relevant documents
    # from the db, puts those files in the context of the prompt, and then uses the LLM to answer the question based on the context.
    # Finally, it documents the sources used to answer the question.

    # Parser to input the query text in the command line

    # arg parser parses the prompt from the user
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The text to search for")
    args = parser.parse_args()
    query_text = args.query_text
    
    # prepare the db: sets up the math function for creating the embeddings  
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    
    # search the vector db for the relevant chunks -> returns a list of (document, score) tuples
    
    results = db.similarity_search_with_relevance_scores(query_text, f=4) # k is the number of results to return
    if len(results) == 0 or results[0][1] < 0.7: # if the relevance score of the first result is less than 0.7, return
        print(f"Unable to find matching results for {query_text}")
        return
    
    # create the prompt for the chatbot
    # This is for the response of the chatbot to the user
    context = "\n\n---\n\n".join([doc.page_content for doc, score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context, question=query_text)
    print(prompt) # print the prompt to the user
    
    # the LLM uses the prompt to answer the question
    model = ChatOpenAI()
    response_text = model.predict(prompt)
    
    # Documents the source
    # used to answer the prompt
    sources = [doc.metadata.get("source", None) for doc, score in results]
    formatted_response = f"{response_text}\n\nSources: {sources}"
    print(formatted_response) # print the entire response and the sources used to answer the prompt
    
if __name__ == "__main__":
    chatbot_response()