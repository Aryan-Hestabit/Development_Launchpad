from src.retriever.hybrid_retriever import HybridRetriever


def build_context(documents):
    context_blocks = []

    for i, doc in enumerate(documents, 1):
        block = (
            f"[Source {i}] "
            f"(File: {doc.metadata.get('source')}, "
            f"Page: {doc.metadata.get('page', 'N/A')})\n"
            f"{doc.page_content}\n"
        )
        context_blocks.append(block)

    return "\n\n".join(context_blocks)


def main():
    retriever = HybridRetriever()

    while True:
        query = input("\nEnter your query (type 'exit' to quit): ")

        if query.lower() == "exit":
            print("Exiting.")
            break

        # Example filter structure
        filters = None
        # filters = {"year": "2024"}  # enable if metadata supports it

        documents = retriever.retrieve(
            query=query,
            top_k=5,
            filters=filters
        )

        context = build_context(documents)

        print("\n=== FINAL CONTEXT ===\n")
        print(context)
        print("=" * 80)


if __name__ == "__main__":
    main()