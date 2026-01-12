from langchain_community.vectorstores import FAISS


def build_vectorstore(documents, embeddings):
    """
    Build a FAISS vector store from documents and embeddings.
    """
    return FAISS.from_documents(documents, embeddings)
