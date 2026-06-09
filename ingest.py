"""
Ingest and chunk the local Markdown document corpus.

This script implements the ingestion and chunking phase described in
planning.md:

- Load all Markdown files from documents/
- Split text into fixed 500-character chunks
- Use 100-character overlap between neighboring chunks
- Print five representative chunks for manual inspection
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


DOCUMENTS_DIR = Path("documents")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
SAMPLE_CHUNK_COUNT = 5


@dataclass(frozen=True)
class SourceDocument:
    """A source Markdown document loaded from disk."""

    path: Path
    text: str


@dataclass(frozen=True)
class TextChunk:
    """A fixed-size chunk with source metadata for retrieval/storage."""

    chunk_id: str
    text: str
    source_path: str
    chunk_index: int
    start_char: int
    end_char: int

    def metadata(self) -> dict:
        """Return metadata in a shape that can be stored in a vector DB later."""
        return {
            "source_path": self.source_path,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
        }


def load_markdown_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[SourceDocument]:
    """Load every Markdown file in the documents directory."""
    if not documents_dir.exists():
        raise FileNotFoundError(f"Documents directory not found: {documents_dir}")

    paths = sorted(documents_dir.glob("*.md"))
    documents = []

    for path in paths:
        text = path.read_text(encoding="utf-8")
        if text.strip():
            documents.append(SourceDocument(path=path, text=text))

    return documents


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[tuple[str, int, int]]:
    """
    Split text into fixed-size character chunks with overlap.

    Returns tuples of (chunk_text, start_char, end_char). Leading and trailing
    whitespace is stripped from each chunk for cleaner retrieval text.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if overlap < 0:
        raise ValueError("overlap must be greater than or equal to 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []
    step_size = chunk_size - overlap
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append((chunk, start, end))

        if end == len(text):
            break

        start += step_size

    return chunks


def chunk_documents(
    documents: list[SourceDocument],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[TextChunk]:
    """Chunk all loaded documents and attach source metadata."""
    chunks = []

    for document in documents:
        document_chunks = chunk_text(
            text=document.text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_index, (chunk, start_char, end_char) in enumerate(document_chunks):
            chunk_id = f"{document.path.stem}-{chunk_index:04d}"
            chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    text=chunk,
                    source_path=str(document.path),
                    chunk_index=chunk_index,
                    start_char=start_char,
                    end_char=end_char,
                )
            )

    return chunks


def representative_chunks(
    chunks: list[TextChunk],
    sample_count: int = SAMPLE_CHUNK_COUNT,
) -> list[TextChunk]:
    """Pick chunks evenly across the full chunk list for debugging."""
    if sample_count <= 0:
        return []
    if len(chunks) <= sample_count:
        return chunks

    max_index = len(chunks) - 1
    indices = [
        round(i * max_index / (sample_count - 1))
        for i in range(sample_count)
    ]

    return [chunks[index] for index in indices]


def print_chunk_samples(chunks: list[TextChunk], sample_count: int) -> None:
    """Print representative chunks for manual inspection."""
    samples = representative_chunks(chunks, sample_count=sample_count)

    for sample_number, chunk in enumerate(samples, start=1):
        print("=" * 80)
        print(f"Sample chunk {sample_number}/{len(samples)}")
        print(f"Chunk ID: {chunk.chunk_id}")
        print(f"Source:   {chunk.source_path}")
        print(f"Chars:    {chunk.start_char}-{chunk.end_char}")
        print("-" * 80)
        print(chunk.text)
        print()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for local debugging."""
    parser = argparse.ArgumentParser(
        description="Load Markdown documents and split them into fixed-size chunks."
    )
    parser.add_argument(
        "--documents-dir",
        type=Path,
        default=DOCUMENTS_DIR,
        help="Directory containing Markdown source documents.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help="Chunk size in characters.",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=CHUNK_OVERLAP,
        help="Overlap between neighboring chunks in characters.",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=SAMPLE_CHUNK_COUNT,
        help="Number of representative chunks to print.",
    )
    return parser.parse_args()


def main() -> None:
    """Run ingestion and chunking, then print debug samples."""
    args = parse_args()

    documents = load_markdown_documents(args.documents_dir)
    chunks = chunk_documents(
        documents=documents,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )

    print(f"Loaded documents: {len(documents)}")
    print(f"Generated chunks: {len(chunks)}")
    print(f"Chunk size:       {args.chunk_size} characters")
    print(f"Overlap:          {args.overlap} characters")
    print()

    print_chunk_samples(chunks, sample_count=args.samples)


if __name__ == "__main__":
    main()
