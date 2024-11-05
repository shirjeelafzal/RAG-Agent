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

load_dotenv()

GROQ_API_KEY=os.getenv('GROQ_API_KEY')

llm = ChatGroq(model="llama3-8b-8192")


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
    def embed_documents(self, texts):
        return embedding_model.encode(texts).tolist() 
    def embed_query(self, text):
        return embedding_model.encode([text])[0].tolist()

vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=CustomEmbeddings(),
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
  
  
# cleanup
vectorstore.delete_collection()

