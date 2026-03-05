from langchain_community.vectorstores import Chroma
from llm.openai_client import embeddings


def get_retriever():

    vectorstore = Chroma.load_local(
        "vector_store",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore.as_retriever(search_kwargs={"k":3})