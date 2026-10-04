import time
from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pathlib import Path
import bs4


urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

COLLECTION = "rag_chroma"
PERSIST_DIR = str(Path(__file__).parent / ".chroma")
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")


def ingest():
    docs = [WebBaseLoader(url,bs_kwargs=dict(parse_only=bs4.SoupStrainer(class_=("post-content", "post-title", "post-header")))).load() for url in urls]
    docs_list = [item for sublist in docs for item in sublist]

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=250, chunk_overlap=0
    )
    doc_splits = text_splitter.split_documents(docs_list)
    print(f"{len(doc_splits)} parça yüklenecek")

    vectorstore = Chroma(
        collection_name=COLLECTION,
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings,
    )

    batch = 50
    for i in range(0, len(doc_splits), batch):
        vectorstore.add_documents(doc_splits[i:i + batch])
        print(f"{min(i + batch, len(doc_splits))} / {len(doc_splits)}")
        if i + batch < len(doc_splits):
            time.sleep(60)


retriever = Chroma(
    collection_name=COLLECTION,
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings,
).as_retriever()


if __name__ == "__main__":
    ingest()