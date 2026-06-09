"""
Embed, store, and retrieve chunks with ChromaDB.

This module implements the embedding, vector storage, and retrieval stage from
planning.md:

- Embed chunks with all-MiniLM-L6-v2 via sentence-transformers
- Store chunk text, embeddings, ids, and metadata in a local ChromaDB database
- Embed user questions with the same model
- Retrieve the top 5 most similar chunks for a query
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import chromadb
from sentence_transformers import SentenceTransformer

from ingest import TextChunk, chunk_documents, load_markdown_documents


MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_DB_DIR = Path("chroma_db")
COLLECTION_NAME = "bu_housing_chunks"
TOP_K = 5
DEBUG_QUERY = "Which freshman dorm has the best social life in BU?"


@dataclass(frozen=True)
class RetrievedChunk:
    """A chunk returned by vector similarity search."""

    chunk_id: str
    text: str
    metadata: dict
    distance: float | None


def load_embedding_model(
    model_name: str = MODEL_NAME,
    local_files_only: bool = False,
) -> SentenceTransformer:
    """Load the sentence-transformers embedding model."""
    return SentenceTransformer(model_name, local_files_only=local_files_only)


def embed_texts(
    texts: Sequence[str],
    model: SentenceTransformer,
) -> list[list[float]]:
    """
    Embed a batch of texts using the configured embedding model.

    The same function is used for source chunks and future user queries so both
    are represented in the same vector space.
    """
    if not texts:
        return []

    embeddings = model.encode(
        list(texts),
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return embeddings.tolist()


def embed_query(query: str, model: SentenceTransformer) -> list[float]:
    """Embed a single user query."""
    return embed_texts([query], model)[0]


def get_chroma_client(db_dir: Path = CHROMA_DB_DIR) -> chromadb.PersistentClient:
    """Create a persistent local ChromaDB client."""
    return chromadb.PersistentClient(path=str(db_dir))


def get_or_create_collection(
    client: chromadb.PersistentClient,
    collection_name: str = COLLECTION_NAME,
):
    """Get the local ChromaDB collection used for BU housing chunks."""
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def load_chunks_from_documents() -> list[TextChunk]:
    """Load Markdown documents through ingest.py and return prepared chunks."""
    documents = load_markdown_documents()
    return chunk_documents(documents)


def store_chunks(
    chunks: Sequence[TextChunk],
    collection,
    model: SentenceTransformer,
) -> None:
    """
    Embed chunks and upsert them into ChromaDB.

    Upsert keeps the script idempotent: running database.py again updates the
    same chunk ids instead of failing on duplicate ids.
    """
    if not chunks:
        return

    documents = [chunk.text for chunk in chunks]
    embeddings = embed_texts(documents, model)

    collection.upsert(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=documents,
        embeddings=embeddings,
        metadatas=[chunk.metadata() for chunk in chunks],
    )


def build_vector_store(
    db_dir: Path = CHROMA_DB_DIR,
    collection_name: str = COLLECTION_NAME,
    model_name: str = MODEL_NAME,
    local_files_only: bool = False,
):
    """Load chunks, embed them, and store them in a persistent ChromaDB collection."""
    chunks = load_chunks_from_documents()
    model = load_embedding_model(
        model_name=model_name,
        local_files_only=local_files_only,
    )
    client = get_chroma_client(db_dir)
    collection = get_or_create_collection(client, collection_name)
    store_chunks(chunks, collection, model)
    return collection, model, chunks


def retrieve_similar_chunks_by_embedding(
    query_embedding: Sequence[float],
    collection,
    top_k: int = TOP_K,
) -> list[RetrievedChunk]:
    """Retrieve the top-k chunks most similar to a precomputed query embedding."""
    results = collection.query(
        query_embeddings=[list(query_embedding)],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved = []
    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        retrieved.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                text=document,
                metadata=metadata,
                distance=distance,
            )
        )

    return retrieved


def retrieve_similar_chunks(
    query: str,
    collection,
    model: SentenceTransformer,
    top_k: int = TOP_K,
) -> list[RetrievedChunk]:
    """Embed a user query and retrieve the top-k most similar chunks."""
    query_embedding = embed_query(query, model)
    return retrieve_similar_chunks_by_embedding(
        query_embedding=query_embedding,
        collection=collection,
        top_k=top_k,
    )


def print_retrieval_results(query: str, chunks: Sequence[RetrievedChunk]) -> None:
    """Print retrieved chunks for manual debugging."""
    print(f"Debug query: {query}")
    print(f"Retrieved chunks: {len(chunks)}")
    print()

    for index, chunk in enumerate(chunks, start=1):
        print("=" * 80)
        print(f"Result {index}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Distance: {chunk.distance}")
        print(f"Source:   {chunk.metadata.get('source_path')}")
        print(
            "Chars:    "
            f"{chunk.metadata.get('start_char')}-{chunk.metadata.get('end_char')}"
        )
        print("-" * 80)
        print(chunk.text)
        print()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for building/querying the vector store."""
    parser = argparse.ArgumentParser(
        description="Embed Markdown chunks into ChromaDB and test retrieval."
    )
    parser.add_argument(
        "--query",
        default=DEBUG_QUERY,
        help="Debug query to retrieve similar chunks for.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K,
        help="Number of chunks to retrieve.",
    )
    parser.add_argument(
        "--db-dir",
        type=Path,
        default=CHROMA_DB_DIR,
        help="Directory for persistent ChromaDB storage.",
    )
    parser.add_argument(
        "--collection",
        default=COLLECTION_NAME,
        help="ChromaDB collection name.",
    )
    parser.add_argument(
        "--model",
        default=MODEL_NAME,
        help="Sentence-transformers model name.",
    )
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Load the embedding model only from the local Hugging Face cache.",
    )
    return parser.parse_args()


def main() -> None:
    """Build/update the vector store, then run one debug retrieval query."""
    args = parse_args()

    collection, model, chunks = build_vector_store(
        db_dir=args.db_dir,
        collection_name=args.collection,
        model_name=args.model,
        local_files_only=args.local_files_only,
    )

    print(f"Loaded chunks:      {len(chunks)}")
    print(f"ChromaDB path:      {args.db_dir}")
    print(f"Collection:         {args.collection}")
    print(f"Collection count:   {collection.count()}")
    print(f"Embedding model:    {args.model}")
    print(f"Top-k:              {args.top_k}")
    print()

    retrieved = retrieve_similar_chunks(
        query=args.query,
        collection=collection,
        model=model,
        top_k=args.top_k,
    )
    print_retrieval_results(args.query, retrieved)


if __name__ == "__main__":
    main()
