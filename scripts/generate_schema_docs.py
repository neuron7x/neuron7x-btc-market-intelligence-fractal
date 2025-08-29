#!/usr/bin/env python3
"""Generate Markdown documentation from JSON Schema files."""
from __future__ import annotations
import json
import pathlib

def schema_to_markdown(schema_path: pathlib.Path) -> str:
    schema = json.loads(schema_path.read_text())
    title = schema.get("title", schema_path.stem)
    lines = [f"# {title}", ""]
    if "description" in schema:
        lines.extend([schema["description"], ""])
    properties = schema.get("properties", {})
    if properties:
        lines.extend(["## Properties", ""])
        for name, prop in properties.items():
            typ = prop.get("type", "any")
            desc = prop.get("description", "")
            lines.append(f"- **{name}** (*{typ}*): {desc}")
    lines.append("")
    return "\n".join(lines)

def main() -> None:
    docs_dir = pathlib.Path("docs/schemas")
    docs_dir.mkdir(parents=True, exist_ok=True)
    for schema_file in ["input_schema.json", "output_schema.json"]:
        path = pathlib.Path(schema_file)
        if not path.exists():
            continue
        markdown = schema_to_markdown(path)
        out_path = docs_dir / f"{path.stem}.md"
        out_path.write_text(markdown)
        print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
