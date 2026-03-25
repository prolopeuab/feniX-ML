import sys
import unittest
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "app"))

from tei_backend import convert_docx_to_tei  # noqa: E402


class FrontLinksTest(unittest.TestCase):
    @staticmethod
    def _ensure_paragraph_style(doc: Document, style_name: str) -> None:
        styles = doc.styles
        try:
            styles[style_name]
        except KeyError:
            styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)

    @staticmethod
    def _append_hyperlink(paragraph, url: str, runs: list[tuple[str, bool]]) -> None:
        relationship_id = paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True)

        hyperlink = OxmlElement("w:hyperlink")
        hyperlink.set(qn("r:id"), relationship_id)

        for text, italic in runs:
            run = OxmlElement("w:r")
            if italic:
                run_properties = OxmlElement("w:rPr")
                italic_node = OxmlElement("w:i")
                run_properties.append(italic_node)
                run.append(run_properties)

            text_node = OxmlElement("w:t")
            if text != text.strip():
                text_node.set(qn("xml:space"), "preserve")
            text_node.text = text
            run.append(text_node)
            hyperlink.append(run)

        paragraph._p.append(hyperlink)

    def _build_test_docx(self, output_path: Path) -> None:
        doc = Document()

        for style_name in ["Quote", "Acot", "Titulo_comedia", "Acto", "Personaje", "Verso"]:
            self._ensure_paragraph_style(doc, style_name)

        doc.add_paragraph("Prólogo")

        para = doc.add_paragraph()
        para.add_run("Consulta ")
        self._append_hyperlink(para, "https://ejemplo.org", [("la web", False)])
        para.add_run(" hoy.")

        para = doc.add_paragraph()
        para.style = "Quote"
        para.add_run("Según ")
        self._append_hyperlink(
            para,
            "https://cita.example",
            [("esta", False), (" cita", True)],
        )

        para = doc.add_paragraph()
        para.style = "Acot"
        para.add_run("Sale con ")
        self._append_hyperlink(para, "https://acot.example", [("sigilo", False)])

        table = doc.add_table(rows=1, cols=1)
        cell_para = table.cell(0, 0).paragraphs[0]
        cell_para.add_run("Tabla con ")
        self._append_hyperlink(
            cell_para,
            "https://tabla.example",
            [("enlace", False), (" en cursiva", True)],
        )

        para = doc.add_paragraph("TÍTULO DE LA COMEDIA")
        para.style = "Titulo_comedia"

        para = doc.add_paragraph("ACTO PRIMERO")
        para.style = "Acto"

        para = doc.add_paragraph("PERSONAJE")
        para.style = "Personaje"

        para = doc.add_paragraph("verso del cuerpo")
        para.style = "Verso"

        doc.save(output_path)

        empty_footnotes = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'
        )
        with zipfile.ZipFile(output_path, "a") as docx_zip:
            docx_zip.writestr("word/footnotes.xml", empty_footnotes)

    def test_front_hyperlinks_become_tei_refs(self):
        with TemporaryDirectory() as tmp_dir:
            docx_path = Path(tmp_dir) / "test_front_links.docx"
            self._build_test_docx(docx_path)
            xml = convert_docx_to_tei(main_docx=str(docx_path), save=False)

        front_start = xml.index('<front xml:id="front">')
        front_end = xml.index('    </front>')
        front_xml = xml[front_start:front_end]

        self.assertIn(
            '<p>Consulta <ref target="https://ejemplo.org">la web</ref> hoy.</p>',
            front_xml,
        )
        self.assertIn(
            '<quote>Según <ref target="https://cita.example">esta<hi rend="italic"> cita</hi></ref></quote>',
            front_xml,
        )
        self.assertIn(
            '<stage>Sale con <ref target="https://acot.example">sigilo</ref></stage>',
            front_xml,
        )
        self.assertIn(
            '<ref target="https://tabla.example">enlace<hi rend="italic"> en cursiva</hi></ref>',
            front_xml,
        )

        body_start = xml.index('<body xml:id="body">')
        body_xml = xml[body_start:]
        self.assertIn('<l n="1">verso del cuerpo</l>', body_xml)


if __name__ == "__main__":
    unittest.main()
