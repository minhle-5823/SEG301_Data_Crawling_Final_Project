## Tinh chỉnh (branch uel-admissions-faq-khang)

**Thay đổi trong profile.yaml**
- Thêm `#posts-results` vào đầu `container_selectors` để chỉ lấy vùng danh sách Q&A.
- Thêm `.faq-tags`, `.faq-copy-button`, `.mt-down-cate`, `.pagination` vào `remove_selectors` để loại "Tags:", nút "Sao chép", menu danh mục.
- Giữ query `faq_category`: các trang category chứa Q&A mà `/faq/` không có (trang chính chỉ có 10 Q&A).
- Giữ nguyên các ngưỡng preprocess: hạ `min_chars` chỉ thêm được 1 trang (194 ký tự).

**Kết quả (cùng crawl 26 trang)**

| Chỉ số | Trước | Sau |
|---|---|---|
| Passage dính rác (menu, Sao chép, Tags) | 25/26 | 0/20 |
| Passage trùng text | 6/26 | 3/20 |
| Valid / Rejected | 15 / 11 | 12 / 14 |
| Passages | 26 | 20 |
| Độ dài passage lớn nhất (từ) | 1191 | 1029 |

Ghi chú: 11 trang bị reject `too_short_chars` có `clean_text` rỗng (0 ký tự) sau khi bỏ menu.

**Vấn đề còn lại (nằm ở core, chưa sửa)**
- 3/20 passage trùng text: dedupe hiện so khớp ở mức cả trang, không ở mức passage.
- 1 passage dài 1029 từ dù `chunk_words=180`: cần xem `chunk_text` trong `core/preprocessor.py`.
- Đề xuất để chị hoặc chủ sở hữu core xem xét.