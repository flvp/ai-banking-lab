"""Template helpers for ticket texts and RAG document generation."""

from __future__ import annotations

from typing import Iterable

from scripts.random_utils import SeededRandom


def render_ticket_description(
    template_group: dict,
    categoria: str,
    placeholders: dict[str, str],
    rng: SeededRandom,
) -> str:
    """Render a ticket description using one template and placeholders."""

    templates = template_group[categoria]["descricao"]
    template = rng.choice(templates)
    return template.format(**placeholders)


def render_ticket_summary(
    template_group: dict,
    categoria: str,
    placeholders: dict[str, str],
    rng: SeededRandom,
) -> str:
    """Render a short ticket summary."""

    template = rng.choice(template_group[categoria]["resumo"])
    return template.format(**placeholders)


def render_ticket_response(
    template_group: dict,
    categoria: str,
    placeholders: dict[str, str],
    rng: SeededRandom,
) -> str:
    """Render the final synthetic customer support response."""

    template = rng.choice(template_group[categoria]["resposta"])
    return template.format(**placeholders)


def build_document_sections(
    title: str,
    objective: str,
    scope: str,
    rules: Iterable[str],
    exceptions: Iterable[str],
    procedure: Iterable[str],
    examples: Iterable[str],
    observations: Iterable[str],
) -> str:
    """Build a Markdown document with a consistent internal structure."""

    return "\n".join(
        [
            f"# {title}",
            "",
            "## Objetivo",
            objective,
            "",
            "## Escopo",
            scope,
            "",
            "## Regras",
            *[f"- {item}" for item in rules],
            "",
            "## Excecoes",
            *[f"- {item}" for item in exceptions],
            "",
            "## Procedimento",
            *[f"{index}. {item}" for index, item in enumerate(procedure, start=1)],
            "",
            "## Exemplos",
            *[f"- {item}" for item in examples],
            "",
            "## Observacoes",
            *[f"- {item}" for item in observations],
        ]
    )


def render_document(
    topic_name: str,
    topic_data: dict,
    related_product: str,
    rng: SeededRandom,
) -> str:
    """Render one document from topic metadata and related product context."""

    objective = rng.choice(topic_data["objetivos"]).format(produto=related_product)
    scope = rng.choice(topic_data["escopos"]).format(produto=related_product)
    rules = [rule.format(produto=related_product) for rule in topic_data["regras"]]
    exceptions = [
        item.format(produto=related_product) for item in topic_data["excecoes"]
    ]
    procedure = [
        step.format(produto=related_product) for step in topic_data["procedimentos"]
    ]
    examples = [
        sample.format(produto=related_product) for sample in topic_data["exemplos"]
    ]
    observations = [
        note.format(produto=related_product) for note in topic_data["observacoes"]
    ]
    return build_document_sections(
        title=topic_name.replace("_", " ").title(),
        objective=objective,
        scope=scope,
        rules=rules,
        exceptions=exceptions,
        procedure=procedure,
        examples=examples,
        observations=observations,
    )
