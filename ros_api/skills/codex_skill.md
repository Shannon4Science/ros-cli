---
name: ros-api
description: "Search and retrieve academic resources (papers, ebooks) via the ros-api service. Use when the user asks to find papers, search metadata by title/DOI/ISBN, query content by SHA256, look up academic literature, or fetch publication details. Triggers on: paper search, DOI lookup, literature query, academic metadata, content download, scholarly resource."
metadata:
  openclaw:
    requires:
      env: []
      bins:
        - python
        - ros
    primaryEnv: ROS_API_KEY
    homepage: https://docs.ros.shlab.tech:18443/
---

# ros — Academic Resource Query CLI

## Hard Rules

1. Follow the **Onboarding** section step-by-step before any query.
2. Never fabricate API responses — always run the actual command.
3. When summarizing for user, use `--output compact` or `--output table`; use `--output json` when raw data is needed.

## Onboarding (run these checks in order)

### Step 1: Check if CLI is installed

```bash
ros --version
```

If the command is not found, install it:

```bash
pip install git+https://github.com/Shannon4Science/ros-cli.git
```

After install, run `ros --version` again to confirm.

### Step 2: Check if API key is configured

```bash
ros config show
```

If API Key shows `(not set)`, tell the user:

> You need an API key for the ros academic resource service.
> Please visit https://docs.ros.shlab.tech:18443/concepts/authentication/#get-api-key to obtain one.

Then help them bind it:

```bash
ros config set-key YOUR_API_KEY
```

Or use interactive setup: `ros config init`

### Step 3: Verify connectivity

Run a quick test query:

```bash
ros metadata query --search "title:test" --page-size 1 --output compact
```

If this returns a result, setup is complete. Tell the user:

> ros CLI is ready! You can now:
> - **Search papers** by title, abstract, or keywords
> - **Fetch paper details** by DOI or ISBN
> - **Find full-text content** (PDF text) by SHA256
> - **Batch fetch** multiple papers at once
> - **Filter** by language, year, open access status, etc.
>
> Just tell me what you'd like to search for!

---

## Command Reference

### Search papers (metadata query)

```bash
ros metadata query --search "title:machine learning" --output compact
ros metadata query --search "abstract:reinforcement learning" --fields "title,author,doi,publication_published_year" --page-size 10 --sort "publication_published_year:desc" --output table
```

Add filters:

```bash
ros metadata query --search "title:transformer" --filter '{"type":"and","conditions":[{"field":"language","value":"en"},{"field":"publication_published_year","operator":"$gte","value":2020}]}' --output compact
```

### Fetch single paper

```bash
ros metadata fetch --doi "10.1234/example" --fields "title,author,abstract,doi"
ros metadata fetch --isbn "9780262046824"
```

### Batch fetch papers

```bash
ros metadata batch-fetch --ids '[{"field":"doi","value":"10.1234/a"},{"field":"isbn13","value":"9780262046824"}]' --fields "title,author,doi"
ros metadata batch-fetch --ids-file identifiers.json
```

### Search content (file-level)

```bash
ros content query --search "title:deep learning" --fields "sha256,title,file_format,content_url" --output table
```

### Fetch content by SHA256

```bash
ros content fetch --sha256 "dee1a64db5c1117b044f945abdd371179119e63f22dc8854bbf2b0427649a204" --fields "sha256,title,content_url"
```

---

## Query Construction Guide

### Search fields

| Resource | `--search` fields |
|----------|------------------|
| Metadata | `title`, `abstract`, `publication_venue_name`, `keywords` |
| Content  | `title`, `abstract`, `keyword`, `magazine` |

### Filter operators

`--filter` accepts JSON. Operators: `$eq` (default), `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$between`, `$contains`.

Logical combinators: `and`, `or`, `not` via `{"type":"and","conditions":[...]}`.

### Key filterable fields

| Resource | Fields |
|----------|--------|
| Metadata | `language`, `doi`, `isbn13`, `author`, `publication_published_year`, `publication_venue_name`, `access_is_oa`, `keywords`, `metadata_type` |
| Content  | `sha256`, `file_format`, `language`, `doi`, `isbn`, `content_length` |

### Sort

Only metadata: `--sort "publication_published_year:desc"` or `publication_published_year:asc`.

### Identifiers

| Resource | Fields |
|----------|--------|
| Metadata | `doi` (papers), `isbn13` (ebooks) |
| Content  | `sha256` |

### Metadata-to-Content linking

Metadata field `access_xinghe_repository_sha256` contains a list of SHA256 hashes. Each maps to a Content record. Workflow:

1. `ros metadata query --search "title:XXX" --fields "title,doi,access_xinghe_repository_sha256"`
2. Pick sha256 from result
3. `ros content fetch --sha256 <hash> --fields "sha256,title,content_url"`
4. `content_url` is a pre-signed link to the extracted full text (time-limited)
