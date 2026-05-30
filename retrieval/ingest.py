from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

print("Loading PDF...")

loader = PyPDFLoader("data/fegp107.pdf")
documents = loader.load()

print(f"Loaded {len(documents)} pages")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

docs = splitter.split_documents(documents)

print(f"Created {len(docs)} chunks")

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Creating vector DB...")

db = Chroma.from_documents(
    docs,
    embedding,
    persist_directory="./chroma_db"
)

db.persist()

print("DONE!")