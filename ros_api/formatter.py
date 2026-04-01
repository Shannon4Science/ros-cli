"""Output formatting for ros-api CLI results."""

from __future__ import annotations

import json
import sys

from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax

console = Console()


def print_result(data: dict, fmt: str = "json"):
    if fmt == "table":
        _print_table(data)
    elif fmt == "compact":
        _print_compact(data)
    else:
        _print_json(data)


def _print_json(data: dict):
    raw = json.dumps(data, indent=2, ensure_ascii=False)
    if sys.stdout.isatty():
        console.print(Syntax(raw, "json", theme="monokai"))
    else:
        print(raw)


def _print_table(data: dict):
    payload = data.get("data", {})
    items = payload.get("items") if isinstance(payload, dict) else None

    # Batch-fetch response (items with index/data/error) — check before query
    if items and isinstance(items[0], dict) and "index" in items[0]:
        _render_batch_table(items)
        return

    # Query response (has items list)
    if items is not None:
        _render_items_table(items)
        pagination = data.get("pagination")
        if pagination:
            console.print(
                f"\n[dim]Page {pagination['page']}/{pagination['total_pages']} "
                f"| {pagination['total']} total results[/dim]"
            )
        return

    # Single-fetch response
    if isinstance(payload, dict) and payload:
        _render_items_table([payload])
        return

    _print_json(data)


def _render_items_table(items: list):
    if not items:
        console.print("[yellow]No results found.[/yellow]")
        return

    columns = list(items[0].keys())
    table = Table(show_lines=True)
    for col in columns:
        table.add_column(col, overflow="fold", max_width=60)

    for item in items:
        row = []
        for col in columns:
            val = item.get(col)
            if isinstance(val, list):
                row.append(", ".join(str(v) for v in val[:5]))
            elif val is None:
                row.append("-")
            else:
                row.append(str(val)[:200])
        table.add_row(*row)

    console.print(table)


def _render_batch_table(items: list):
    table = Table(show_lines=True)
    table.add_column("#", justify="right", width=4)
    table.add_column("Identifier", max_width=50)
    table.add_column("Status", width=10)
    table.add_column("Data Preview", overflow="fold", max_width=80)

    for item in items:
        idx = str(item.get("index", ""))
        ident = item.get("identifier", {})
        ident_str = f"{ident.get('field', '')}={ident.get('value', '')}"
        error = item.get("error")
        status = "[red]not found[/red]" if error else "[green]ok[/green]"
        inner = item.get("data", {})
        preview = inner.get("title", json.dumps(inner, ensure_ascii=False)[:80]) if inner else "-"
        table.add_row(idx, ident_str, status, str(preview)[:80])

    console.print(table)


def _print_compact(data: dict):
    payload = data.get("data", {})

    items = payload.get("items") if isinstance(payload, dict) else None
    if items is not None:
        for item in items:
            # Batch-fetch items have nested data
            if "index" in item and "data" in item:
                inner = item["data"]
                error = item.get("error")
                if error:
                    ident = item.get("identifier", {})
                    print(f"[NOT FOUND] {ident.get('field')}={ident.get('value')}")
                else:
                    _print_compact_line(inner)
            else:
                _print_compact_line(item)
        pagination = data.get("pagination")
        if pagination:
            print(f"--- Page {pagination['page']}/{pagination['total_pages']} ({pagination['total']} total) ---")
        return

    if isinstance(payload, dict) and payload:
        _print_compact_line(payload)
        return

    print(json.dumps(data, ensure_ascii=False))


def _print_compact_line(item: dict):
    title = item.get("title", "")
    authors = item.get("author", item.get("authors", []))
    if isinstance(authors, list):
        authors = ", ".join(str(a) for a in authors[:3])
    doi = item.get("doi", "")
    year = item.get("publication_published_year", "")
    parts = [p for p in [title, authors, str(year) if year else "", doi] if p]
    print(" | ".join(parts))
