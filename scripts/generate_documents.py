"""Generate Markdown and text documents used for RAG exercises."""

from __future__ import annotations

from collections import defaultdict

from scripts.config import DOCUMENT_TYPE_COUNTS, RunConfig
from scripts.io_utils import write_text_file
from scripts.random_utils import SeededRandom
from scripts.seed_loader import SeedBundle
from scripts.text_templates import render_document


def generate_documents(
    run_config: RunConfig,
    products: list[dict[str, str]],
    seeds: SeedBundle,
) -> list[str]:
    """Generate institutional documents linked to product themes."""

    rng = SeededRandom(run_config.seed, "documents")
    created_files: list[str] = []
    by_category = defaultdict(list)
    for product in products:
        by_category[product["categoria_produto"]].append(product["nome_produto"])
    topic_groups = seeds.document_topics
    remaining = run_config.scale.documents
    doc_types = list(topic_groups.items())
    for position, (doc_type, topics) in enumerate(doc_types):
        types_left = len(doc_types) - position
        default_count = DOCUMENT_TYPE_COUNTS.get(doc_type, 10)
        target_count = min(default_count, max(1, remaining // types_left))
        topic_names = list(topics)
        for index in range(target_count):
            topic_name = topic_names[index % len(topic_names)]
            product_names = by_category.get("cartao_credito") or by_category.get("investimento_renda_fixa")
            related_product = rng.choice(product_names)
            content = render_document(
                topic_name=topic_name,
                topic_data=topics[topic_name],
                related_product=related_product,
                rng=rng,
            )
            extension = ".txt" if doc_type == "regras_internas" and index % 3 == 0 else ".md"
            filename = f"{topic_name}_{index + 1}{extension}"
            output_path = run_config.documents_dir / doc_type / filename
            write_text_file(output_path, content)
            created_files.append(str(output_path))
        remaining -= target_count
    return created_files
