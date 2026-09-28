import tempfile
import unittest
from pathlib import Path

from core.database import CrawlDB
from core.duplicate import DuplicateDetector
from core.extractor import extract_links, parse_page
from core.frontier import URLFrontier
from core.preprocessor import preprocess_document
from core.profile_loader import load_group, load_site
from core.url_tools import is_allowed_url, normalize_url

ROOT = Path(__file__).resolve().parents[1]


class FrontierTests(unittest.TestCase):
    def test_bfs_fifo(self):
        f = URLFrontier()
        self.assertTrue(f.add("A", 0))
        self.assertTrue(f.add("B", 1))
        self.assertTrue(f.add("C", 1))
        self.assertEqual(f.pop().url, "A")
        self.assertEqual(f.pop().url, "B")
        self.assertEqual(f.pop().url, "C")

    def test_queue_and_visited_duplicate(self):
        f = URLFrontier()
        self.assertTrue(f.add("A", 0))
        self.assertFalse(f.add("A", 1))
        item = f.pop()
        f.mark_visited(item.url)
        self.assertFalse(f.add("A", 2))


class ActiveProfileTests(unittest.TestCase):
    def test_group_has_five_active_sites(self):
        self.assertEqual(
            load_group(ROOT, "vire_web_corpus"),
            [
                "mobifone_5g_faq",
                "momo_help",
                "fpt_telecom_support",
                "uel_admissions_faq",
                "hcmus_admissions",
            ],
        )

    def test_momo_scope_and_self_link(self):
        profile = load_site(ROOT, "momo_help")
        html = b"""
        <html><body>
          <a href='/hoi-dap/vi-sao-giao-dich-that-bai'>FAQ</a>
          <a href='/blog/promo'>Blog</a>
          <a href='/hoi-dap'>Self</a>
        </body></html>
        """
        parsed = parse_page(html, "https://www.momo.vn/hoi-dap", profile)
        links, rejected = extract_links(
            parsed["soup"], "https://www.momo.vn/hoi-dap", profile
        )
        self.assertEqual(
            links,
            ["https://www.momo.vn/hoi-dap/vi-sao-giao-dich-that-bai"],
        )
        self.assertGreaterEqual(rejected.get("self_link", 0), 1)

    def test_hcmus_scope(self):
        profile = load_site(ROOT, "hcmus_admissions")
        html = b"""
        <html><body>
          <a href='/hoc-phi/'>Hoc phi</a>
          <a href='/cau-hoi-thuong-gap/'>FAQ</a>
          <a href='/gioi-thieu-chung/'>About</a>
        </body></html>
        """
        parsed = parse_page(html, "https://tuyensinh.hcmus.edu.vn/", profile)
        links, _ = extract_links(
            parsed["soup"], "https://tuyensinh.hcmus.edu.vn/", profile
        )
        self.assertIn("https://tuyensinh.hcmus.edu.vn/hoc-phi/", links)
        self.assertIn(
            "https://tuyensinh.hcmus.edu.vn/cau-hoi-thuong-gap/", links
        )
        self.assertNotIn(
            "https://tuyensinh.hcmus.edu.vn/gioi-thieu-chung/", links
        )

    def test_fpt_rejects_sports_paths(self):
        profile = load_site(ROOT, "fpt_telecom_support")
        self.assertFalse(
            is_allowed_url("https://fpt.vn/tin-tuc/the-thao/", profile)[0]
        )
        self.assertTrue(
            is_allowed_url(
                "https://fpt.vn/tin-tuc/toc-do-mang-cham-bat-thuong-10460.html",
                profile,
            )[0]
        )


class PreprocessTests(unittest.TestCase):
    def test_customer_support_document_accept(self):
        profile = load_site(ROOT, "momo_help")
        text = (
            "Nếu giao dịch thanh toán không thành công, khách hàng kiểm tra số dư "
            "tài khoản và ngân hàng liên kết. Nếu vẫn lỗi, liên hệ bộ phận hỗ trợ. "
        ) * 18
        p = preprocess_document("Vì sao giao dịch thanh toán không thành công?", text, profile)
        self.assertTrue(p.valid)
        self.assertGreaterEqual(len(p.passages), 1)

    def test_irrelevant_document_reject(self):
        profile = load_site(ROOT, "fpt_telecom_support")
        text = ("Đội bóng thi đấu và giành chiến thắng trong trận chung kết. " * 30)
        p = preprocess_document("Kết quả bóng đá hôm nay", text, profile)
        self.assertFalse(p.valid)


class URLAndDuplicateTests(unittest.TestCase):
    def test_normalize_tracking_query(self):
        profile = load_site(ROOT, "momo_help")
        u = normalize_url(
            "/hoi-dap/demo?utm_source=x#abc",
            "https://www.momo.vn/hoi-dap",
            profile,
        )
        self.assertEqual(u, "https://www.momo.vn/hoi-dap/demo")
        self.assertTrue(is_allowed_url(u, profile)[0])

    def test_sha_duplicate(self):
        d = DuplicateDetector()
        self.assertFalse(d.check_and_add("same text")[0])
        self.assertTrue(d.check_and_add("same text")[0])


class DatabaseResumeTests(unittest.TestCase):
    def test_persistent_frontier_state(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "test.db"
            db = CrawlDB(path)
            db.discover_url("https://example.com/", 0)
            db.discover_url(
                "https://example.com/a",
                1,
                "https://example.com/",
            )
            db.mark_url_done("https://example.com/", "visited")
            db.conn.commit()

            self.assertEqual(
                db.queued_urls(),
                [("https://example.com/a", 1)],
            )
            self.assertIn(
                "https://example.com/",
                db.visited_urls(),
            )
            db.close()


if __name__ == "__main__":
    unittest.main()
