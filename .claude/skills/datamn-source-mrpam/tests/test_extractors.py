import importlib.util
import tempfile
import unittest
from pathlib import Path

import pandas as pd


SKILL_DIR = Path(__file__).resolve().parents[1]


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, SKILL_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extract = load_module("mrpam_extract", "extract_tables.py")
fetch = load_module("mrpam_fetch", "fetch_report.py")


class FakePage:
    def __init__(self, text, words=None):
        self._text = text
        self._words = words or []

    def extract_text(self):
        return self._text

    def extract_words(self):
        return self._words


class FakePdf:
    def __init__(self, *pages):
        self.pages = list(pages)


class FakeAnchor:
    def __init__(self, text):
        self.text = text

    def get_text(self, separator=" ", strip=False):
        return self.text.strip() if strip else self.text

    def find_parent(self, name):
        return None


class FilenameTests(unittest.TestCase):
    def test_2026_opendata_filenames(self):
        cases = {
            "2026.04opendata_%281%29.pdf": (2026, 4),
            "2026.05opendata.pdf": (2026, 5),
            "2026.06%20opendata%20%284%29.pdf": (2026, 6),
        }
        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                self.assertEqual(
                    extract.parse_year_month_from_filename(filename), expected
                )

    def test_mongolian_dash_month_label(self):
        anchor = FakeAnchor("Статистикийн мэдээ 6-р сар")
        self.assertEqual(fetch._guess_month("report.pdf", anchor, 2026), 6)

    def test_two_digit_mongolian_month_is_not_misread(self):
        anchor = FakeAnchor("Статистикийн мэдээ 11 сар")
        self.assertEqual(fetch._guess_month("report.pdf", anchor, 2026), 11)

    def test_cached_encoded_duplicates_collapse_to_one_month(self):
        with tempfile.TemporaryDirectory() as directory:
            year_dir = Path(directory) / "2026"
            year_dir.mkdir()
            for filename in [
                "2026.06%20opendata%20%284%29.pdf",
                "2026.06 opendata (4).pdf",
            ]:
                (year_dir / filename).touch()
            paths = extract.collect_pdfs_for_year(2026, Path(directory))

        self.assertEqual([path.name for path in paths], ["2026.06 opendata (4).pdf"])


class ExtractorTests(unittest.TestCase):
    def test_petroleum_imports_preserve_empty_product_column(self):
        words = [{"text": "2026.VI", "x0": 37, "top": 100}]
        values = [
            (86, "221,575"), (144, "57,353"), (209, "521"),
            # AI-95 at x=262 is intentionally empty.
            (316, "114,874"), (382, "21,574"), (443, "5,253"),
            (493, "4,043"), (540, "17,957"),
        ]
        words.extend({"text": text, "x0": x, "top": 100} for x, text in values)
        page = FakePage(
            "ГАЗРЫН ТОСНЫ БҮТЭЭГДЭХҮҮНИЙ ИМПОРТ Евро-5",
            words,
        )
        frame = extract.extract_petroleum_imports(FakePdf(page), 2026, 6)

        self.assertEqual(len(frame), 9)
        self.assertTrue(pd.isna(frame.loc[3, "volume_t"]))
        self.assertEqual(frame.loc[4, "volume_t"], 114874)
        self.assertEqual(frame.loc[8, "volume_t"], 17957)

    def test_petroleum_imports_use_historical_product_positions(self):
        words = [{"text": "2024.I", "x0": 70, "top": 100}]
        values = [
            (115, "231,404"), (174, "1,740"), (224, "78,421"),
            (278, "2,492"), (338, "0"), (379, "129,542"),
            (431, "8,552"), (479, "3,022"), (526, "7,635"),
        ]
        words.extend({"text": text, "x0": x, "top": 100} for x, text in values)
        page = FakePage(
            "ГАЗРЫН ТОСНЫ БҮТЭЭГДЭХҮҮНИЙ ИМПОРТ АИ-98",
            words,
        )
        frame = extract.extract_petroleum_imports(FakePdf(page), 2024, 1)

        self.assertEqual(frame.loc[1, "product"], "Автобензин А-80")
        self.assertEqual(frame.loc[2, "product"], "Автобензин АИ-92")
        self.assertEqual(frame.loc[4, "product"], "Автобензин АИ-98")
        self.assertEqual(frame.loc[5, "volume_t"], 129542)

    def test_mining_permits_clean_names_and_keep_thousand_hectares(self):
        text = "\n".join([
            "1.1. ТУСГАЙ ЗӨВШӨӨРӨЛ хайгуулын",
            "Говь-Aлтай 148 642.0 4.5% 65 79.1 0.6% 83 562.9 4.0%",
        ])
        frame = extract.extract_mining_permits(FakePdf(FakePage(text)), 2026, 6)

        self.assertEqual(frame.loc[0, "province"], "Говь-Алтай")
        self.assertEqual(frame.loc[0, "total_area_kha"], 642.0)
        self.assertEqual(frame.loc[0, "extraction_count"], 65)
        self.assertEqual(frame.loc[0, "exploration_area_kha"], 562.9)

    def test_fuel_uses_current_value_bands_and_missing_placeholders(self):
        words = []
        provinces = [
            name for name in extract._PROVINCE_MN_EN
            if name not in {"Улсын дундаж", "Говь-Алтай"}
        ][:20]
        for top, province in enumerate(provinces, start=1):
            words.extend([
                {"text": province, "x0": 57, "top": top * 10},
                {"text": "2,700", "x0": 143, "top": top * 10},
                {"text": "-", "x0": 238, "top": top * 10},
                {"text": "4,240", "x0": 324, "top": top * 10},
                {"text": "4,570", "x0": 415, "top": top * 10},
                {"text": "5,170", "x0": 505, "top": top * 10},
            ])
        page = FakePage(
            "4.6. ГАЗРЫН ТОСНЫ БҮТЭЭГДЭХҮҮНИЙ ЖИЖИГЛЭН", words
        )
        frame = extract.extract_fuel_prices(FakePdf(page), 2026, 6)

        self.assertEqual(len(frame), 20)
        self.assertEqual(frame.loc[0, "ai92_price"], 2700)
        self.assertTrue(pd.isna(frame.loc[0, "ai92_euro5_price"]))
        self.assertEqual(frame.loc[0, "diesel_price"], 4570)

    def test_bilingual_output_translates_categories_only_in_english(self):
        frame = pd.DataFrame([{
            "year": 2026, "month": 6, "product": "Дизелийн түлш",
            "volume_t": 114874,
        }])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            extract.save_bilingual(frame, "mrpam-petroleum-imports", output)
            en = pd.read_csv(output / "mrpam-petroleum-imports-en.csv")
            mn = pd.read_csv(output / "mrpam-petroleum-imports-mn.csv")

        self.assertEqual(en.loc[0, "product"], "Diesel fuel")
        self.assertEqual(mn.loc[0, "бүтээгдэхүүн"], "Дизелийн түлш")
        self.assertEqual(en.loc[0, "volume_t"], mn.loc[0, "хэмжээ_тн"])


if __name__ == "__main__":
    unittest.main()
