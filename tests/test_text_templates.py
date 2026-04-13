"""Tests for text rendering helpers used by tickets and documents."""

from __future__ import annotations

import unittest

from scripts.random_utils import SeededRandom
from scripts.seed_loader import load_seed_bundle
from scripts.text_templates import render_document, render_ticket_description


class TextTemplatesTestCase(unittest.TestCase):
    """Ensure generated texts are not empty and interpolate placeholders."""

    def test_ticket_description_renders_placeholders(self) -> None:
        """Ticket templates should interpolate dynamic fields."""

        seeds = load_seed_bundle()
        text = render_ticket_description(
            seeds.ticket_templates,
            "pix",
            {
                "valor_formatado": "R$ 120.00",
                "momento": "01/03/2026 10:10",
                "status": "em analise",
                "periodo": "ontem",
                "erro": "erro temporario",
                "evento": "login",
                "prazo": "24",
                "produto": "Produto X",
                "estabelecimento": "Loja X",
            },
            SeededRandom(42, "ticket-template"),
        )
        self.assertIn("R$ 120.00", text)
        self.assertTrue(text.strip())

    def test_document_render_contains_sections(self) -> None:
        """Documents should keep the agreed internal structure."""

        seeds = load_seed_bundle()
        document = render_document(
            "politica_pix",
            seeds.document_topics["politicas"]["politica_pix"],
            "CDB Liquidez Diaria",
            SeededRandom(42, "document-template"),
        )
        self.assertIn("## Objetivo", document)
        self.assertIn("## Regras", document)
        self.assertIn("CDB Liquidez Diaria", document)


if __name__ == "__main__":
    unittest.main()
