"""
Gradio interface and grounded generation for the BU housing RAG app.

This file implements Milestone 5 from planning.md:

- Accept a user question through a Gradio web UI
- Retrieve the top 5 relevant chunks from ChromaDB
- Send those chunks to Groq's llama-3.3-70b-versatile model
- Return a grounded answer with source context for inspection
"""

from __future__ import annotations

import argparse
import os
from functools import lru_cache
from typing import Sequence

import gradio as gr
from dotenv import load_dotenv
from groq import Groq

from database import (
    CHROMA_DB_DIR,
    COLLECTION_NAME,
    MODEL_NAME,
    TOP_K,
    RetrievedChunk,
    get_chroma_client,
    get_or_create_collection,
    load_chunks_from_documents,
    load_embedding_model,
    retrieve_similar_chunks,
    store_chunks,
)


GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_CONTEXT_CHARS_PER_CHUNK = 900
MAX_ANSWER_TOKENS = 500
SOURCE_COLUMNS = ["Rank", "Distance", "Source", "Chunk ID", "Preview"]
APP_THEME = gr.themes.Soft(
    primary_hue="red",
    neutral_hue="slate",
    radius_size="sm",
)


SYSTEM_PROMPT = """
You answer questions about Boston University on-campus housing.
Use only the retrieved source chunks provided by the system.
If the chunks do not contain enough information, say that the sources do not
provide enough evidence.
Keep the answer concise and practical.
Mention relevant caveats when the source chunks disagree.
End with a short "Sources:" line listing the chunk numbers you used.
""".strip()


EXAMPLE_QUESTIONS = [
    "Which freshman dorm is the most convenient in BU?",
    "Which freshman dorm has the best social life in BU?",
    "I am an introvert and want to socialize. Is HoJo or Warren better?",
    "Is StuVi worth the extra money to live at?",
    "Is Fenway worth the additional distance from the main campus?",
]


@lru_cache(maxsize=1)
def get_retriever_resources():
    """Load the local embedding model and ChromaDB collection once."""
    model = load_embedding_model(MODEL_NAME, local_files_only=True)
    client = get_chroma_client(CHROMA_DB_DIR)
    collection = get_or_create_collection(client, COLLECTION_NAME)

    if collection.count() == 0:
        chunks = load_chunks_from_documents()
        store_chunks(chunks, collection, model)

    return collection, model


@lru_cache(maxsize=1)
def get_groq_client() -> Groq:
    """Create a Groq client from the local .env file."""
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing from .env")
    return Groq(api_key=api_key)


def clean_preview(text: str, limit: int = 260) -> str:
    """Collapse whitespace and shorten source text for UI display."""
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def format_context(chunks: Sequence[RetrievedChunk]) -> str:
    """Format retrieved chunks for the LLM prompt."""
    context_blocks = []

    for index, chunk in enumerate(chunks, start=1):
        source_path = chunk.metadata.get("source_path", "unknown source")
        start_char = chunk.metadata.get("start_char", "?")
        end_char = chunk.metadata.get("end_char", "?")
        text = chunk.text[:MAX_CONTEXT_CHARS_PER_CHUNK]
        context_blocks.append(
            "\n".join(
                [
                    f"[{index}] source={source_path}",
                    f"chunk_id={chunk.chunk_id}",
                    f"chars={start_char}-{end_char}",
                    f"distance={chunk.distance}",
                    text,
                ]
            )
        )

    return "\n\n".join(context_blocks)


def source_rows(chunks: Sequence[RetrievedChunk]) -> list[list[object]]:
    """Convert retrieved chunks into a Gradio DataFrame-friendly shape."""
    rows = []

    for index, chunk in enumerate(chunks, start=1):
        distance = round(chunk.distance, 6) if chunk.distance is not None else None
        rows.append(
            [
                index,
                distance,
                chunk.metadata.get("source_path", ""),
                chunk.chunk_id,
                clean_preview(chunk.text),
            ]
        )

    return rows


def generate_grounded_answer(question: str, chunks: Sequence[RetrievedChunk]) -> str:
    """Generate an answer from retrieved context using Groq."""
    context = format_context(chunks)
    user_prompt = f"""
Question:
{question}

Retrieved source chunks:
{context}
""".strip()

    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=MAX_ANSWER_TOKENS,
    )
    return response.choices[0].message.content.strip()


def answer_question(question: str) -> tuple[str, list[list[object]]]:
    """Retrieve relevant chunks and generate a grounded answer."""
    question = question.strip()
    if not question:
        return "Enter a question about BU housing.", []

    collection, model = get_retriever_resources()
    chunks = retrieve_similar_chunks(
        query=question,
        collection=collection,
        model=model,
        top_k=TOP_K,
    )

    if not chunks:
        return "No relevant chunks were retrieved.", []

    try:
        answer = generate_grounded_answer(question, chunks)
    except Exception as exc:
        answer = (
            "Generation failed. The retrieved chunks are shown below for debugging.\n\n"
            f"Error: {exc}"
        )

    return answer, source_rows(chunks)


def build_app() -> gr.Blocks:
    """Build the Gradio app."""
    with gr.Blocks(title="BU Housing Guide") as app:
        gr.Markdown("# BU Housing Guide")

        with gr.Row():
            question = gr.Textbox(
                label="Question",
                placeholder="Ask about BU freshman dorms, location, social life, bathrooms, dining, or cost.",
                lines=3,
                scale=5,
            )
            submit = gr.Button("Ask", variant="primary", scale=1)

        gr.Examples(
            examples=EXAMPLE_QUESTIONS,
            inputs=question,
            label="Examples",
        )

        answer = gr.Markdown(label="Answer")
        sources = gr.Dataframe(
            headers=SOURCE_COLUMNS,
            datatype=["number", "number", "str", "str", "str"],
            label="Retrieved Sources",
            interactive=False,
            wrap=True,
        )

        submit.click(
            fn=answer_question,
            inputs=question,
            outputs=[answer, sources],
        )
        question.submit(
            fn=answer_question,
            inputs=question,
            outputs=[answer, sources],
        )

    return app


def parse_args() -> argparse.Namespace:
    """Parse CLI options for local development."""
    parser = argparse.ArgumentParser(description="Run the BU housing RAG UI.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind Gradio to.")
    parser.add_argument("--port", type=int, default=7860, help="Port for Gradio.")
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio share link.",
    )
    return parser.parse_args()


def main() -> None:
    """Launch the Gradio UI."""
    args = parse_args()
    app = build_app()
    app.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        theme=APP_THEME,
    )


if __name__ == "__main__":
    main()
