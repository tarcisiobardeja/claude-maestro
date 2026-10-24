#!/usr/bin/env python3
"""Scan the local Claude Code install and print every skill, plugin and MCP connector found on disk.

Usage:
    python inventory.py                 # markdown catalog
    python inventory.py --json          # JSON (for tooling)
    python inventory.py --dupes         # only skills that look like duplicates/overlaps
    python inventory.py --project PATH  # also scan PATH/.claude/skills and PATH/.mcp.json

Stdlib only. Read-only: never writes or deletes anything.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

HOME = Path.home()
CLAUDE = HOME / ".claude"
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".trash", "evals", "examples", "assets"}


def frontmatter(path):
    """Return the name/description from a SKILL.md YAML header (no yaml dependency)."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    meta, key = {}, None
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            meta[key] = "" if val in ("|", ">", "|-", ">-") else val.strip("\"'")
        elif key and line.startswith((" ", "\t")):
            meta[key] = (meta[key] + " " + line.strip()).strip()
    return meta


def walk_skills(root, source):
    out = []
    if not root.is_dir():
        return out
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if "SKILL.md" in filenames:
            p = Path(dirpath) / "SKILL.md"
            meta = frontmatter(p)
            out.append({
                "name": meta.get("name") or Path(dirpath).name,
                "description": meta.get("description", ""),
                "manual_only": meta.get("disable-model-invocation", "").lower() == "true",
                "source": source,
                "path": str(p),
            })
    return out


def plugin_name(plugin_dir):
    for sub in (".claude-plugin", "."):
        f = plugin_dir / sub / "plugin.json"
        if f.is_file():
            try:
                return json.loads(f.read_text(encoding="utf-8")).get("name") or plugin_dir.name
            except (OSError, ValueError):
                pass
    return plugin_dir.name


def scan_plugins():
    """Plugins from the CLI registry plus the desktop app's synced folders."""
    plugins, skills, mcps = {}, [], []
    roots = []
    reg = CLAUDE / "plugins" / "installed_plugins.json"
    if reg.is_file():
        try:
            data = json.loads(reg.read_text(encoding="utf-8"))
            for key, entries in data.get("plugins", {}).items():
                entries = entries if isinstance(entries, list) else [entries]
                for e in entries:
                    if e.get("installPath"):
                        roots.append(Path(e["installPath"]))
        except (OSError, ValueError):
            pass
    synced = CLAUDE / "plugins" / "synced"
    if synced.is_dir():
        for f in synced.rglob(".claude-plugin/plugin.json"):
            if ".trash" not in f.parts:
                roots.append(f.parent.parent)

    for root in roots:
        name = plugin_name(root)
        # Synced folders keep older generations as "<id>~gN"; the first seen per name wins.
        if name in plugins:
            continue
        plugins[name] = str(root)
        for s in walk_skills(root / "skills", f"plugin:{name}"):
            s["name"] = f"{name}:{s['name']}"
            skills.append(s)
        mcp_file = root / ".mcp.json"
        if mcp_file.is_file():
            try:
                servers = json.loads(mcp_file.read_text(encoding="utf-8"))
                servers = servers.get("mcpServers", servers)
                mcps += [{"name": f"plugin:{name}:{k}", "source": f"plugin:{name}"} for k in servers]
            except (OSError, ValueError):
                pass
    return plugins, skills, mcps


def scan_mcp_config(project):
    out = []
    cfg = HOME / ".claude.json"
    if cfg.is_file():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            out += [{"name": k, "source": "user (~/.claude.json)"} for k in data.get("mcpServers", {})]
            if project:
                proj = data.get("projects", {}).get(Path(project).resolve().as_posix(), {})
                out += [{"name": k, "source": "project (~/.claude.json)"} for k in proj.get("mcpServers", {})]
        except (OSError, ValueError):
            pass
    if project and (Path(project) / ".mcp.json").is_file():
        try:
            data = json.loads((Path(project) / ".mcp.json").read_text(encoding="utf-8"))
            out += [{"name": k, "source": "project (.mcp.json)"} for k in data.get("mcpServers", {})]
        except (OSError, ValueError):
            pass
    return out


def tokens(text):
    stop = {"the", "and", "for", "with", "use", "when", "this", "skill", "user", "asks", "that", "from",
            "your", "into", "any", "you", "are", "using", "about", "also", "or", "to", "of", "a", "in", "on"}
    return {w for w in re.findall(r"[a-z0-9]{4,}", text.lower()) if w not in stop}


def find_dupes(skills):
    """Pairs of skills whose descriptions overlap heavily (Jaccard >= 0.25) or that share a base name."""
    pairs = []
    toks = [tokens(s["name"] + " " + s["description"]) for s in skills]
    for i in range(len(skills)):
        for j in range(i + 1, len(skills)):
            a, b = skills[i], skills[j]
            base_a, base_b = a["name"].split(":")[-1], b["name"].split(":")[-1]
            union = toks[i] | toks[j]
            score = len(toks[i] & toks[j]) / len(union) if union else 0
            if base_a == base_b or score >= 0.25:
                pairs.append((round(score, 2), a["name"], b["name"]))
    return sorted(pairs, reverse=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dupes", action="store_true")
    ap.add_argument("--project", default=os.getcwd())
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252

    skills = walk_skills(CLAUDE / "skills", "user")
    skills += walk_skills(Path(args.project) / ".claude" / "skills", "project")
    plugins, plugin_skills, plugin_mcps = scan_plugins()
    skills += plugin_skills
    mcps = scan_mcp_config(args.project) + plugin_mcps

    if args.json:
        json.dump({"skills": skills, "plugins": plugins, "mcp_servers": mcps,
                   "possible_duplicates": find_dupes(skills)}, sys.stdout, indent=2, ensure_ascii=False)
        return

    out = []
    if args.dupes:
        out.append("# Possible duplicates / overlaps\n")
        out += [f"- {a}  <->  {b}  (overlap {s})" for s, a, b in find_dupes(skills)] or ["- none"]
    else:
        out.append(f"# Inventory: {len(skills)} skills, {len(plugins)} plugins, {len(mcps)} MCP servers on disk\n")
        out.append("## Skills")
        for s in sorted(skills, key=lambda s: s["name"]):
            flag = " [manual: /" + s["name"] + "]" if s["manual_only"] else ""
            out.append(f"- **{s['name']}**{flag} ({s['source']}): {s['description'][:220]}")
        out.append("\n## Plugins")
        out += [f"- {n}" for n in sorted(plugins)] or ["- none"]
        out.append("\n## MCP servers (connectors configured on disk)")
        out += [f"- {m['name']} ({m['source']})" for m in mcps] or ["- none"]
        out.append("\nNote: claude.ai connectors (Gmail, Drive, Calendar...) are not on disk. "
                   "They only show up as tools inside a session.")
    print("\n".join(out))


if __name__ == "__main__":
    main()
