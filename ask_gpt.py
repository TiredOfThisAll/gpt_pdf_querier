from langchain import hub
from langchain_community.document_loaders.pdf import PDFPlumberLoader
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
import hashlib
import os
import json


OPENAI_TOKEN_CACHE = None
OPENAI_TOKEN_CACHE_TIME = None


def openai_token():
	global OPENAI_TOKEN_CACHE
	global OPENAI_TOKEN_CACHE_TIME
	if OPENAI_TOKEN_CACHE_TIME is None or OPENAI_TOKEN_CACHE_TIME < os.path.getmtime("token.txt"):
		with open("token.txt") as token:
			OPENAI_TOKEN_CACHE_TIME = os.path.getmtime("token.txt")
			OPENAI_TOKEN_CACHE = token.read()
	return OPENAI_TOKEN_CACHE


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def hash_file(path):
	BUF_SIZE = 65536
	sha1 = hashlib.sha1()

	with open(path, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			sha1.update(data)
	return sha1.hexdigest()


def extract_text_from_pdf(path):
	hash = hash_file(path)
	
	
	if os.path.isdir("cache"):
		if os.path.exists(f"cache/{hash}.json"):
			with open(f"cache/{hash}.json") as f:
				file = json.loads(f.read())
				return list(map(lambda x: Document(x["page_content"], metadata=x["metadata"]), file))
	else:
		os.mkdir("cache")

	loader = PDFPlumberLoader(path)
	data = loader.load()
	with open(f"cache/{hash}.json", mode="w") as f:
		f.write(json.dumps(list(map(lambda x: {"metadata": x.metadata, "page_content": x.page_content}, data))))

	return data


def process_pdf(path):
	data = extract_text_from_pdf(path)
	text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
	splits = text_splitter.split_documents(data)
	vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(api_key=openai_token()))

	retriever = vectorstore.as_retriever()
	prompt = hub.pull("rlm/rag-prompt")
	llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, api_key=openai_token())
	rag_chain = (
		{"context": retriever | format_docs, "question": RunnablePassthrough()}
		| prompt
		| llm
		| StrOutputParser()
	)
	return rag_chain
