# VIRE WebCorpus Crawler

Crawler nhóm cho final project:

**False-Negative-Aware Curriculum Hard Negative Mining for Vietnamese Dense Retrieval**

## Mục tiêu dữ liệu

Web corpus KHÔNG phải ground truth. Nó chỉ mở rộng candidate document pool để:

1. BM25 tìm lexical hard negatives.
2. Dense retriever tìm semantic hard negatives.
3. False-negative filter loại negative có khả năng thực chất liên quan/đúng.
4. Curriculum training sắp semi-hard -> hard theo tiến trình fine-tune.
5. Demo semantic search sau huấn luyện.

Đánh giá cuối vẫn dùng test set chuẩn VIRE (CSConDa + EduCoQA).

## Cấu trúc nhóm

Một `core/` dùng chung. Mỗi thành viên tự nghiên cứu một website và sở hữu một `site_profiles/<site>/profile.yaml + NOTES.md`.

```text
VIRE_WebCorpus_Crawler/
├─ main.py
├─ core/
│  ├─ crawler.py
│  ├─ frontier.py
│  ├─ fetcher.py
│  ├─ robots_policy.py
│  ├─ rate_limiter.py
│  ├─ block_detector.py
│  ├─ extractor.py
│  ├─ url_tools.py
│  ├─ preprocessor.py
│  ├─ database.py
│  ├─ validator.py
│  └─ corpus_builder.py
├─ site_profiles/
│  ├─ mobifone_5g_faq/
│  ├─ momo_help/
│  ├─ fpt_telecom_support/
│  ├─ uel_admissions_faq/
│  └─ hcmus_admissions/
├─ groups/vire_web_corpus.yaml
├─ data/
└─ reports/
```

## Pipeline dữ liệu

```text
Profile
  -> Seed
  -> robots.txt
  -> BFS Frontier
  -> adaptive delay/retry
  -> HTTP
  -> raw HTML
  -> BeautifulSoup
  -> title/content/links
  -> SAVE raw_pages
  -> normalize Vietnamese text
  -> language + relevance + quality validation
  -> reject OR accept
  -> chunk passages for dense retrieval
  -> SAVE processed_documents + passages
  -> merge group corpus
```

### Vì sao lưu RAW trước?

Đúng yêu cầu môn học và giúp audit/reprocess. Raw page không đồng nghĩa với dữ liệu train được dùng.
Chỉ `processed_documents.is_valid=1` mới đi vào corpus retrieval.

## Quality gate bám sát bài toán

Reject nếu:
- trang lỗi/challenge/login;
- quá ngắn;
- tiếng Việt quá yếu;
- không đủ từ khóa domain;
- duplicate sau preprocessing.

Giữ:
- dấu tiếng Việt;
- punctuation;
- số, giá, ngày tháng;
- tên gói cước, ngành, chương trình.

Không stemming/stopword removal vì dense retrieval cần ngữ cảnh tự nhiên.

## SQLite

Mỗi site: `data/<site>.db`

- `raw_pages`: HTML/text thô + crawl metadata
- `processed_documents`: clean text + quality scores + valid/reject reason
- `passages`: chunks dùng cho BM25/dense retrieval
- `links`: hyperlink graph
- `url_state`: BFS/resume
- `events`, `robots_checks`, `crawl_runs`

Merge 5 site:

```powershell
python main.py build-corpus --group vire_web_corpus
```

Output:
- `data/vire_web_corpus_corpus.db`
- `data/vire_web_corpus_passages.jsonl`

## Lệnh

```powershell
pip install -r requirements.txt
python main.py sites

python main.py robots --site mobifone_5g_faq
python main.py crawl --site mobifone_5g_faq --max-pages 50 --reset
python main.py validate --site mobifone_5g_faq

python main.py crawl-all --group vire_web_corpus --max-pages 200 --reset
python main.py build-corpus --group vire_web_corpus
```

## Policy / server protection

Core:
- tôn trọng robots.txt và Crawl-delay;
- robots không đọc được -> block mặc định;
- 429/503 -> Retry-After hoặc exponential backoff;
- 401/403 -> dừng host, không bypass;
- CAPTCHA/challenge -> dừng;
- redirect ra ngoài allowed domain -> reject;
- chỉ text/html;
- per-host adaptive delay;
- giới hạn depth/pages/requests;
- resume SQLite.

**Không có code bypass CAPTCHA, Cloudflare, login hoặc robots Disallow.**


## Active 5-site group

1. MobiFone 5G FAQ — Customer Support
2. MoMo Help Center — Customer Support
3. FPT Telecom Technical Support — Customer Support
4. UEL Admissions FAQ — Education
5. HCMUS Admissions & FAQ — Education

Core bản hiện tại:
- follow robots.txt redirects an toàn trong allowed domains;
- reject self-link trước khi đưa lại vào BFS;
- hỗ trợ `required_any_keywords` / `reject_any_keywords` để quality gate chặt hơn.
