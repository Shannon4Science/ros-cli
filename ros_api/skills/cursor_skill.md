---
name: ros-api
description: Query academic resources through the ros CLI. Requires the ros CLI to be installed locally first. Use when the user asks to search papers or ebooks, fetch metadata by DOI or ISBN, query extracted content by SHA256, batch fetch records, inspect scholarly resources in the ROS service, or install and configure the ros CLI.
---

# ROS API CLI

Use the `ros` command-line tool as the source of truth for every lookup. This skill requires the CLI to be installed locally before use.

## Hard Rules

1. Install `ros-cli` before using this skill. If the `ros` command is unavailable, stop and install it before any lookup.
2. Run the real `ros` CLI. Do not fabricate results.
3. Run the onboarding checks after installation and before the first query in a session, or whenever the CLI or config may have changed.
4. Prefer `--output compact` or `--output table` for user-facing summaries. Use `--output json` only when the raw payload is needed.
5. Keep API keys out of chat when possible.
6. Treat returned DOI, ISBN, and SHA256 values as authoritative identifiers.

## Onboarding

1. Install or upgrade the CLI, then verify it is available:

   ```bash
   pip install --upgrade git+https://github.com/Shannon4Science/ros-cli.git
   ros --version
   ```

   If installation is blocked in the current environment, tell the user the skill cannot be used until `ros` is installed.

2. Check configuration:

   ```bash
   ros config show
   ```

   If the API key is missing, direct the user to:
   `https://docs.ros.shlab.tech:18443/concepts/authentication/#get-api-key`

   Then configure the CLI with either:

   ```bash
   ros config set-key YOUR_API_KEY
   ros config init
   ```

   Use `ros config set-url URL` only when the user needs a non-default base URL.

3. Verify connectivity:

   ```bash
   ros metadata query --search "title:test" --page-size 1 --output compact
   ```

## Standard Workflows

Search metadata:

```bash
ros metadata query --search "title:machine learning" --output compact
ros metadata query --search "abstract:reinforcement learning" --fields "title,author,doi,publication_published_year" --page-size 10 --sort "publication_published_year:desc" --output table
```

Fetch one metadata record:

```bash
ros metadata fetch --doi "10.1590/1806-9126-rbef-2022-0101" --fields "title,author,abstract,doi"
ros metadata fetch --isbn "9780262046824"
```

Batch fetch metadata:

```bash
ros metadata batch-fetch --ids "[{\"field\":\"doi\",\"value\":\"10.1234/a\"},{\"field\":\"isbn13\",\"value\":\"9780262046824\"}]" --fields "title,author,doi"
ros metadata batch-fetch --ids-file identifiers.json
```

Search content:

```bash
ros content query --search "title:deep learning" --fields "sha256,title,file_format,content_url" --output table
```

Fetch content by SHA256:

```bash
ros content fetch --sha256 "dee1a64db5c1117b044f945abdd371179119e63f22dc8854bbf2b0427649a204" --fields "sha256,title,content_url"
```

## Full-Text Retrieval Pattern

When the user starts from a paper title, DOI, or ISBN and needs the full extracted text:

1. Query or fetch metadata and request `access_xinghe_repository_sha256`.
2. Select the relevant SHA256 hash from that field.
3. Fetch the content record with `ros content fetch --sha256 ...`.
4. Use the returned `content_url` as the time-limited link to the extracted text.
