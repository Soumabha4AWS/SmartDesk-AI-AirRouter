from pathlib import Path
from typing import Callable
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


def build_rag_pipeline(
    documents_dir: Path,
    collection_name: str,
    chunk_size: int,
    chunk_overlap: int,
    top_k: int,
    api_key: str,
    base_url: str,
):
    """Build core RAG components: docs -> chunks -> embeddings -> vectorstore -> retriever.

    Returns a dict with: vectorstore, retriever, format_docs.
    """
    # Load documents
    document_files = [
        "hr-policies.md", "it-support.md",
        "onboarding.md", "payroll.md",
    ]
    all_documents = []
    for filename in document_files:
        content = (documents_dir / filename).read_text(encoding="utf-8")
        all_documents.append(Document(page_content=content, metadata={"source": filename}))

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(all_documents)

    # Embed and store in Chroma
    embeddings = OpenAIEmbeddings(
        model="openai/text-embedding-3-small",
        api_key=api_key,
        base_url=base_url,
        check_embedding_ctx_length=False,
    )
    vectorstore = Chroma.from_documents(
        chunks, embeddings, collection_name=collection_name
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})

    def format_docs(docs):
        return "\n\n---\n\n".join(
            f"[{doc.metadata.get('source', '')}]\n{doc.page_content}"
            for doc in docs
        )

    return {
        "vectorstore": vectorstore,
        "retriever": retriever,
        "format_docs": format_docs,
    }
