import json
import streamlit as st
import boto3

# Dictionary containing model providers, model name and model ID
model_dic = {
    'Amazon':
        {'Titan Text G1 - Lite': "amazon.titan-text-lite-v1",
         'Titan Text G1 - Express': "amazon.titan-text-express-v1"},
    'Mistral':
        {"Mistral 7B Instruct": "mistral.mistral-7b-instruct-v0:2",
         "Mistral 8x7B Instruct": "mistral.mixtral-8x7b-instruct-v0:1",
         "Mistral Large": "mistral.mistral-large-2402-v1:0"},
    'Meta':
        {"Llama 3 8B Instruct": "meta.llama3-8b-instruct-v1:0",
         "Llama 3 70B Instruct": "meta.llama3-70b-instruct-v1:0"}
}


# Function to configure sidebar to get the secret access key
def configure_secret_access_key_sidebar():
    st.sidebar.subheader('Enter the Secret Access Key')
    secret_key = st.sidebar.text_input('Enter the secret access key', type='password', label_visibility='collapsed')
    if secret_key == '':
        st.sidebar.warning('Enter the secret access key to unlock the application')
        app_unlocked = False
    elif len(secret_key) == 40:
        st.sidebar.success('Proceed. Application is now unlocked', icon='️👉')
        app_unlocked = True
    else:
        st.sidebar.error('Please enter the correct credentials!', icon='⚠️')
        app_unlocked = False

    return secret_key, app_unlocked


# Function configure sidebar for model selection
def configure_sidebar_for_model_selection():
    st.sidebar.subheader('Select the Model Provider')
    model_provider = st.sidebar.selectbox("Select the Model Provider:", (model_dic.keys()),
                                          label_visibility='collapsed')
    st.sidebar.subheader('Select the LLM')
    llm = st.sidebar.selectbox("Select the LLM", (model_dic[model_provider].keys()), label_visibility='collapsed')
    model_id = model_dic[model_provider][llm]
    return model_provider, model_id


# Function to configure model payload as per given model provider. Each model provider has different ways to
# configure payload
def get_model_payload(model_provider, prompt_data):
    if model_provider == 'Mistral':
        return {
            "prompt": "[INST]" + prompt_data + "[/INST]",
            "max_tokens": 200,
            "temperature": 0.5,
            "top_p": 0.9,
            "top_k": 50
        }
    elif model_provider == 'Amazon':
        textGenerationConfig = {"maxTokenCount": 4096, "stopSequences": [], "temperature": 0, "topP": 1}
        return {
            "inputText": prompt_data,
            "textGenerationConfig": textGenerationConfig
        }

    elif model_provider == 'Meta':
        return {
            "prompt": "[INST]" + prompt_data + "[/INST]",
            "max_gen_len": 512,
            "temperature": 0.5,
            "top_p": 0.9
        }


# Function to get model response based on model provider.
def get_model_response(model_provider, response_body):
    if model_provider == 'Mistral':
        return response_body['outputs'][0]['text']
    elif model_provider == 'Amazon':
        return response_body['results'][0]['outputText']
    elif model_provider == 'Meta':
        return response_body['generation']


# Function to invoke LLM
def invoke_llm_model(prompt_data, model_provider, model_id, secret_key):
    bedrock = boto3.client(service_name='bedrock-runtime',
                           aws_access_key_id='AKIAYS2NUCSXLJLV3AG6',
                           aws_secret_access_key=secret_key,
                           region_name='ap-south-1')
    payload = get_model_payload(model_provider, prompt_data)
    body = json.dumps(payload)
    response = bedrock.invoke_model(
        body=body,
        modelId=model_id,
        contentType="application/json",
        accept="application/json"
    )
    response_body = json.loads(response.get("body").read())
    response_text = get_model_response(model_provider, response_body)
    return response_text
