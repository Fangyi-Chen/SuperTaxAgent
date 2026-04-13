---
name: tax-publish
description: Create a git branch, stage only skill and reference files, commit, push, and open a GitHub PR with anonymized evidence. Use after tax-evolve applies fixes, or when contributing manual improvements.
allowed-tools: [Read, Write, Bash, Glob]
argument-hint: "[description]"
---

# Tax Agent Publisher

Submit skill improvements as a GitHub pull request. Stages only safe files (never user data), shows a full diff for review, and opens a PR with anonymized context.

## Arguments

Invocation: `/tax-publish [description]`

- `[description]` — optional short description for the branch name (e.g., `fix-ctc-phaseout`)
- If omitted, defaults to `improvement`

## Prerequisites

- Git must be installed: `git --version`
- GitHub CLI must be installed: `gh --version`
- The repository must be initialized: `git status`
- `.claude-plugin/plugin.json` must exist with a `repository` field.

## Steps

### Step 1: Read Repository from Plugin Manifest

Read `.claude-plugin/plugin.json` and extract the `repository` field.

If `repository` is empty or missing:
> "The `repository` field in `.claude-plugin/plugin.json` is not set. Please add your GitHub repository URL (e.g., `https://github.com/your-username/your-repo`) and run `/tax-publish` again."

Stop if no repository is configured.

### Step 2: Determine Branch Type and Name

- If invoked from `/tax-evolve` (argument starts with `evolve-`): use prefix `evolve/`
- Otherwise (user-initiated contribution): use prefix `contrib/`

Format the date as `YYYY-MM-DD`.

Branch name: `{prefix}{description}-{date}`

Examples:
- `evolve/fix-ctc-phaseout-2026-04-02`
- `contrib/add-estimated-payments-question-2026-04-02`

```bash
git checkout -b {branch-name}
```

If the branch already exists, append a short random suffix or increment a counter.

### Step 3: Identify Staged Files

Determine which files have been modified since the last commit:

```bash
git status --short
```

Filter to only include safe files — those that match these patterns:
- `skills/*/SKILL.md`
- `skills/*/references/*.md`
- `.claude-plugin/plugin.json`
- `package.json`
- `README.md`
- `forms/*.pdf`

**NEVER stage these paths:**
- `data/` (all user tax data — gitignored, but verify)
- `*.pdf` outside of `forms/` (user-generated forms)
- Any file containing PII (check filenames for: `profile`, `calculation`, `comparison`, `evolution-log`, `output`)

Show the user the list of files that will be staged and ask for confirmation before proceeding.

### Step 4: Show Full Diff for Review

```bash
git diff HEAD -- {safe-files-list}
```

Display the full diff to the user and say:
> "Please review the above diff carefully. If you see any personal information (names, SSNs, dollar amounts from your return), say 'stop' and do not proceed. Otherwise, say 'looks good' to continue."

Wait for the user's explicit confirmation before proceeding.

### Step 5: Stage Safe Files

Stage only the approved files:

```bash
git add {safe-files-list}
```

Verify staging:
```bash
git status --short
```

Confirm that `data/` and any PDF outside `forms/` are NOT staged.

### Step 6: Commit

Write a structured commit message:

```
fix(skills): {short description of what changed}

Changes:
- {file 1}: {what was changed}
- {file 2}: {what was changed}

Root cause: {classification from tax-evolve, if available}
Evidence: {anonymized line deltas — e.g., "Line 19 CTC: under by ~18%"}

No user PII included in this commit.
```

Commit:
```bash
git commit -m "{structured message}"
```

### Step 7: Push to Remote

```bash
git push -u origin {branch-name}
```

If the push fails due to authentication, tell the user:
> "Push failed. Ensure you are authenticated with `gh auth login` and have write access to the repository."

### Step 8: Open Pull Request

Use the GitHub CLI to open a PR:

```bash
gh pr create \
  --title "{short description}" \
  --body "{pr body}" \
  --base main
```

PR body format:

```markdown
## Summary

- {bullet: what changed}
- {bullet: what changed}

## Root Cause

{Classification from tax-evolve: calculation_error / missing_data / missing_domain}

{Brief explanation of the rule that was wrong or missing}

## Evidence (Anonymized)

| Line | Description | Direction | Delta % |
|------|-------------|-----------|---------|
| 19   | Child Tax Credit | under | ~18% |

_No user PII included. Deltas are directional percentages only._

## Test Plan

- [ ] Run `/tax-calculate` on a sample return and verify line {N} now matches expected value
- [ ] Run `/tax-compare` on the sample return to confirm mismatch is resolved
- [ ] Review SKILL.md changes for correctness

🤖 Generated with Claude Code tax-agent self-evolution
```

### Step 9: Show PR URL

After the PR is created, display the URL:
> "PR submitted: {url}"
> "Thank you for helping improve the tax agent! The maintainer will review your proposed fix."

## Error Handling

- If `git` is not available, tell the user to install Git.
- If `gh` is not available, tell the user to install GitHub CLI: `brew install gh` or https://cli.github.com
- If `gh auth status` fails (not logged in), tell the user to run `gh auth login`.
- If the push fails, display the error and tell the user to check network access and repository permissions.
- If the user says "stop" during the diff review step, abort without staging, committing, or pushing anything. Run `git checkout main` to return to the main branch.
- If there are no modified skill files to stage, tell the user:
  > "No skill files have been modified. Nothing to publish."
