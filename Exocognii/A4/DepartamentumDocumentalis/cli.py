# Departamentum Documentalis — cli.py
# v1.0.0
"""CLI entry point: compile .bureau files, scaffold templates."""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

from .bureau_parser import parse_file
from .emitter_md import emit_to_file as emit_md
from .emitter_wiz import emit_wiz
from .templates import get_template, list_templates
from .schema import CompanionJson


def _write_companion(doc, source: Path, wiz_path: Path,
                     md_path: Path, outdir: Path):
    """Write the .bureau.json sidecar file."""
    companion = {
        'source': str(source),
        'outputs': {
            'wiz': str(wiz_path),
            'md': str(md_path),
        },
        'template': doc.header.doc_type,
        'document_theme': doc.header.theme,
        'gui_theme_designator': None,
        'compiled_at': datetime.now(timezone.utc).isoformat(),
        'version': doc.header.version,
        'author': doc.header.author,
    }
    companion_path = outdir / (source.stem + '.bureau.json')
    with open(companion_path, 'w', encoding='utf-8') as f:
        json.dump(companion, f, indent=2, ensure_ascii=False)
    return companion_path


def cmd_compile(args):
    """Compile a .bureau file to .wiz + .md."""
    source = Path(args.source)
    if not source.exists():
        print(f"\u2715  Source not found: {source}", file=sys.stderr)
        return 1

    outdir = Path(args.outdir) if args.outdir else source.parent
    outdir.mkdir(parents=True, exist_ok=True)

    doc = parse_file(source)
    stem = source.stem

    md_path = outdir / f'{stem}.md'
    wiz_path = outdir / f'{stem}.wiz'

    # Emit .md
    emit_md(doc, md_path)
    print(f"\u2726  {md_path.name}")

    # Emit .wiz
    try:
        emit_wiz(doc, wiz_path)
        print(f"\u2726  {wiz_path.name}")
    except RuntimeError as e:
        print(f"\u2334  .wiz failed: {e}", file=sys.stderr)

    # Companion JSON
    _write_companion(doc, source, wiz_path, md_path, outdir)
    print(f"\u2726  {stem}.bureau.json")

    return 0


def cmd_new(args):
    """Scaffold a new .bureau file from a template."""
    template_type = args.template
    available = list_templates()
    if template_type not in available:
        print(f"\u2715  Unknown template: {template_type}", file=sys.stderr)
        print(f"   Available: {', '.join(available)}")
        return 1

    title = args.title or 'Untitled'
    author = args.author or ''
    content = get_template(template_type, title=title, author=author)

    out = Path(args.out) if args.out else Path(f'{title.replace(" ", "_")}.bureau')
    out.write_text(content, encoding='utf-8')
    print(f"\u2726  Scaffolded: {out}")
    return 0


def cmd_templates(args):
    """List available templates."""
    for name in list_templates():
        print(f"  {name}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='DepartamentumDocumentalis',
        description='\u2726  The Department of Documented Design Definitives',
    )
    sub = parser.add_subparsers(dest='command')

    # compile
    p_compile = sub.add_parser('compile', help='Compile a .bureau file')
    p_compile.add_argument('source', help='Path to .bureau file')
    p_compile.add_argument('--outdir', help='Output directory (default: same as source)')
    p_compile.set_defaults(func=cmd_compile)

    # new
    p_new = sub.add_parser('new', help='Scaffold a new .bureau from template')
    p_new.add_argument('template', help='Template type')
    p_new.add_argument('--title', help='Document title')
    p_new.add_argument('--author', help='Author name')
    p_new.add_argument('--out', help='Output file path')
    p_new.set_defaults(func=cmd_new)

    # templates
    p_tmpl = sub.add_parser('templates', help='List available templates')
    p_tmpl.set_defaults(func=cmd_templates)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    return args.func(args)
