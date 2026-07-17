#!/usr/bin/env python3
"""Generate Fumadocs API reference pages directly from BlendGen's Python AST."""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path


DOCS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = DOCS_ROOT.parent
OUTPUT_ROOT = DOCS_ROOT / "content" / "docs" / "api" / "generated"
SOURCE_URL = "https://github.com/juniorxsound/BlendGen/blob/main"

PUBLIC_MODULES = (
    "blendgen.session",
    "blendgen.renderer",
    "blendgen.dataset",
    "blendgen.renderers.base",
    "blendgen.renderers.cycles",
    "blendgen.renderers.eevee",
    "blendgen.passes.base",
    "blendgen.passes.color",
    "blendgen.passes.alpha",
    "blendgen.passes.depth",
    "blendgen.passes.normal",
    "blendgen.passes.opticalflow",
    "blendgen.passes.index",
    "blendgen.util",
    "blendgen.utils.scene",
)


@dataclass(frozen=True)
class Symbol:
    name: str
    kind: str
    signature: str
    doc: str
    line: int
    members: tuple["Symbol", ...] = ()
    values: tuple[str, ...] = ()


def module_path(module: str) -> Path:
    return REPO_ROOT / Path(*module.split(".")).with_suffix(".py")


def display_doc(node: ast.AST) -> str:
    value = (ast.get_docstring(node, clean=True) or "No description is available yet.").strip().strip('"')
    return escape_mdx(value)


def escape_mdx(value: str) -> str:
    """Escape Python prose that MDX would otherwise interpret as JSX."""
    return (value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("{", "&#123;")
            .replace("}", "&#125;"))


def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    return f"{prefix} {node.name}({ast.unparse(node.args)}){returns}"


def class_symbol(node: ast.ClassDef) -> Symbol:
    members: list[Symbol] = []
    values: list[str] = []
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if child.name.startswith("_") and child.name != "__init__":
                continue
            is_property = any(
                isinstance(item, ast.Name) and item.id == "property"
                for item in child.decorator_list
            )
            is_setter = any(
                isinstance(item, ast.Attribute) and item.attr == "setter"
                for item in child.decorator_list
            )
            kind = "property" if is_property else "setter" if is_setter else "method"
            member_name = f"{child.name}.setter" if is_setter else child.name
            members.append(Symbol(
                name=member_name,
                kind=kind,
                signature=signature(child),
                doc=display_doc(child),
                line=child.lineno,
            ))
        elif isinstance(child, (ast.Assign, ast.AnnAssign)):
            targets = child.targets if isinstance(child, ast.Assign) else [child.target]
            value = child.value
            for target in targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    rendered = ast.unparse(value) if value is not None else "..."
                    values.append(f"{target.id} = {rendered}")

    bases = f"({', '.join(ast.unparse(base) for base in node.bases)})" if node.bases else ""
    return Symbol(
        name=node.name,
        kind="class",
        signature=f"class {node.name}{bases}",
        doc=display_doc(node),
        line=node.lineno,
        members=tuple(members),
        values=tuple(values),
    )


def public_symbols(tree: ast.Module) -> list[Symbol]:
    symbols: list[Symbol] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            symbols.append(class_symbol(node))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            symbols.append(Symbol(
                name=node.name,
                kind="function",
                signature=signature(node),
                doc=display_doc(node),
                line=node.lineno,
            ))
    return symbols


def source_link(relative_path: Path, line: int) -> str:
    return f"{SOURCE_URL}/{relative_path.as_posix()}#L{line}"


def render(module: str, relative_path: Path, module_doc: str, symbols: list[Symbol]) -> str:
    title = module.removeprefix("blendgen.")
    lines = [
        "---",
        f"title: {title}",
        f"description: Generated Python API reference for {module}.",
        "---",
        "",
        f"# `{module}`",
        "",
        "> This page is generated from the Python source by `npm run generate:api`. Do not edit it by hand.",
        "",
        escape_mdx(module_doc) if module_doc else f"Public symbols exposed by `{module}`.",
        "",
    ]

    for item in symbols:
        lines.extend([
            f"## `{item.name}`",
            "",
            f"[{item.kind.title()} source]({source_link(relative_path, item.line)})",
            "",
            "```python",
            item.signature,
            "```",
            "",
            item.doc,
            "",
        ])
        if item.values:
            lines.extend(["### Values", "", "```python", *item.values, "```", ""])
        for member in item.members:
            lines.extend([
                f"### `{item.name}.{member.name}`",
                "",
                f"[{member.kind.title()} source]({source_link(relative_path, member.line)})",
                "",
                "```python",
                member.signature,
                "```",
                "",
                member.doc,
                "",
            ])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    page_names: list[str] = []
    expected: set[Path] = set()

    for module in PUBLIC_MODULES:
        path = module_path(module)
        relative_path = path.relative_to(REPO_ROOT)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        name = module.removeprefix("blendgen.").replace(".", "-")
        output = OUTPUT_ROOT / f"{name}.mdx"
        output.write_text(
            render(module, relative_path, ast.get_docstring(tree, clean=True) or "", public_symbols(tree)),
            encoding="utf-8",
        )
        expected.add(output)
        page_names.append(name)

    for stale in OUTPUT_ROOT.glob("*.mdx"):
        if stale not in expected:
            stale.unlink()

    (OUTPUT_ROOT / "meta.json").write_text(
        json.dumps({"title": "Generated modules", "pages": page_names}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {len(page_names)} API reference pages in {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
