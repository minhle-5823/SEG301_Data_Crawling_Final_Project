# Data pipeline for VIRE hard-negative mining

## Raw
`raw_pages` giữ nguyên HTML + text BeautifulSoup đã extract để audit.

## Processed document
`preprocessor.py`:
1. Unicode NFC
2. remove zero-width/control
3. whitespace normalization
4. duplicate boilerplate lines
5. Vietnamese-language score
6. domain relevance score
7. quality gate
8. retrieval chunking

## Retrieval passage
Mặc định 180-220 words, overlap 35-40 words tùy profile.
Mỗi chunk gắn `source_site`, `domain_label`, `page_url`, `quality_score`.

## Downstream hard-negative mining
Không nằm trong crawler:
- index `passages`;
- BM25 top-k;
- baseline dense retriever top-k;
- remove known positives;
- false-negative filtering;
- difficulty scoring;
- curriculum semi-hard -> hard.

Crawler KHÔNG tự gán relevance label/ground truth cho web documents.
