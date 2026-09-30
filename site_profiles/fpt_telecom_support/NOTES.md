# FPT Telecom Technical Support

## 1. Thông tin profile

- Thành viên: Trần Anh Khôi
- MSSV: CE190880
- Site ID: `fpt_telecom_support`
- Domain: Customer Support
- Website: FPT Telecom
- Ngôn ngữ: Vietnamese

Profile này phục vụ phần xây dựng WebCorpus cho đề tài:

**False-Negative-Aware Curriculum Hard Negative Mining for Vietnamese Dense Retrieval**

Web corpus của FPT được dùng để mở rộng candidate document pool. Dữ liệu
crawl không được xem là ground truth và không thay thế test set chuẩn của
VIRE.

---

## 2. Seed URL

```text
https://fpt.vn/tin-tuc/vien-thong-cong-nghe
```

Seed thuộc khu vực **Viễn thông công nghệ** của FPT Telecom.

Mục tiêu là thu thập các tài liệu tiếng Việt có nội dung liên quan đến
Internet, Wi-Fi và công nghệ viễn thông để tạo nguồn document thực tế cho
hard-negative mining.

---

## 3. Crawl configuration

```text
max_depth     = 2
max_pages     = 50
max_requests  = 200
timeout       = 20 seconds
```

Profile sử dụng BFS frontier và các cơ chế chung của `core/`.

Các chính sách robots, retry, rate limiting, duplicate detection và database
được xử lý bởi core dùng chung của nhóm.

---

## 4. URL scope

### Allowed domain

```text
fpt.vn
```

### Allowed content

Profile ưu tiên:

```text
/tin-tuc/vien-thong-cong-nghe
```

và các bài viết HTML dưới khu vực `/tin-tuc/`.

### Rejected

Không ưu tiên hoặc không crawl:

- URL ngoài domain `fpt.vn`
- file PDF
- file Word/Excel/PowerPoint
- archive
- ảnh
- audio/video
- CSS/JS/font
- URL liên quan tuyển dụng/việc làm
- URL liên hệ/giới thiệu ngoài phạm vi corpus

Mục tiêu của URL filtering là giữ candidate documents dạng HTML text có thể
được preprocessing và chunk thành passages.

---

## 5. Content relevance

FPT Telecom có nhiều nội dung khác nhau. Không phải mọi trang trên website
đều phù hợp với Customer Support.

Profile sử dụng `relevance_keywords` để ưu tiên nội dung có các tín hiệu
liên quan đến:

- Internet
- Wi-Fi
- modem
- router
- cáp quang
- mạng
- băng thông
- tốc độ mạng
- kết nối
- Mesh
- Access Point
- Wi-Fi 6 / Wi-Fi 7
- XGS-PON
- FPT Telecom
- FPT WiFi
- Hi FPT
- F-Safe

`min_keyword_hits: 2` được dùng để yêu cầu nhiều tín hiệu domain hơn thay vì
chỉ giữ một trang vì có một từ khóa đơn lẻ.

Không đặt ngưỡng quá cao vì WebCorpus cần giữ độ đa dạng tài liệu để BM25 và
Dense Retrieval có thể tìm được nhiều loại hard negatives.

---

## 6. Vietnamese preprocessing

Dữ liệu tiếng Việt cần giữ ngữ cảnh tự nhiên.

Giữ:

- dấu tiếng Việt
- punctuation
- số
- ngày tháng
- giá
- tên công nghệ
- tên dịch vụ
- tên sản phẩm

Không thực hiện stemming hoặc stopword removal trong profile này.

Lý do là corpus được dùng cho BM25 và Dense Retrieval, trong đó ngữ cảnh tự
nhiên của tài liệu là thông tin quan trọng.

---

## 7. Quality gate

Các tiêu chí preprocessing chính:

```text
min_words            = 60
min_chars            = 500
min_vietnamese_score = 0.35
min_relevance_score  = 0.20
min_keyword_hits     = 2
```

Các nội dung có dấu hiệu:

- 404
- not found
- access denied
- verify you are human
- CAPTCHA
- challenge

sẽ bị loại khỏi processed corpus theo cơ chế của core.

Mục tiêu là tránh đưa trang lỗi/challenge hoặc nội dung không có giá trị vào
candidate document pool.

---

## 8. Chunking

Profile sử dụng:

```text
chunk_words       = 220
chunk_overlap     = 40
min_chunk_words   = 45
```

Các passages sau khi tạo được dùng cho:

```text
BM25
Dense Retrieval
Hard Negative Mining
```

---

## 9. Vai trò trong đề tài

Luồng dữ liệu của FPT:

```text
FPT Website
     |
     v
Raw Pages
     |
     v
Preprocessing
     |
     v
Language + Relevance + Quality Validation
     |
     +---- Reject
     |
     v
Valid Documents
     |
     v
Passages
     |
     v
Candidate Document Pool
     |
     +--------------------+
     |                    |
     v                    v
   BM25             Dense Retrieval
     |                    |
     v                    v
Lexical Hard         Semantic Hard
Negatives             Negatives
     |                    |
     +---------+----------+
               |
               v
      False-negative Filtering
               |
               v
      Curriculum Hard-negative
             Training
```

Web corpus này chỉ mở rộng candidate document pool.

Không sử dụng các tài liệu crawl từ FPT làm ground truth cho đánh giá cuối.

Đánh giá cuối của đề tài vẫn sử dụng test set chuẩn VIRE, gồm CSConDa và
EduCoQA theo thiết kế của nhóm.

---

## 10. Server protection

Không bypass:

- robots.txt
- CAPTCHA
- Cloudflare/challenge
- login
- HTTP 401/403 restrictions

Profile để core xử lý robots, retry/backoff, rate limiting và host protection.

---

## 11. Expected output

Sau khi chạy crawler, FPT sẽ tạo database riêng theo cơ chế của core:

```text
data/fpt_telecom_support.db
```

Database/corpus sẽ chứa raw pages, processed documents, passages, links,
crawl state và các metadata/events tương ứng với thiết kế chung của project.

Có thể kiểm tra chất lượng bằng:

```bash
python main.py validate --site fpt_telecom_support
```

Kết quả validation cần chú ý:

- valid documents > 0
- passages > 0
- duplicate raw URLs = 0
- duplicate processed hashes = 0
- empty passages = 0
- low Vietnamese valid documents = 0
- request/HTTP/robots/block statistics

---

## 12. Không sửa core

Phần site profile này chỉ sở hữu:

```text
site_profiles/fpt_telecom_support/
├── profile.yaml
└── NOTES.md
```

Không thay đổi các file trong `core/` khi hoàn thiện phần FPT.
