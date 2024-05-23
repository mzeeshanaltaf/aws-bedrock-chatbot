from util import *

# --- PAGE SETUP ---
# Initialize streamlit app
page_title = "Chatbot using AWS Bedrock"
page_icon = "💬"
st.set_page_config(page_title=page_title, page_icon=page_icon, layout="centered")

st.title("💬 Chatbot using AWS Bedrock")
st.write("***A Streamlit Chatbot powered by AWS Bedrock***")

secret_key, app_unlocked = configure_secret_access_key_sidebar()
model_provider, model_id = configure_sidebar_for_model_selection()

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder='Enter Your Message', disabled=not app_unlocked):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner('Processing...'):
        model_response = invoke_llm_model(prompt, model_provider, model_id, secret_key)

        st.session_state.messages.append({"role": "assistant", "content": model_response})
        st.chat_message("assistant").write(model_response)
