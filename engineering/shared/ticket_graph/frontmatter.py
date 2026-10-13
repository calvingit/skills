"""A restricted YAML subset for ticket frontmatter, with no third-party dependency.

Supported: block mappings, block sequences (of scalars or mappings), the empty
flow collections ``[]`` and ``{}``, ``null``, ``true``/``false``, decimal
integers, double-quoted strings (JSON escapes), single-quoted strings, and a
narrow set of plain scalars. Everything else (anchors, tags, block scalars,
flow collections with items, comments, tabs, multi-document markers, duplicate
keys, ambiguous plain words such as ``yes``) is rejected rather than guessed.
"""

from __future__ import annotations

import json
import re
from typing import Any

INDENT = 2
KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
INT_RE = re.compile(r"-?(0|[1-9][0-9]*)")
# Plain scalars we emit and accept: no YAML indicator at the start, no ": " or " #".
PLAIN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_./@+-]*")
AMBIGUOUS = {"y", "n", "yes", "no", "on", "off", "true", "false", "null", "~", ".nan", ".inf", "-.inf", ".inf"}


class FrontmatterError(ValueError):
    def __init__(self, line: int | None, detail: str) -> None:
        super().__init__(f"line {line}: {detail}" if line is not None else detail)
        self.line = line
        self.detail = detail


def _plain_ok(text: str) -> bool:
    return (
        bool(PLAIN_RE.fullmatch(text))
        and text.lower() not in AMBIGUOUS
        and not INT_RE.fullmatch(text)
        and not re.fullmatch(r"[-+]?[0-9._]+([eE][-+]?[0-9]+)?|0[xob].*", text)
    )


def parse_scalar(text: str, line: int) -> Any:
    if text == "":
        raise FrontmatterError(line, "empty value; use null, [] or {} explicitly")
    if text.startswith('"'):
        if len(text) < 2 or not text.endswith('"'):
            raise FrontmatterError(line, "unterminated double-quoted string")
        try:
            value = json.loads(text)
        except json.JSONDecodeError as exc:
            raise FrontmatterError(line, f"unsupported double-quoted string: {exc.msg}") from None
        if not isinstance(value, str):
            raise FrontmatterError(line, "invalid double-quoted string")
        return value
    if text.startswith("'"):
        inner = text[1:-1] if len(text) >= 2 and text.endswith("'") else None
        if inner is None or re.search(r"(?<!')'(?!')", inner.replace("''", "")):
            raise FrontmatterError(line, "invalid single-quoted string")
        return inner.replace("''", "'")
    if text in {"null", "~"}:
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if text == "[]":
        return []
    if text == "{}":
        return {}
    if INT_RE.fullmatch(text):
        return int(text)
    if _plain_ok(text):
        return text
    raise FrontmatterError(line, f"unsupported YAML value: {text!r}; quote strings with double quotes")


def _lines(text: str) -> list[tuple[int, int, str]]:
    result: list[tuple[int, int, str]] = []
    for number, raw in enumerate(text.split("\n"), start=1):
        if "\t" in raw:
            raise FrontmatterError(number, "tabs are not supported")
        if raw.endswith("\r"):
            raise FrontmatterError(number, "CR line endings are not supported")
        stripped = raw.rstrip(" ")
        if not stripped:
            continue
        content = stripped.lstrip(" ")
        if content.startswith("#"):
            raise FrontmatterError(number, "comments are not supported")
        if content in {"---", "..."} or content[0] in "&*!|>%@`{[" and content not in {"[]", "{}"}:
            raise FrontmatterError(number, f"unsupported YAML syntax: {content[:20]!r}")
        result.append((number, len(stripped) - len(content), content))
    return result


def _split_key(content: str, line: int) -> tuple[str, str | None]:
    if content.startswith('"') or content.startswith("'"):
        raise FrontmatterError(line, "quoted keys are not supported")
    key, sep, rest = content.partition(":")
    if not sep:
        raise FrontmatterError(line, "expected 'key: value'")
    if not KEY_RE.fullmatch(key):
        raise FrontmatterError(line, f"unsupported key: {key!r}")
    if rest == "":
        return key, None
    if not rest.startswith(" "):
        raise FrontmatterError(line, "a space is required after ':'")
    return key, rest[1:].strip(" ")


