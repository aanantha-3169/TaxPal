import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
import weaviate
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import WeaviateVectorStore
from llama_index.memory import ChatMemoryBuffer

st.set_page_config(page_title="TaxPal", page_icon="💰", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets["openai_key"]

st.title("TaxPal: Your personal income tax assistant 🧾👨🏻‍🏫")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Try me out! Ask me your questions about personal income tax"}
    ]

def load_data():
    with st.spinner(text="Waking up TaxPal 😴"):
        auth_config = weaviate.AuthApiKey(api_key=st.secrets['w_key'])
        

        client = weaviate.Client(
        url= st.secrets['w_url'],
        auth_client_secret=auth_config
        )

        vector_store = WeaviateVectorStore(
                weaviate_client=client, index_name="TaxIndex"
            )
        
        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", system_prompt="You are a Malaysia income tax expert and your job is to answer only questions related to Malaysia income tax. You must only use information provided to generate your answer. If the information is not relevant to the question response 'Dont know'. You must very answer questions that are not related to income tax."))
        
        loaded_index = VectorStoreIndex.from_vector_store(vector_store
        , service_context = service_context
        )

        return loaded_index

index = load_data()

memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
    st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question",
    verbose=True)
#  st.session_state.chat_engine = index.as_chat_engine(
#     chat_mode="context",
#     memory=memory,
#     system_prompt=(
#         "You are a Malaysia income tax expert and your job is to answer only questions related to Malaysia income tax. You must only use information provided to generate your answer. If the information is not relevant to the question response 'Dont know' "
#         ),
#         verbose = True
#     )   
if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history