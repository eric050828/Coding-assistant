from langchain.vectorstores.chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from dotenv import load_dotenv

import os


load_dotenv()
VECTORSTORE_DIRECTORY = os.getenv("VECTORSTORE_DIRECTORY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


def load_text(file_path: str):
    loader = TextLoader(file_path)
    data = loader.load()
    return data


def split_data(data):
    text_slpitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=0)
    chunks = text_slpitter.split_documents(data)
    return chunks


def store_codes(
    collection_name: str, 
    file_paths: list[str]
):
    """Save all Python files in file_paths to the collection.
    """
    for file_path in file_paths:
        data = load_text(file_path)
        chunks = split_data(data)
        vectordb = Chroma.from_documents(
            collection_name=collection_name,
            documents=chunks,
            persist_directory=VECTORSTORE_DIRECTORY,
            embedding=OpenAIEmbeddings(),
        )
        vectordb.persist()


def delete_codes(
    collection_name: str, 
    ids: list[str], 
):
    """From collection delete by IDs.
    """
    vectordb = Chroma(
        collection_name=collection_name,
        persist_directory=VECTORSTORE_DIRECTORY
    )
    vectordb.delete(ids=ids)

def show_codes_data(
    collection_name: str, 
    show_ids: bool = False, 
    show_embeddings: bool = False, 
    show_metadatas: bool = False, 
    show_documents: bool = True, 
    row_col_swap: bool = True,
    where:dict[str, str] = None, 
) -> list[str] | list[list[str]]:
    """Get data from the collection and return a list.
    Notes:
    - param ``where`` is not working
    """
    vectordb = Chroma(
        collection_name=collection_name,
        persist_directory=VECTORSTORE_DIRECTORY
    )
    data = vectordb.get(where=where)
    result = []
    if show_ids: result.append(data["ids"])
    if show_embeddings: result.append(data["embeddings"])
    if show_metadatas: result.append(data["metadatas"])
    if show_documents: result.append(data["documents"])

    if len(result) > 1 and row_col_swap:
        return list(zip(*result))
    return result[0] if len(result) == 1 else result


def update_code(
    collection_name: str, 
    id: str, 
    file_path: str
):
    """Deprecated.
    
    Parameters
    ----------
    id: str
        Original document ID to be modified.
    file_path: str
        New document to be uploaded.
    """
    vectordb = Chroma(
        collection_name=collection_name,
        persist_directory=VECTORSTORE_DIRECTORY
    )
    data = load_text(file_path)
    chunks = split_data(data)
    vectordb.update_document(document_id=id, document=chunks)
    

def get_exist_problems() -> list[str]:
    """From VectorDB get collection names.
    """
    client = chromadb.PersistentClient(path=VECTORSTORE_DIRECTORY)
    collections = client.list_collections()
    collections = list(filter(lambda x:x.name!="langchain", collections))
    collections.sort(key=lambda x:x.name)
    return collections
    