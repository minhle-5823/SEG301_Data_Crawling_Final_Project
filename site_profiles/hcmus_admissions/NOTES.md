# HCMUS Admissions & FAQ

## Nguồn và phạm vi

- Website chính thức: https://tuyensinh.hcmus.edu.vn/
- Domain duy nhất được crawl: `tuyensinh.hcmus.edu.vn`.
- Nội dung: tuyển sinh đại học, phương thức xét tuyển, chỉ tiêu, điểm chuẩn, ngành/chương trình đào tạo, học phí, học bổng, hồ sơ và nhập học, câu hỏi thường gặp, thông báo dành cho thí sinh. Bài viết năm 2024–2026 và trang ngành/nhóm ngành được phép đi theo liên kết.
- Seed URLs (đã kiểm tra HTTP 200 và liên kết từ trang chủ): `/`, `/cau-hoi-thuong-gap/`, `/thong-tin-tuyen-sinh-cac-nam/`, `/chi-tieu/`, `/phuong-thuc-tuyen-sinh/`, `/diem-chuan-2/`, `/hoc-phi/`, `/nganh-dao-tao/`, `/nganh-moi/`, `/hoc-bong/`, `/thong-tin-nhap-hoc/`.

`/diem-chuan/` trả HTTP 301 sang ảnh JPG; trang HTML được trang chủ liên kết là `/diem-chuan-2/`. Vì vậy profile dùng `/diem-chuan-2/` và không đưa `/diem-chuan/` vào seed/allowlist. Trang chủ còn liên kết bài `/2026-diem-chuan/`, chứa thông báo điểm chuẩn đầy đủ.

## Cấu hình dễ giải thích

- `allow_path_regex` chỉ cho phép các trang chủ đề trên, bài viết có slug `2024-`, `2025-`, `2026-`, các trang `nganh-`/`nhom-nganh-` và danh mục thông tin tuyển sinh tương ứng. Các trang ngoài phạm vi bị chặn trước khi vào BFS.
- `deny_path_regex` chặn khu vực quản trị, đăng nhập, feed, API và tài nguyên WordPress. Core cũng bỏ qua ảnh, PDF, CSS, JS và các file tĩnh theo `ignored_extensions` mặc định; domain ngoài luôn bị loại.
- Page types phân biệt `root`, `faq`, các trang chỉ tiêu/phương thức/điểm chuẩn/học phí/ngành/học bổng/nhập học, và `education_article`. Đây là nhãn mô tả trong DB, không phải crawler riêng.
- Title ưu tiên `.entry-title`, tiếp đến tiêu đề đầu trang `#content > div > h1`, rồi HTML `<title>`. Trang `/thong-tin-nhap-hoc/` dùng nhiều `<h1>` cho các mục I, II, III nên không lấy `h1` chung làm title. Nội dung lấy từ `main` (fallback `article`, `.entry-content`, `.site-main`, `body`) và bỏ `script`, `style`, menu, header, footer, form. Kiểm tra mẫu cho thấy FAQ và bài tuyển sinh giữ tiếng Việt có dấu, không chứa menu/footer đáng kể.
- Quality gate hiện có: tối thiểu 55 từ, 280 ký tự, Vietnamese score 0.35, relevance score 0.20 và 2 keyword hits. Toàn trang FAQ có 831 từ nên không bị loại nhầm. Hai trang chỉ gồm danh sách liên kết bị reject; các bài thông tin chi tiết vẫn được crawl. Preprocessing giữ dấu và ngữ cảnh tiếng Việt, không stemming, không xóa stopwords.
- `max_depth: 2`, `max_pages: 400`, `max_requests: 900`. Smoke test ghi đè `max_pages` bằng CLI. Seed ở depth 0; link từ seed ở depth 1.

## Robots và giới hạn tốc độ

Ngày 05/10/2026, `python main.py robots --site hcmus_admissions` nhận `robots.txt` HTTP 200; cả 11 seed đều `allowed: true`. Robots cấm `/wp-admin/`; profile còn loại path này. Crawler luôn tôn trọng robots.txt, chặn mặc định nếu không đọc được, không vượt CAPTCHA/Cloudflare/login. Delay ban đầu và tối thiểu là 2 giây/host; 429/503 dùng retry/backoff thích ứng, tối đa 5 lần theo profile.

## Lệnh chạy lại (từ thư mục gốc repository)

```powershell
pip install -r requirements.txt
python main.py robots --site hcmus_admissions
python main.py crawl --site hcmus_admissions --max-pages 5 --reset
python main.py validate --site hcmus_admissions
python main.py crawl --site hcmus_admissions --max-pages 20 --reset
python main.py validate --site hcmus_admissions
```

`--reset` chỉ reset `data/hcmus_admissions.db`; không dùng lệnh này khi muốn resume. SQLite nằm ở `data/hcmus_admissions.db`; báo cáo ở `reports/hcmus_admissions/`.

## Kết quả smoke test ngày 05/10/2026

| Giới hạn | Raw/HTTP 200 | Valid | Rejected | Passages | Links | Requests | Validation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 5 trang | 5 | 4 | 1 | 8 | 142 | 5 | PASS |
| 20 trang (sau sửa title) | 20 | 18 | 2 | 34 | 337 | 21 | PASS |

Run 20 trang: `failed_requests=0`, `robots_skipped=0`, `rate_limit_responses=0`, `duplicate_content=0`, `path_not_allowed=251`, `outside_domain=160`, `stop_reason=MAX_PAGES reached`. Có 20 phản hồi HTTP 200 và 1 HTTP 301 từ URL danh mục thiếu dấu `/` cuối; core đưa URL đích vào frontier, không lưu redirect thành raw page. Không có request error/HTTP error/challenge. Một timeout thoáng qua ở lần chạy thử 20 trang đầu đã thành công sau retry; lần chạy cuối không có timeout.

Hai reject ở run cuối đều là trang điều hướng: `/thong-tin-tuyen-sinh-cac-nam/` chỉ liệt kê link đề án (336 ký tự, `topic_not_relevant_enough`); `/diem-chuan-2/` chỉ liệt kê link điểm chuẩn theo năm (42 từ, `too_short_chars`). Raw HTML và link vẫn được lưu, còn bài `/2026-diem-chuan/` và `/2026-thong-tin-tuyen-sinh/` được chấp nhận. `PASS` kiểm tra tính toàn vẹn và chất lượng cơ bản của DB; đã kiểm tra thủ công các mẫu FAQ, chỉ tiêu, học phí, nhập học và thông tin tuyển sinh 2026 để xác nhận nội dung đúng chủ đề, có dấu và không có rác rõ rệt.
