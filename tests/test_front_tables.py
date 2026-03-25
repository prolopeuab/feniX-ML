import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "app"))

from tei_backend import convert_docx_to_tei  # noqa: E402


class FrontTablesTest(unittest.TestCase):
    def test_tables_keep_document_order_and_minimal_markup(self):
        xml = convert_docx_to_tei(
            main_docx=str(REPO_ROOT / "test" / "test_prologoycomedia.docx"),
            save=False
        )

        estudio_head = '<head type="divTitle" subtype="MenuLevel_2">Estudio'
        sinopsis_head = '<head type="divTitle" subtype="MenuLevel_2">Sinopsis de la versificación</head>'
        generic_table = '          <table>'
        versification_table = '          <table type="sinopsisversificacion">'

        estudio_pos = xml.index(estudio_head)
        generic_table_pos = xml.index(generic_table)
        sinopsis_pos = xml.index(sinopsis_head)
        versification_pos = xml.index(versification_table)

        self.assertLess(estudio_pos, generic_table_pos)
        self.assertLess(generic_table_pos, sinopsis_pos)
        self.assertLess(sinopsis_pos, versification_pos)

        self.assertEqual(xml.count('type="sinopsisversificacion"'), 1)
        self.assertNotIn('style="', xml)

        generic_table_xml = xml[generic_table_pos:xml.index('          </table>', generic_table_pos) + len('          </table>')]
        self.assertNotIn('type="sinopsisversificacion"', generic_table_xml)
        self.assertNotIn('cols="3"', generic_table_xml)
        self.assertNotIn('rend="summary"', generic_table_xml)

        versification_table_xml = xml[versification_pos:xml.index('          </table>', versification_pos) + len('          </table>')]
        self.assertIn('cols="3"', versification_table_xml)
        self.assertIn('rend="summary"', versification_table_xml)


if __name__ == "__main__":
    unittest.main()
