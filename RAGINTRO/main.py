from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings
import bs4
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


llm = ChatGoogleGenerativeAI(model = "gemini-3.6-flash")

loader = WebBaseLoader(
   web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",), #Bilgiyi nerden çekeceğimizi belirtiyoruz
   bs_kwargs = dict(   #BeatifulSoup keyword arguments
      parse_only = bs4.SoupStrainer( #İnternet üzerinden html olaarak çektiğimiz verilerin parse edip ilgili yerlere almamızı sağlayan kütüphane
         class_ =("post-content","post-title","post-header") #neleri alacağımız söylüyoruz
      )
   ),
)


docs = loader.load()

def format_docs(docs):
   return "\n\n".join(doc.page_content for doc in docs)

splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
splits = splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits,embedding=GoogleGenerativeAIEmbeddings(model = "gemini-embedding-2"))

retriever = vectorstore.as_retriever()

#rag_promt


prompt = ChatPromptTemplate.from_messages([
    ("human",
     "You are an assistant for question-answering tasks. "
     "Use the following pieces of retrieved context to answer the question. "
     "If you don't know the answer, just say that you don't know. "
     "Use three sentences maximum and keep the answer concise.\n\n"
     "Question: {question}\n\nContext: {context}\n\nAnswer:")
])

chain = (
   {"context" : retriever | format_docs , "question" : RunnablePassthrough()}
   | prompt
   | llm
   | StrOutputParser()
)






if __name__ == '__main__':
   for chunk in chain.stream("what is ReAct?"):
      print(chunk,end="",flush=True)
