# Architecture differences under a vague request

## 1. Deliberately vague technical request

Both models were asked only:

> Write a script to scrape a web page and save the data, handling errors.

The prompt names no URL, no fields to extract, no output format, no libraries, no CLI, and no rule for what “handling errors” means. Each model had to invent those decisions. The runs were kept in separate folders (`Claude Sonnet 5.5/`, `Grok 4.7/`) so neither implementation could copy the other.

## 2. Models tested

| Model | Role in this comparison | Artifact |
| --- | --- | --- |
| Claude Sonnet 5.5 | General-purpose model | `Claude Sonnet 5.5/scrape.py` (100 lines) |
| Grok 4.7 | Code-specialized model | `Grok 4.7/scrape.py` (205 lines) |

## 3. Summary of observed differences

The scripts share a shape: a CLI that fetches one page, pulls a title, headings, and links, then writes a file. They diverge on every decision the prompt left open.

The general-purpose model reached for the usual third-party stack (`requests`, BeautifulSoup), a short procedural script, logging, retries with backoff, and a second output format (CSV). The code-specialized model stayed on the standard library, wrote a custom `HTMLParser`, and added validation the prompt never asked for: URL scheme, content type, charset, empty body, “nothing extracted,” parent directories, and a configurable timeout.

The saved records are not interchangeable. Claude stores heading text as strings (`h1`–`h3`) and leaves `href` values as they appear in the HTML. Grok stores heading level, paragraphs, HTTP status, and absolute links. Claude’s `.csv` path saves links only, so the title and headings disappear. Grok writes JSON only, and its default path (`Grok/output/page.json`) still points at a folder from the run instructions.

## Observed choices

| Decision | Claude Sonnet 5.5 (general-purpose) | Grok 4.7 (code-specialized) |
| --- | --- | --- |
| Dependencies | `requests`, `beautifulsoup4` | Standard library only (`urllib.request`, `html.parser`, `pathlib`) |
| HTML parser | BeautifulSoup (`html.parser`) | Hand-written `PageExtractor(HTMLParser)` |
| Saved fields | URL, title, headings, links | URL, HTTP status, title, headings, paragraphs, links |
| Headings | `h1`–`h3` as plain strings | `h1`–`h6` as `{level, text}` |
| Links | Raw `href`, plus anchor text, document order | Absolute `href` via `urljoin`, plus anchor text |
| Ignored markup | Not filtered | `script`, `style`, `noscript` skipped |
| Output format | JSON, or links-only CSV when the path ends in `.csv` | Pretty-printed JSON only |
| Default output path | `output.json` | `Grok/output/page.json` |
| Parent directories | Not created; a nested path fails | Created with `mkdir(parents=True)` |
| CLI | `url`, `-o/--output` | `url`, `-o/--output`, `--timeout` |
| Timeout | Fixed at 10 seconds | Default 15 seconds; must be greater than 0 (exit code 2) |
| Retries | 3 attempts, exponential backoff, skip most 4xx except 429 | One attempt |
| Fetch checks | Status via `raise_for_status` | Scheme, host, status, content type, charset, non-empty body |
| Empty extraction | Saved anyway | Rejected as an error |
| Failures | `logging` to stderr, exit code 1, plus a catch-all `Exception` | `print` to stderr, exit codes 1 and 2, typed exceptions only |
| User-Agent | `SimpleScraper/1.0` | `Grok-scraper/1.0` |

## 4. Problems and arbitrary choices

**What “the data” is.** Nothing in the prompt defines the record. Claude omits paragraphs and HTTP status and flattens headings to strings. Grok omits any non-JSON format and refuses a page that parses but yields no title, heading, paragraph, or link. A caller cannot swap the two files. Claude’s CSV branch is a further arbitrary cut: the same run that would have saved title and headings as JSON saves only `text` and `href`.

**How far “handling errors” goes.** Claude treats many failures as transient and retries them, and then hides unexpected bugs behind `except Exception`. Grok treats the first failure as final, but invents checks the prompt never mentioned (content type must contain `html` or `text`, body must be non-empty, extraction must find something, timeout must be positive). A page that is valid HTML with an unusual content type, or a page whose only content is a `div`, succeeds for one model and fails for the other.

**Where the file goes, and which stack is allowed.** Claude writes `output.json` in the current directory and will not create missing folders. Grok defaults to `Grok/output/page.json` and creates parents, so the output path still carries the folder hint from the run rather than the script’s own location (`Grok 4.7/`). Claude also assumes `pip install requests beautifulsoup4`. Grok assumes nothing beyond Python. Both are reasonable, and neither was specified.

## 5. Self-assessment

Checked against the two scripts, two invented choices are load-bearing. Claude assumes `requests` and `beautifulsoup4` must be installed, then adds a CSV mode the prompt never asked for: `save()` writes only `text` and `href`, so title and headings vanish whenever the path ends in `.csv`. It also retries failed requests with backoff and follows redirects, with no cap on body size and no block on private or link-local addresses. Grok assumes a hand-rolled `HTMLParser` and a record of status, paragraphs, and `h1`–`h6` are what “the data” means, and it hard-codes the output path `Grok/output/page.json`, which is not the folder the script lives in. `urlopen` likewise follows redirects and calls `response.read()` with no size limit, so either program can be pointed at an internal URL. A vague prompt is dangerous in production because both answers look complete and still disagree on the contract: one downstream job loses fields, another job is rejected for an empty extract or a content type, and both will happily send traffic — including retries — wherever the URL points. Reviewers who only approved “scrape a page and handle errors” never accepted that schema, that dependency, or that network behavior.

