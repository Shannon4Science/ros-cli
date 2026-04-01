# ros CLI — Academic Resource Query Tool

## What This Tool Does

`ros` is a CLI that queries the ros-api academic resource service (papers, ebooks). It supports metadata search, content retrieval, and batch operations.

## Setup

```bash
pip install git+https://github.com/Shannon4Science/ros-cli.git
ros config init   # Bind your API key interactively
```

API key portal: https://docs.ros.shlab.tech:18443/concepts/authentication/#get-api-key

## Before Any Query

Run `ros config show`. If API Key is "(not set)", guide the user to run `ros config init` or `ros config set-key KEY`.

## Commands

### Search metadata (papers/ebooks)

```bash
ros metadata query --search "title:machine learning" --fields "title,author,doi" --output compact
ros metadata query --filter '{"type":"and","conditions":[{"field":"language","value":"en"},{"field":"publication_published_year","operator":"$gte","value":2020}]}' --sort "publication_published_year:desc"
```

### Fetch by identifier

```bash
ros metadata fetch --doi "10.1590/1806-9126-rbef-2022-0101"
ros metadata fetch --isbn "9780262046824"
ros content fetch --sha256 "dee1a64db5c1117b044f945abdd371179119e63f22dc8854bbf2b0427649a204"
```

### Batch fetch

```bash
ros metadata batch-fetch --ids '[{"field":"doi","value":"10.xxx"},{"field":"isbn13","value":"978xxx"}]'
ros content batch-fetch --ids '[{"field":"sha256","value":"abc..."}]'
```

### Content search

```bash
ros content query --search "title:deep learning" --filter '{"field":"file_format","value":"pdf"}' --fields "sha256,title,content_url"
```

## Key Knowledge

- **Metadata identifiers**: `doi` (papers), `isbn13` (ebooks)
- **Content identifier**: `sha256`
- **Link metadata->content**: metadata field `access_xinghe_repository_sha256` contains SHA256 list mapping to content records
- **Search fields (metadata)**: `title`, `abstract`, `publication_venue_name`, `keywords`
- **Search fields (content)**: `title`, `abstract`, `keyword`, `magazine`
- **Filter operators**: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$in`, `$nin`, `$between`, `$contains`
- **Sort**: only metadata supports `--sort "publication_published_year:desc"`
- **Output**: `--output json|table|compact`
- **content_url**: pre-signed download link for extracted full text (time-limited)
