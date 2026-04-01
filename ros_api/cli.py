"""ros CLI entry point."""

import json
import sys

import click

from ros_api import __version__
from ros_api import config as cfg
from ros_api.client import RosApiClient, ApiError
from ros_api.formatter import print_result


def _get_client() -> RosApiClient:
    key = cfg.get_api_key()
    if not key:
        click.echo(
            "Error: API key not configured.\n"
            "Run 'ros config init' to set up your API key.",
            err=True,
        )
        sys.exit(1)
    return RosApiClient(api_key=key, base_url=cfg.get_base_url())


def _parse_search(search_str: str | None) -> dict | None:
    """Parse 'field:value' into search object."""
    if not search_str:
        return None
    parts = search_str.split(":", 1)
    if len(parts) != 2:
        click.echo("Error: --search format must be 'field:value' (e.g. title:machine learning)", err=True)
        sys.exit(1)
    return {"field": parts[0], "operator": "$match", "value": parts[1]}


def _parse_sort(sort_str: str | None) -> list | None:
    """Parse 'field:asc' or 'field:desc' into sort array."""
    if not sort_str:
        return None
    parts = sort_str.split(":", 1)
    field = parts[0]
    order = parts[1] if len(parts) > 1 else "asc"
    if order not in ("asc", "desc"):
        click.echo("Error: sort order must be 'asc' or 'desc'", err=True)
        sys.exit(1)
    return [{"field": field, "order": order}]


def _parse_fields(fields_str: str | None) -> dict | None:
    if not fields_str:
        return None
    return {"fields": [f.strip() for f in fields_str.split(",") if f.strip()]}


def _parse_json_arg(value: str | None, arg_name: str) -> dict | list | None:
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        click.echo(f"Error: invalid JSON for --{arg_name}: {e}", err=True)
        sys.exit(1)


def _run_api(fn, output_format: str, **kwargs):
    """Call an API function, handle errors, and print."""
    try:
        result = fn(**{k: v for k, v in kwargs.items() if v is not None})
        print_result(result, output_format)
    except ApiError as e:
        click.echo(f"API Error [{e.status_code}]: {e.message}", err=True)
        if e.details:
            click.echo(f"Details: {json.dumps(e.details, ensure_ascii=False)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ── Main group ──────────────────────────────────────────────

@click.group()
@click.version_option(__version__, prog_name="ros")
def main():
    """ros CLI - Academic resource query tool."""


# ── Config commands ─────────────────────────────────────────

@main.group()
def config():
    """Manage API configuration."""


@config.command("init")
def config_init():
    """Interactive setup: configure API key and base URL."""
    click.echo("=== ros Configuration ===\n")

    current_url = cfg.get_base_url()
    click.echo(f"Current Base URL: {current_url}")
    new_url = click.prompt(
        "Base URL", default=current_url, show_default=True
    )
    cfg.set_base_url(new_url)

    current_key = cfg.get_api_key()
    if current_key:
        click.echo(f"Current API Key: {cfg.mask_key(current_key)}")
    new_key = click.prompt("API Key", hide_input=False)
    cfg.set_api_key(new_key)

    click.echo("\nVerifying connection...")
    try:
        client = RosApiClient(api_key=new_key, base_url=new_url)
        client.metadata_query(
            search={"field": "title", "value": "test"},
            pagination={"page": 1, "page_size": 1},
        )
        click.echo("Connection verified successfully!")
    except Exception as e:
        click.echo(f"Warning: verification failed ({e}). Config saved anyway.", err=True)

    click.echo(f"\nConfig saved to {cfg.CONFIG_FILE}")


@config.command("show")
def config_show():
    """Show current configuration."""
    data = cfg.load()
    click.echo(f"Config file : {cfg.CONFIG_FILE}")
    click.echo(f"Base URL    : {data.get('base_url', cfg.DEFAULT_BASE_URL)}")
    click.echo(f"API Key     : {cfg.mask_key(data.get('api_key'))}")


@config.command("set-key")
@click.argument("key")
def config_set_key(key):
    """Set API key."""
    cfg.set_api_key(key)
    click.echo(f"API key set: {cfg.mask_key(key)}")


@config.command("set-url")
@click.argument("url")
def config_set_url(url):
    """Set base URL."""
    cfg.set_base_url(url)
    click.echo(f"Base URL set: {url}")


# ── Metadata commands ───────────────────────────────────────

@main.group()
def metadata():
    """Query academic resource metadata."""


@metadata.command("query")
@click.option("--search", "search_str", help="Full-text search as field:value (e.g. title:machine learning)")
@click.option("--filter", "filter_json", help="Filter conditions as JSON string")
@click.option("--fields", help="Comma-separated projection fields")
@click.option("--page", type=int, default=1, help="Page number (1-20)")
@click.option("--page-size", type=int, default=25, help="Results per page (1-200)")
@click.option("--sort", "sort_str", help="Sort as field:asc or field:desc")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "compact"]), default="json")
def metadata_query(search_str, filter_json, fields, page, page_size, sort_str, output_fmt):
    """Search and filter metadata with pagination."""
    client = _get_client()
    _run_api(
        client.metadata_query,
        output_fmt,
        filter=_parse_json_arg(filter_json, "filter"),
        search=_parse_search(search_str),
        projection=_parse_fields(fields),
        pagination={"page": page, "page_size": page_size},
        sort=_parse_sort(sort_str),
    )


