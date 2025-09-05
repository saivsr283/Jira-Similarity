# 📚 How This Tool Works — JIRA Similarity Tool (Python/Streamlit)

## Scope and Services
- PLAT Similarity UI: http://localhost:8501
- Filter Analysis UI: http://localhost:8503

## Data Source and Authentication
- Reads JIRA URL, username, API token from `config.json` or environment variables.
- Uses an authenticated Requests session to call Atlassian REST APIs.
- Primary endpoint: `/rest/api/3/search/jql` with `jql`, `maxResults`, and selected `fields`.

## Candidate Search Strategy
- Prefer tickets from `project in (PLAT, XOP)`.
- Restrict to `issuetype in (Bug, "Customer-Incident", "Customer-Defect")`.
- Build query terms from the target ticket:
  - Full summary
  - Subject/feature terms extracted from the summary (e.g., “goal completion rate”, “performance dashboard”, “user id filter”, “gen ai node”)
  - 2-gram and 3-gram phrases from the summary
- For each query, search PLAT/XOP + allowed issue types; if empty, fall back to current project scope.
- Deduplicate candidates by ticket key.

## Text Preprocessing
- Lowercases text.
- Strips generic status/function phrases so they don’t bias similarity:
  - “not functioning”, “not working”, “as expected”, “unexpected”, “issue with”,
    “error occurred”, “failed”, “failure”, “failing”, “throws error”, “showing error”.
- Removes punctuation (except hyphens) and collapses whitespace.

## Subject/Feature Extraction
- Detects subject heads and constructs subject terms around them:
  - heads: node, flag, field, feature, event, function, endpoint, api, setting, connector,
    channel, intent, entity, analytics, dashboard, report, metric, filter, log, usage,
    userid, console, import, migration, genai, llm, gpt, dialoggpt, searchai, websdk
- Adds domain phrases when present:
  - “goal completion rate”, “performance dashboard”, “user id filter”, “usage logs”,
    “gen ai node”, “dialog gpt”, “openai connector”, “admin console”, “full bot import”.

## Hard Subject Overlap (Gate)
- A candidate is considered only if it shares at least one extracted subject term with the target summary.
- Prevents unrelated tickets (e.g., migrations/admin console) from matching “performance dashboard” subjects.

## Similarity Scoring (Content-First)
- Weighted combination:
  - Subject similarity: 0.50
  - Summary keyword overlap: 0.35
  - Technical term overlap: 0.10
  - Overall Jaccard overlap: 0.05
- Metadata (type, priority, labels, components, project) is not weighted.
- Small bonus for similar summary length.

## Threshold and Fallback
- User sets the similarity threshold (default 0.20).
- If no results pass and there are candidates, retry once with `threshold - 0.10` (min 0.10).

## UI Behavior When No Results
- If similarity search yields zero results, the PLAT UI shows a fallback card with the target ticket details
  (key, summary, status, type, assignee, reporter, created date, priority, and a JIRA link).

## Filter Analysis (http://localhost:8503)
- Accepts raw JQL input and fetches matching tickets.
- Forms similarity groups using TF‑IDF + cosine on summaries; compact table UI with expand/collapse.
- Per-group “Find similar tickets” uses the same subject-first strategy and threshold behavior.

## Where to Adjust Logic
- Project/Issue type constraints: `search_tickets_projects_issue_type()` in `jira_similarity_tool.py`.
- Status phrase stripping: `SimilarityAnalyzer.preprocess_text()`.
- Subject extraction: `SimilarityAnalyzer.extract_subject_terms()`.
- Subject gating + scoring: `JIRASimilarityTool.analyze_similarity()` and
  `SimilarityAnalyzer.calculate_similarity()`.

## Known Limitations
- Very generic summaries can limit recall; lowering the threshold may help.
- Relevant issues outside PLAT/XOP or outside allowed issue types require relaxing constraints. 

## 📌 Example: DialogGPT

- Target summary: "DialogGPT: Repeat Response Event firing incorrectly for imported app"
- Extracted subjects: dialog gpt, repeat response event, event, response, imported app
- Included (subject overlap):
  - [PLAT-45859](https://koreteam.atlassian.net/browse/PLAT-45859) — repeat response feature relates to Repeat Response Event / DialogGPT
  - [PLAT-46639](https://koreteam.atlassian.net/browse/PLAT-46639) — DialogGPT task failure event (same DialogGPT/event subject)
- Excluded (no subject overlap):
  - [PLAT-46201](https://koreteam.atlassian.net/browse/PLAT-46201) — admin console / migration topics (different subject) 