class _Parser:
    def __init__(self, lines: list[tuple[int, int, str]]) -> None:
        self.lines = lines
        self.index = 0

    def peek(self) -> tuple[int, int, str] | None:
        return self.lines[self.index] if self.index < len(self.lines) else None

    def block(self, indent: int) -> Any:
        current = self.peek()
        if current is None or current[1] != indent:
            raise FrontmatterError(current[0] if current else None, "expected an indented block")
        if current[2] == "-" or current[2].startswith("- "):
            return self.sequence(indent)
        return self.mapping(indent)

    def value_after_key(self, rest: str | None, indent: int, line: int) -> Any:
        if rest is not None:
            return parse_scalar(rest, line)
        nxt = self.peek()
        if nxt is None or nxt[1] <= indent:
            raise FrontmatterError(line, "missing value; use null, [] or {} explicitly")
        if nxt[1] != indent + INDENT:
            raise FrontmatterError(nxt[0], f"nested blocks must be indented by {INDENT} spaces")
        return self.block(indent + INDENT)

    def mapping(self, indent: int, first: tuple[int, str] | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {}

        def add(line: int, content: str) -> None:
            key, rest = _split_key(content, line)
            if key in result:
                raise FrontmatterError(line, f"duplicate key: {key}")
            result[key] = self.value_after_key(rest, indent, line)

        if first is not None:
            add(*first)
        while (current := self.peek()) is not None and current[1] >= indent:
            line, column, content = current
            if column != indent:
                raise FrontmatterError(line, "unexpected indentation")
            if content == "-" or content.startswith("- "):
                raise FrontmatterError(line, "sequence item where a mapping key was expected")
            self.index += 1
            add(line, content)
        return result

    def sequence(self, indent: int) -> list[Any]:
        result: list[Any] = []
        while (current := self.peek()) is not None and current[1] >= indent:
            line, column, content = current
            if column != indent or not (content == "-" or content.startswith("- ")):
                raise FrontmatterError(line, "expected a sequence item")
            self.index += 1
            item = content[2:].strip(" ") if content != "-" else ""
            if item == "":
                raise FrontmatterError(line, "empty sequence items are not supported")
            if item.startswith("- "):
                raise FrontmatterError(line, "nested inline sequences are not supported")
            if not item.startswith(('"', "'")) and re.match(r"[A-Za-z_][A-Za-z0-9_]*:( |$)", item):
                result.append(self.mapping(indent + INDENT, (line, item)))
            else:
                result.append(parse_scalar(item, line))
        return result


def loads(text: str) -> dict[str, Any]:
    lines = _lines(text)
    if not lines:
        raise FrontmatterError(None, "frontmatter is empty")
    if lines[0][1] != 0:
        raise FrontmatterError(lines[0][0], "top-level keys must not be indented")
    parser = _Parser(lines)
    value = parser.block(0)
    if not isinstance(value, dict):
        raise FrontmatterError(lines[0][0], "frontmatter must be a mapping")
    if parser.peek() is not None:
        raise FrontmatterError(parser.peek()[0], "unexpected content")
    return value


def _scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value if _plain_ok(value) else json.dumps(value, ensure_ascii=False)
    if value == []:
        return "[]"
    if value == {}:
        return "{}"
    raise TypeError(f"unsupported frontmatter value: {type(value).__name__}")


def _emit(value: Any, indent: int, out: list[str]) -> None:
    pad = " " * indent
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or not KEY_RE.fullmatch(key):
                raise TypeError(f"unsupported frontmatter key: {key!r}")
            if isinstance(item, (dict, list)) and item:
                out.append(f"{pad}{key}:")
                _emit(item, indent + INDENT, out)
            else:
                out.append(f"{pad}{key}: {_scalar(item)}")
        return
    for item in value:
        if isinstance(item, dict) and item:
            nested: list[str] = []
            _emit(item, indent + INDENT, nested)
            out.append(f"{pad}- {nested[0][indent + INDENT:]}")
            out.extend(nested[1:])
        elif isinstance(item, list) and item:
            raise TypeError("nested non-empty sequences are not supported")
        else:
            out.append(f"{pad}- {_scalar(item)}")


def dumps(value: dict[str, Any]) -> str:
    out: list[str] = []
    _emit(value, 0, out)
    text = "\n".join(out) + "\n"
    if loads(text) != value:  # The writer must never emit something the reader reads differently.
        raise ValueError("frontmatter round-trip mismatch")
    return text
