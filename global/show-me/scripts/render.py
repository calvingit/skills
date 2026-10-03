#!/usr/bin/env python3
"""Render a JSON explanation draft using the bundled, offline HTML template."""
import argparse
import html
import json
import re
import sys
from pathlib import Path


def text(value, field):
    if not isinstance(value, str):
        raise ValueError(f'{field}: expected a string')
    return html.escape(value, quote=True)


def strings(value, field):
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f'{field}: expected an array of strings')
    return value


def block_html(block):
    if not isinstance(block, dict):
        raise ValueError('block: expected an object')
    kind = block.get('type')
    if kind in ('text', 'callout'):
        lines = strings(block.get('paragraphs', []), 'paragraphs')
        return ''.join(f'<p>{text(line, "paragraph")}</p>' for line in lines)
    if kind == 'list':
        items = strings(block.get('items', []), 'items')
        return '<ul>' + ''.join(f'<li>{text(x, "item")}</li>' for x in items) + '</ul>'
    if kind == 'table':
        headers = strings(block.get('headers'), 'headers')
        rows = block.get('rows')
        if not headers or not isinstance(rows, list):
            raise ValueError('table: nonempty headers and rows array are required')
        rendered = []
        for row in rows:
            strings(row, 'row')
            if len(row) != len(headers):
                raise ValueError('table: row width must match headers')
            rendered.append('<tr>' + ''.join(f'<td>{text(x, "cell")}</td>' for x in row) + '</tr>')
        return ('<div class="table-scroll"><table><thead><tr>'
                + ''.join(f'<th>{text(x, "header")}</th>' for x in headers)
                + '</tr></thead><tbody>' + ''.join(rendered) + '</tbody></table></div>')
    if kind in ('diagram', 'html'):
        # An intentional escape hatch for author-reviewed SVG / custom interaction.
        markup = block.get('svg' if kind == 'diagram' else 'html')
        if not isinstance(markup, str) or not markup.strip():
            raise ValueError(f'{kind}: markup must be a nonempty string')
        if kind == 'diagram':
            if not re.match(r'\s*<svg\b', markup):
                raise ValueError('diagram: expected inline SVG, not Mermaid source')
            caption = text(block.get('caption', ''), 'caption')
            return f'<div class="diagram-scroll">{markup}</div>' + (f'<p class="diagram-note">{caption}</p>' if caption else '')
        return markup
    raise ValueError(f'block: unsupported type {kind!r}')


def render(draft):
    if not isinstance(draft, dict):
        raise ValueError('draft: expected an object')
    layout = draft.get('layout', 'sheet')
    if layout not in ('sheet', 'doc'):
        raise ValueError('layout: choose sheet or doc')
    sections = draft.get('sections')
    if not isinstance(sections, list) or not sections:
        raise ValueError('sections: expected a nonempty array')
    presentation = draft.get('presentation', {})
    if not isinstance(presentation, dict):
        raise ValueError('presentation: expected an object')
    unknown = set(presentation) - {'toc', 'numbers', 'cards'}
    if unknown:
        raise ValueError(f'presentation: unknown fields {sorted(unknown)}')
    options = {'toc': len(sections) > 1, 'numbers': True, 'cards': True}
    for key, value in presentation.items():
        if type(value) is not bool:
            raise ValueError(f'presentation.{key}: expected a boolean')
        options[key] = value
    panels, links = [], []
    for i, section in enumerate(sections, 1):
        if not isinstance(section, dict):
            raise ValueError('section: expected an object')
        title = text(section.get('title', ''), 'section.title')
        blocks = section.get('blocks')
        if not isinstance(blocks, list) or not blocks:
            raise ValueError('section.blocks: expected a nonempty array')
        span = section.get('span', 1)
        if type(span) is not int or span not in (1, 2, 3):
            raise ValueError('section.span: choose 1, 2 or 3')
        ident = f'section-{i}'
        classes = 'panel' + (' wide' if span == 2 else ' full' if span == 3 else '')
        if any(b.get('type') == 'callout' for b in blocks if isinstance(b, dict)):
            classes += ' verdict'
        body = ''.join(block_html(b) for b in blocks)
        number = f'<span class="number">{i:02}</span>' if options['numbers'] else ''
        heading = f'<div class="panel-head">{number}<h2>{title}</h2></div>' if title else ''
        panels.append(f'<section class="{classes}" id="{ident}">{heading}<div class="panel-body">{body}</div></section>')
        if title:
            label = f'{i:02} {title}' if options['numbers'] else title
            links.append(f'<a href="#{ident}">{label}</a>')
    status = text(draft.get('status', ''), 'status')
    script = draft.get('script', '')
    if not isinstance(script, str):
        raise ValueError('script: expected a string')
    if re.search(r'</script', script, re.I):
        raise ValueError('script: closing script tags are not allowed')
    source = json.dumps(draft, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    replacements = {
        'LAYOUT': layout, 'TITLE': text(draft.get('title'), 'title'),
        'TOC_ENABLED': str(options['toc'] and bool(links)).lower(),
        'CARDS': str(options['cards']).lower(),
        'SUBTITLE': text(draft.get('subtitle', ''), 'subtitle'),
        'SUMMARY': text(draft.get('summary', ''), 'summary'),
        'STATUS': f'<span class="status">{status}</span>' if status else '',
        'SHEET_PRESSED': str(layout == 'sheet').lower(),
        'DOC_PRESSED': str(layout == 'doc').lower(),
        'TOC': '<nav class="toc" aria-label="章节导航">' + ''.join(links) + '</nav>' if options['toc'] and links else '',
        'PANELS': ''.join(panels), 'SOURCE': source,
        'CUSTOM_SCRIPT': f'<script>\n{script}\n</script>' if script else '',
    }
    template = Path(__file__).resolve().parent.parent / 'references' / 'explanation.html'
    # One substitution pass: content containing token-like text is preserved.
    return re.sub(r'@@([A-Z_]+)@@', lambda m: replacements[m[1]], template.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('draft', help='JSON draft path; - reads stdin')
    parser.add_argument('-o', '--output', required=True, type=Path)
    parser.add_argument('--force', action='store_true', help='replace an existing output')
    args = parser.parse_args()
    try:
        source = sys.stdin.read() if args.draft == '-' else Path(args.draft).read_text(encoding='utf-8')
        page = render(json.loads(source))
        with args.output.open('w' if args.force else 'x', encoding='utf-8') as target:
            target.write(page)
    except (OSError, ValueError, KeyError) as error:
        print(f'render: {error}', file=sys.stderr)
        return 1
    print(args.output.resolve())
    return 0


if __name__ == '__main__':
    sys.exit(main())
