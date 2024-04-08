import argparse
import streamlit as st
from utils.config import Config
from models.ragtools import RAGServiceConfig
from models.ragtools import RAGServiceContext 
from llama_index.core import KnowledgeGraphIndex
from llama_index.core import StorageContext
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever

def chatbot(config: Config) -> None:
    if prompt := st.chat_input(config.chatbot.chat_input_prompt):
        st.session_state.messages.append({"role": "user", "content": prompt})

    # Display old messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If the last message isn't from the assistant, generate a new response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner(config.chatbot.chat_generation_phrase):
                response = st.session_state.chat_engine.chat(prompt)
                st.write(response.response)
                message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(message)


if __name__ == "__main__":
    # Initialize our configurations
    config = Config(
        config_dict=st.secrets,
        yaml_path=[
        "src/configs/chatbot_config.yaml", 
        "src/configs/azure/model_config.yaml"],
    )
    RAGService = RAGServiceContext(
        config=RAGServiceConfig(config=config.model_config))
   # Knowledge Graph
    graph_store = Neo4jGraphStore(
        username=config.neo4j_user,
        password=config.neo4j_password,
        url=config.neo4j_url,
        database=config.neo4j_database
    )
    storage_context = StorageContext.from_defaults(graph_store=graph_store)
    graph_rag_retriever = KnowledgeGraphRAGRetriever(
        storage_context=storage_context,
        verbose=True,
    )
    # Start the chatbot
    st.set_page_config(**config.chatbot.page_config)
    st.title(config.chatbot.page_config.page_title)
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [config.chatbot.messages]

    if "chat_engine" not in st.session_state.keys():
        st.session_state.chat_engine = RetrieverQueryEngine.from_args(
            graph_rag_retriever, service_context=RAGService.service_context)
        
    chatbot(config=config)
