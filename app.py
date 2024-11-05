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

prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
)

response = rag_chain.invoke("What is Task Decomposition?")

print(response.content)


# cleanup
vectorstore.delete_collection()