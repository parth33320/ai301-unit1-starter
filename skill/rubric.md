# Rubric: is this a good first issue?

<!--
A filled rubric must contain:
1. At least one row in the checks table (Check, Evidence, Pass condition, Weight).
2. A verdict rule below the table specifying how grades combine and how unclear is treated.
-->

## Checks

| Check | Evidence | Pass condition | Weight |
|---|---|---|---|
| maintainer-alive | Repo-facts block: last default-branch commit date and last maintainer comment timestamp | The last commit on the default branch or a maintainer comment occurred within the last 60 days. | required |
| repo-active | Repo-facts block: open pull requests count, closed issues count, and recent commit velocity | The repository has at least 10 closed issues or PRs in the last 90 days, indicating active project usage. | required |
| newcomer-scope | Issue body and initial description text | The issue description is self-contained, specifies clear files/paths or reproduction steps, and does not require deep architecture redesign. | required |
| clean-assignment | Issue comment thread and assignee metadata fields | The issue has no active assignees and no comments from external contributors claiming or working on it within the last 14 days. | required |
| good-first-label | Issue labels list in the issue metadata | The issue carries a beginner-friendly tag such as "good first issue", "help wanted", or equivalent documentation/cleanup focus. | preferred |

## Verdict rule

Accept if and only if all `required` checks pass (evaluating to pass). Any `unclear` result on a `required` check counts as a fail. `preferred` checks never change the binary verdict; they are used solely to rank accepted issues by fit order.

<!-- State how the grades above combine into accept or reject, and how
unclear is treated. Example shape (write your own): "accept if every
required check passes; preferred checks never change the verdict, they
rank accepted issues; unclear counts as fail." -->
