from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores.chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate

from dotenv import load_dotenv

import os


load_dotenv("config/.env")
VECTORSTORE_DIRECTORY = os.getenv("VECTORSTORE_DIRECTORY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo", 
    temperature=0
)

def generate_prompt(partial_variables = None):
    input_variables = ["context", "question"]
    prompt_template = """
你是一位專業的演算法和資料結構教授，你擅長逐行分析我的程式碼，並與相似的正確程式碼互相比較，思考當中的程式邏輯、演算法、資料結構、時間複雜度等，最後依據我的程式碼以五句內的提示指引我下一步的方向、或指出程式的錯誤，而不直接提供程式碼和答案。
題目敘述: {description}
相似的正確答案: {context}\n
我的錯誤程式碼: {code}\n
額外問題(若無則忽略): {question}
"""
    messages = [
        SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=input_variables,
                partial_variables=partial_variables,
                template=prompt_template
            )
        )
    ]
    prompt = ChatPromptTemplate(input_variables=input_variables, messages=messages)
    return prompt


def retrieve(
    name: str, 
    prompt: ChatPromptTemplate
):
    """Retrieve data from the specified collection_name and create a QA_Chain.
    """
    vectordb = Chroma(
        collection_name=name, 
        persist_directory=VECTORSTORE_DIRECTORY,
        embedding_function=OpenAIEmbeddings()
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(),
        chain_type_kwargs={"prompt": prompt}, 
        return_source_documents=True
    )
    return qa_chain


def generate_response(
    collection_name: str, 
    question: str,
    code: str, 
    description: str, 
):
    """Generate a response using LLM based on the user's query and retrieved data.
    """
    prompt = generate_prompt(
        {
            "description": description, 
            "code": code
        }
    )
    qa_chain = retrieve(collection_name, prompt)
    response = qa_chain(
        {"query": question,}
    )
    return response