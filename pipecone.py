import os 
import bs4
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from sentence_transformers import SentenceTransformer
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import MessagesPlaceholder
from typing_extensions import Annotated, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools.retriever import create_retriever_tool
from langgraph.graph import START, StateGraph
from typing import Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import create_react_agent

from langchain.vectorstores import Pinecone as lang_pinecone
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

GROQ_API_KEY=os.getenv('GROQ_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
llm = ChatGroq(model="llama3-8b-8192")


index_name = "test"

pc = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY")
)

# Now do stuff
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name='test', 
        dimension=384, 
        metric='euclidean',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )



loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

class State(TypedDict):
    input: str
    chat_history: Annotated[Sequence[BaseMessage], add_messages]
    context: str
    answer: str
    
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class CustomEmbeddings:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
    
    # This will make the object callable directly
    def __call__(self, texts):
        return self.embed_documents(texts)
    
    def embed_documents(self, texts):
        # Convert the texts into embeddings using the Sentence Transformer model
        return self.embedding_model.encode(texts).tolist()

    def embed_query(self, text):
        # Convert the query into an embedding
        return self.embedding_model.encode([text])[0].tolist()

vectorstore = lang_pinecone.from_documents(
    documents=splits,
    embedding=CustomEmbeddings(embedding_model=embedding_model),
    index_name=index_name,
    text_key="text"
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

tool = create_retriever_tool(
    retriever,
    "blog_post_retriever",
    "Searches and returns excerpts from the Autonomous Agents blog post.",
)
tools = [tool]
memory = MemorySaver()
agent_executor = create_react_agent(llm, tools, checkpointer=memory)
config = {"configurable": {"thread_id": "abc123"}}

while True:
    
    # query = "What is Task Decomposition?"
    query=input("Enter your question: ")
    if query in ["quit","exit","close"]:
        break
    for event in agent_executor.stream(
        {"messages": [HumanMessage(content=query)]},
        config=config,
        stream_mode="values",
    ):
        last_message = event["messages"][-1]
        # last_message.pretty_print()  # This will give you a nicely formatted output of the last message

        # Print the actual content of the AI's response
        if isinstance(last_message, AIMessage):
            print("AI Response:", last_message.content)
  
  
