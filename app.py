import os
import logging
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import sentry_sdk

from ingest import ingest_data
from utils.vector_store import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions
        profiles_sample_rate=1.0,
        # Enable performance monitoring
        enable_tracing=True,
        # Add Streamlit integration
        integrations=[],
        # Add environment name
        environment=os.getenv("SENTRY_ENV", "development"),
    )
    # Log that Sentry was initialized
    logging.info("Sentry initialized for error tracking")

# Get configuration from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
vector_db_dir = os.getenv("VECTOR_DB_DIR")

# Validate required environment variables
if not all([openai_api_key, vector_db_dir]):
    st.error("Missing required environment variables. Please check your .env file.")
    st.stop()

# Check if vector store exists
if not os.path.exists(vector_db_dir):
    st.error(f"Vector store not found at {vector_db_dir}. Please run ingest.py first.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Junior product manager",
    page_icon="🐔",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation" not in st.session_state:
    # Initialize vector store
    vector_store = VectorStore(vector_db_dir, openai_api_key)
    
    # Initialize language model
    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0,
        openai_api_key=openai_api_key
    )
    
    # Initialize conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Initialize retrieval chain
    st.session_state.conversation = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.db.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        verbose=True
    )

# App title
st.title("🐔Junior product manager")
st.markdown("""
Ask questions about the product knowledge based stored in Notion and local files.
""")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
# Chat input
if prompt := st.chat_input("Ask a question about your knowledge base..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if this is a data import request
    if prompt.lower() in ["update knowledge base"]:
        # Create a single assistant message placeholder
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            # First show the loading message
            message_placeholder.markdown("🔄 Starting data import process. This may take a few minutes...")

            # Run the import
            results = ingest_data(clear_existing=True)

            # Update the same placeholder with results
            completion_message = f"✅ Data import complete! Total amount of imported docs is {results['total_documents']}"
            message_placeholder.markdown(completion_message)

            # Add to chat history
            st.session_state.messages.append({"role": "assistant", "content": completion_message})
    else:
        # Display assistant response for normal queries
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            try:
                if st.session_state.conversation is None:
                    answer = "Please import your data first by typing 'import data'."
                else:
                    # Get response from conversation chain
                    response = st.session_state.conversation.invoke({"question": prompt})
                    answer = response["answer"]

                # Display the response
                message_placeholder.markdown(answer)

                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})

            except Exception as e:
                error_message = f"Error: {str(e)}"
                message_placeholder.error(error_message)
                logger.error(f"Error processing query: {e}")

                # Add error message to chat history
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
    Junior product manager. Reads the documents you have and answers stupid questions.
    
    **Can deal with:**
    - Notion pages
    - Plain text files stored in local folder
    
    To update the knowledge base, run the `ingest.py` script or
    text `update knowledge base` in the chat.
    
    Got questions? Ask Andrei!
    [Linkedin](https://www.linkedin.com/in/a-korchak/)
    [me@akorchak.software](mailto:me@akorchak.software)
    """)
    
    # Add a button to clear chat history
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        # Also clear the conversation memory
        st.session_state.conversation.memory.clear()
        st.rerun() 