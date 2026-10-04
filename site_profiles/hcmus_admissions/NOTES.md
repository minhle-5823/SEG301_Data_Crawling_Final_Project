# HCMUS Admissions & FAQ

## Nguồn và phạm vi

- Website chính thức: https://tuyensinh.hcmus.edu.vn/
- Domain duy nhất được crawl: `tuyensinh.hcmus.edu.vn`.
- Nội dung: tuyển sinh đại học, phương thức xét tuyển, chỉ tiêu, điểm chuẩn, ngành/chương trình đào tạo, học phí, học bổng, hồ sơ và nhập học, câu hỏi thường gặp, thông báo dành cho thí sinh. Bài viết năm 2024–2026 và trang ngành/nhóm ngành được phép đi theo liên kết.
- Chỉ có 2 seed URLs: `/` và `/cau-hoi-thuong-gap/`. Giống profile MobiFone, core bắt đầu từ seed, duyệt BFS theo các link hợp lệ rồi dùng `allow_path_regex` để giữ đúng phạm vi; không cần seed riêng từng trang nội dung.

`/diem-chuan/` trả HTTP 301 sang ảnh JPG; trang HTML được trang chủ liên kết là `/diem-chuan-2/`. Trang chủ còn liên kết bài `/2026-diem-chuan/`, chứa thông báo điểm chuẩn đầy đủ. `/chi-tieu-2/` cũng chuyển sang ảnh, nên allowlist chỉ giữ `/chi-tieu/`.

## Cấu hình dễ giải thích

- `allow_path_regex` gồm 5 nhóm dễ giải thích: `/`, FAQ, `/danh-muc/thong-tin-tuyen-sinh...`, bài có slug `2024-` đến `2026-`, và các path chỉ tiêu/phương thức/điểm chuẩn/học phí/học bổng/nhập học/ngành/nhóm ngành. Link ngoài phạm vi bị loại trước khi vào BFS.
- `deny_path_regex` chặn khu vực quản trị, đăng nhập, feed, API và tài nguyên WordPress. Core cũng bỏ qua ảnh, PDF, CSS, JS và các file tĩnh theo `ignored_extensions` mặc định; domain ngoài luôn bị loại.
- Page types phân biệt `root`, `faq`, các trang chỉ tiêu/phương thức/điểm chuẩn/học phí/ngành/học bổng/nhập học, và `education_article`. Đây là nhãn mô tả trong DB, không phải crawler riêng.
- Title ưu tiên `.entry-title`, tiếp đến tiêu đề đầu trang `#content > div > h1`, rồi HTML `<title>`. Trang `/thong-tin-nhap-hoc/` dùng nhiều `<h1>` cho các mục I, II, III nên không lấy `h1` chung làm title. Nội dung lấy từ `main` (fallback `article`, `.entry-content`, `.site-main`, `body`) và bỏ `script`, `style`, menu, header, footer, form. Kiểm tra mẫu cho thấy FAQ và bài tuyển sinh giữ tiếng Việt có dấu, không chứa menu/footer đáng kể.
- Quality gate hiện có: tối thiểu 55 từ, 280 ký tự, Vietnamese score 0.35, relevance score 0.20 và 2 keyword hits. Toàn trang FAQ có 831 từ nên không bị loại nhầm. Các trang chỉ có danh sách link hoặc text rỗng bị reject; các bài thông tin chi tiết vẫn được crawl. Preprocessing giữ dấu và ngữ cảnh tiếng Việt, không stemming, không xóa stopwords.
- `max_depth: 2`, `max_pages: 400`, `max_requests: 900`. Lần crawl đầy đủ không ghi đè các giới hạn này. Seed ở depth 0; link từ seed ở depth 1.

## Robots và giới hạn tốc độ

Ngày 05/10/2026, `python main.py robots --site hcmus_admissions` nhận `robots.txt` HTTP 200; cả 2 seed đều `allowed: true`. Robots cấm `/wp-admin/`; profile còn loại path này. Crawler luôn tôn trọng robots.txt, chặn mặc định nếu không đọc được, không vượt CAPTCHA/Cloudflare/login. Delay ban đầu và tối thiểu là 2 giây/host; 429/503 dùng retry/backoff thích ứng, tối đa 5 lần theo profile.

## Lệnh chạy lại (từ thư mục gốc repository)

```powershell
pip install -r requirements.txt
python main.py robots --site hcmus_admissions
python main.py crawl --site hcmus_admissions --reset
python main.py validate --site hcmus_admissions
```

`--reset` reset `data/hcmus_admissions.db` và lần crawl mới cập nhật báo cáo HCMUS trong `reports/hcmus_admissions/`; không dùng lệnh này khi muốn resume.

## Kết quả crawl đầy đủ ngày 05/10/2026

Chạy ba lệnh trên trong bản test tách riêng có cùng `main.py`, `core/` và profile HCMUS để không ghi đè `data/` hoặc `reports/` của checkout chính. Không đặt `--max-pages`; profile dùng giới hạn mặc định 400 trang, 900 requests và depth 2.

| Raw/HTTP 200 | Valid | Rejected | Passages | Links | Requests | Validation |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 100 | 97 | 3 | 189 | 1.303 | 101 | PASS |

`stop_reason=URL Frontier is empty`, `frontier_remaining=0`; depth 0/1/2 lần lượt 2/73/25 trang. `failed_requests=0`, `robots_skipped=0`, `rate_limit_responses=0`, `duplicate_content=0`, `path_not_allowed=1632` và `outside_domain=805` (số link bị lọc, không phải request). Có một HTTP 301 của URL danh mục thiếu dấu `/` cuối; core đưa URL đích hợp lệ vào frontier. Không có request error, HTTP error hay challenge.

Ba reject đều có `too_short_chars`: `/diem-chuan-2/` chỉ liệt kê link điểm chuẩn (219 ký tự), danh mục `/danh-muc/thong-tin-tuyen-sinh/thong-tin-tuyen-sinh-nam-2026/diem-chuan-nam-2026/` chỉ có 144 ký tự, và `/2025-to-hop-va-chi-tieu-phuong-thuc-2/` có text trích xuất rỗng. Raw HTML và link vẫn được lưu; bài `/2026-diem-chuan/` và `/2026-thong-tin-tuyen-sinh/` được chấp nhận. `PASS` kiểm tra tính toàn vẹn/chất lượng cơ bản của DB; các mẫu FAQ, chỉ tiêu, học phí, nhập học và bài tuyển sinh vẫn có nội dung tiếng Việt có dấu, đúng chủ đề, không có menu/footer lặp đáng kể.
