import os
from flask import Flask, request, jsonify, render_template
from elasticsearch import Elasticsearch
import openai
import requests
import json


# Load Env File
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Load Envs
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELASTICSEARCH_ENDPOINT = os.getenv("ELASTICSEARCH_ENDPOINT")
ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
BOT_NAME = os.getenv("BOT_NAME")

openai.api_key = OPENAI_API_KEY
#openai.base_url = "http://192.168.1.232:1234/v1/"

# Connect to Elasticsearch
es = Elasticsearch(
    ELASTICSEARCH_ENDPOINT,
    api_key=ELASTICSEARCH_API_KEY
)

##### ONLY IF ERROR HAPPENS
def force_generate_dsl_query(question, dsl_query, es_response, index):
    
    print("###### ENTROU NO FORCE #######")
    print("FORCE")
    print("####################")
    
    while "[*] Error:" in es_response:
    
        prompt = f"""
        
        You received this question: "{BOT_NAME}", in your first attempted you genereted this Elasticsearch dsl query "{dsl_query}", but when I ran this query I received this error: "{es_response}". Can you generate another dsl query? Remember some question can only asnwer with aggregations for example, the max value, the min value, how many times and other situation that you need to aggregate data.

        - Respond with only valid JSON query without any additional explanations or syntax formatter like mardown.
        - Remove marks like "```json" or any other type
        - Your output answer MUST TO BE a json string, without any other explanations
        """
        try:
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "system", "content": prompt},
                        {"role": "user", "content": question}],
                temperature=0.1
            )
        except Exception as e:
            print(f"Error: {e}")
            return "Failed to generate response from OpenAI"

        # Parse the response and return the generated query
        #print(response)
        dsl_query = response.choices[0].message.content
        if "<think>" in dsl_query:
            dsl_query = dsl_query.split("</think>")[1]
        print(dsl_query)
        
        es_response = execute_query(INDEX_NAME, dsl_query)
        print(es_response)
        
    return dsl_query, es_response

def generate_dsl_query(question, index):
    
    mapping = str(index_mapping(index))
    
    print("########QUESITION#########")
    print(question)
    print("####################")
    
    print("######MAPPING#######")
    #print(mapping)
    print("####################")
    
    """
    Uses OpenAI API to convert a natural language question into an Elasticsearch Query DSL.
    """
    prompt = f"""
    
    - You are an Elasticsearch Especialist
    - You are correct, factual, precise, and reliable.
    
    Now you MUST generate a dsl query using this "{question}" based in the following mapping! Remember some question can only asnwer with aggregations for example, the max value, the min value, how many times and other situation that you need to aggregate data.
    
    {mapping}

    - Respond with only valid JSON query without any additional explanations or syntax formatter like mardown.
    - Remove marks like "```json" or any other type
    - Your output answer MUST TO BE a json string, without any other explanations
    """
    
    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": prompt},
                    {"role": "user", "content": question}],
            temperature=0.1
        )
    except Exception as e:
        print(f"Error: {e}")
        return "Failed to generate response from OpenAI"

    # Parse the response and return the generated query
    print("####################")
    print("heuheuheu")
    print("####################")
    #print(response)
    dsl_query = response.choices[0].message.content
    print(dsl_query)
    if "<think>" in dsl_query:
        dsl_query = dsl_query.split("</think>")[1]
    print(dsl_query)
    print("####################")
    print("heuheuheu")
    print("####################")

    return dsl_query.strip()
    
def execute_query(index, query_dsl):
    """
    Executes the DSL query in Elasticsearch.
    """
    print("###### query dsl #########")
    print(query_dsl)
    print("####################")
    try:
        #query = eval(query_dsl)  # Convert string JSON to Python dictionary
        response = es.search(index=index, body=query_dsl)
        return response
    except Exception as e:
        return "[*] Error: " + str(e)
    
def index_mapping(index):
    print("####################")
    print(index)
    print("####################")
    try:
        mapping = es.indices.get_mapping(index=index)
        return mapping
    except Exception as e:
        return "[*] Error: " + str(e)

def format_response(question, es_response):
    """
    Converts the Elasticsearch response into a natural language answer.
    """
    
    prompt = f"""
    Instructions:
    - Your name now is "{BOT_NAME}"
    - You are an Elasticsearch Especialist
    - You are correct, factual, precise, and reliable.
    - If you don't know the answer, just say that you don't know, don't make up an answer.
    - Your must answer the question in the same language of the question
    - Convert the following document in a natural language to answer the question:

    Response: "{es_response}"
    
    - If the answer return 0 hits, you can answer things like: "I didn't find any information for this question. Could you inform more details? I really want to help you.
    - Respond like you are talking with a human, but again YOU MUST answer in the same language of the question!
    - Based on the response you need to check if the data returned by the query may contain some kind of anomaly in a global context.
    
    """
    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            #model="mistral-nemo-instruct-2407",
            messages=[{"role": "system", "content": prompt},
                    {"role": "user", "content": question}]
        )
    except Exception as e:
        return "Could not process the response."

    # Parse the response and return the generated query
    dsl_query = response.choices[0].message.content
    
    print("######### RESPONSE DSL  ###########")
    print(dsl_query)
    print("####################")
    if "<think>" in dsl_query:
        dsl_query = dsl_query.split("</think>")[1]
    return dsl_query.strip()

# Route to serve the index.html file
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    # Dummy response for now, replace with logic if needed
    
    url = "http://192.168.1.87:7860/api/v1/run/be365d9e-4049-43ac-89d1-8a32f3bcbdfe"

    querystring = {"stream":"false"}

    payload = {
        "input_value": user_message,
        "output_type": "text",
        "input_type": "text",
        "tweaks": {"Prompt-Noy6B": {
                "template": "kibana_sample_data_ecommerce",
                "tool_placeholder": ""
            }}
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/10.3.1"
    }

    response_question = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    response_question = response_question.text
    response_question = json.loads(response_question)
    response_question = response_question['outputs'][0]['outputs'][0]['results']['text']['data']['text']

    response = {"reply": f"{response_question}"}
    return jsonify(response)

# Flask route for the API endpoint
@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.json
    question = data.get("question", "")
    index = INDEX_NAME
    
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Get Elasticsearch results
    dsl_query = generate_dsl_query(question, index)
    es_response = execute_query(index, dsl_query)
    print(str(es_response))
    if "[*] Error" in es_response:
        dsl_query, es_response = force_generate_dsl_query(question, dsl_query, es_response, index)
    answer = format_response(question, es_response)
    #answer = "Debug mode ativado"
    #return jsonify({"answer": answer,"dsl_query": answer, "es_response": answer})

    return jsonify({"answer": answer,"dsl_query": dsl_query, "es_response": str(es_response)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
