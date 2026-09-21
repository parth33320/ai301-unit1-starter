# Rubric: is this a good first issue?

## Checks

| Check | Evidence | Pass condition | Weight |
|---|---|---|---|
| maintainer-alive | Repo-facts block: last default-branch commit date, last push date, and last maintainer comment timestamp | The repository is not archived, and either the last commit on the default branch or a maintainer comment occurred within 90 days of the capture date. | required |
| repo-active | Repo-facts block: commit history, releases, and issue activity | The repository shows ongoing activity (recent commits, releases, or issue responses) and is not archived or abandoned. | required |
| newcomer-scope | Issue body and initial description text | The issue description provides a bounded, well-defined task with clear context or reproduction steps, and is not a mega-issue, multi-year design debate, or codebase-wide architectural refactor. | required |
| clean-assignment | Issue comment thread and assignee metadata fields | The issue has no active assignees and no active open linked PRs or recent claim comments from external contributors. | required |
| policy-check | Repo-facts block: contribution policy and AI policy | The repository's contribution policy does not explicitly ban AI-generated or AI-assisted contributions. | required |
| good-first-label | Issue labels list in the issue metadata | The issue carries beginner-friendly labels such as "good first issue", "help wanted", "documentation", or "easy". | preferred |

## Verdict rule

Accept if and only if all `required` checks pass (`maintainer-alive`, `repo-active`, `newcomer-scope`, `clean-assignment`, `policy-check`). If any `required` check fails or evaluates to `unclear`, the final verdict is `reject`. `preferred` checks (`good-first-label`) do not alter the binary verdict; they are used solely to rank accepted issues by fit order.
