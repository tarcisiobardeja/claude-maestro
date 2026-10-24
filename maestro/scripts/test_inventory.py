"""Self-check for inventory.py: python test_inventory.py"""
import tempfile
from pathlib import Path

from inventory import find_dupes, frontmatter

with tempfile.TemporaryDirectory() as d:
    p = Path(d) / "SKILL.md"
    p.write_text("---\nname: rive\ndescription: |\n  Line one\n  line two\ndisable-model-invocation: true\n---\n# body\n",
                 encoding="utf-8")
    m = frontmatter(p)
    assert m["name"] == "rive", m
    assert m["description"] == "Line one line two", m
    assert m["disable-model-invocation"] == "true", m

    p.write_text("no header here", encoding="utf-8")
    assert frontmatter(p) == {}

a = {"name": "x:rive", "description": "rive state machine animation"}
b = {"name": "rive", "description": "totally different words"}
c = {"name": "pdf", "description": "merge split pages"}
names = {(x, y) for _, x, y in find_dupes([a, b, c])}
assert ("x:rive", "rive") in names and not any("pdf" in n for pair in names for n in pair), names
print("ok")