@metadata.command("fetch")
@click.option("--doi", help="Fetch by DOI")
@click.option("--isbn", help="Fetch by ISBN-13")
@click.option("--fields", help="Comma-separated projection fields")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "compact"]), default="json")
def metadata_fetch(doi, isbn, fields, output_fmt):
    """Fetch a single metadata record by identifier."""
    if not doi and not isbn:
        click.echo("Error: provide --doi or --isbn", err=True)
        sys.exit(1)
    identifier = {"field": "doi", "value": doi} if doi else {"field": "isbn13", "value": isbn}
    client = _get_client()
    _run_api(
        client.metadata_fetch,
        output_fmt,
        identifier=identifier,
        projection=_parse_fields(fields),
    )


@metadata.command("batch-fetch")
@click.option("--ids", "ids_json", help="Identifiers as JSON array: [{\"field\":\"doi\",\"value\":\"...\"},...]")
@click.option("--ids-file", type=click.Path(exists=True), help="Read identifiers from JSON file")
@click.option("--fields", help="Comma-separated projection fields")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "compact"]), default="json")
def metadata_batch_fetch(ids_json, ids_file, fields, output_fmt):
    """Batch fetch multiple metadata records."""
    if ids_json:
        identifiers = _parse_json_arg(ids_json, "ids")
    elif ids_file:
        identifiers = json.loads(open(ids_file, encoding="utf-8").read())
    else:
        click.echo("Error: provide --ids or --ids-file", err=True)
        sys.exit(1)
    client = _get_client()
    _run_api(
        client.metadata_batch_fetch,
        output_fmt,
        identifiers=identifiers,
        projection=_parse_fields(fields),
    )


# ── Content commands ────────────────────────────────────────

@main.group()
def content():
    """Query academic resource content."""


@content.command("query")
@click.option("--search", "search_str", help="Full-text search as field:value (e.g. title:deep learning)")
@click.option("--filter", "filter_json", help="Filter conditions as JSON string")
@click.option("--fields", help="Comma-separated projection fields")
@click.option("--page", type=int, default=1, help="Page number (1-20)")
@click.option("--page-size", type=int, default=25, help="Results per page (1-200)")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "compact"]), default="json")
def content_query(search_str, filter_json, fields, page, page_size, output_fmt):
    """Search and filter content with pagination."""
    client = _get_client()
    _run_api(
        client.content_query,
        output_fmt,
        filter=_parse_json_arg(filter_json, "filter"),
        search=_parse_search(search_str),
        projection=_parse_fields(fields),
        pagination={"page": page, "page_size": page_size},
    )


@content.command("fetch")
@click.option("--sha256", required=True, help="Content SHA256 hash")
@click.option("--fields", help="Comma-separated projection fields")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "compact"]), default="json")
def content_fetch(sha256, fields, output_fmt):
    """Fetch a single content record by SHA256."""
    client = _get_client()
    _run_api(
        client.content_fetch,
        output_fmt,
        identifier={"field": "sha256", "value": sha256},
        projection=_parse_fields(fields),
    )


@content.command("batch-fetch")
@click.option("--ids", "ids_json", help="Identifiers as JSON array: [{\"field\":\"sha256\",\"value\":\"...\"},...]")
@click.option("--ids-file", type=click.Path(exists=True), help="Read identifiers from JSON file")
@click.option("--fields", help="Comma-separated projection fields")
@click.option("--output", "output_fmt", type=click.Choice(["json", "table", "compact"]), default="json")
def content_batch_fetch(ids_json, ids_file, fields, output_fmt):
    """Batch fetch multiple content records."""
    if ids_json:
        identifiers = _parse_json_arg(ids_json, "ids")
    elif ids_file:
        identifiers = json.loads(open(ids_file, encoding="utf-8").read())
    else:
        click.echo("Error: provide --ids or --ids-file", err=True)
        sys.exit(1)
    client = _get_client()
    _run_api(
        client.content_batch_fetch,
        output_fmt,
        identifiers=identifiers,
        projection=_parse_fields(fields),
    )


if __name__ == "__main__":
    main()
