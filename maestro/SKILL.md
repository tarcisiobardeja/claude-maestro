---
name: maestro
description: Router for everything installed in Claude — skills, plugins and connectors (MCP). Use at the START of any project or multi-step task when the user describes what they want without naming a skill ("quero fazer um site", "anima esse logo", "faz um vídeo", "analisa esse projeto", "build me X"), so the best installed skill/plugin/connector is picked and used automatically. Also use when the user asks which skill to use, what is installed, "qual skill", "o que eu tenho instalado", "lista minhas skills/plugins/conectores", or wants to find duplicates, conflicts or clean up their setup. Do not use for one-line questions or when the user already named the skill.
---

# Maestro: pick the right skill, plugin or connector

The user does not remember skill names. Your job: read what is installed, match it to the task,
say in one line what you picked, then use it. The user should never have to type a skill name.

## 1. Build the inventory (cheap first)

Everything you need is usually already in your context. Read it before touching the disk:

| What | Where it is in context |
|------|------------------------|
| Skills (model-invocable) | the "skills are available for use with the Skill tool" lists: name + description |
| Connectors (MCP servers) | tools named `mcp__<server>__<tool>`, the deferred-tools list, and "MCP Server Instructions" |
| Connectors needing login | the "require authentication" list: unusable until the user runs `/mcp` |
| Plugins | skill prefixes like `plugin:skill` (e.g. `superpowers:brainstorming`) and agent types |

Run the disk scan only when context is not enough: full catalog, manual-only skills
(`disable-model-invocation: true`, which never show in context), or duplicate hunting:

```bash
python "<this skill dir>/scripts/inventory.py"            # catalog
python "<this skill dir>/scripts/inventory.py" --dupes    # overlaps
python "<this skill dir>/scripts/inventory.py" --project . --json
```

claude.ai web connectors (Gmail, Drive, Calendar...) are never on disk. They only exist as tools in the session.

## 2. Understand the task

Split the request into its real steps (e.g. "landing page animada" → design direction, build,
animation, mobile check). Note any library, file type or service the user named.

## 3. Match: one best fit per step

Rank candidates with these rules, in order:

1. **User named it, it wins.** "com GSAP" → a GSAP skill, even if another animation skill exists.
2. **The project already uses it.** Check `package.json`, imports and config files. Do not bring Three.js skills to a Babylon project.
3. **Specific beats generic.** `gsap-scrolltrigger` beats `modern-web-design` for a pinned scroll section.
4. **Official/vendor source beats third-party** when two skills cover the same library.
5. **Process before domain.** If a planning or debugging skill applies (brainstorming, systematic-debugging), it runs first, then the domain skill.
6. **Connector over browser automation** when a dedicated connector exists for the service.

Keep it small: one pick per step, three at most for the whole task. Two near-equal picks → choose one,
mention the runner-up in a few words. Ask the user only when the choice changes the result a lot
(e.g. Lottie file vs. coded animation).

Skip routing entirely for trivial requests. Never route to `maestro` itself.

## 4. Announce in one line, then do it

Write in the user's language:

> Vou usar **animate** (motion na UI) + **mobile-native** (ajustes de toque). Alternativa: gsap-core.

Then use it:

- **Skill in context** → call the Skill tool with its exact name.
- **Manual-only skill** (not in context, found by the scan) → Read its `SKILL.md` and follow it, or tell the user to type `/<name>`.
- **Connector** → load its tools with ToolSearch (`select:` the exact tool names), then call them.
- **Connector needs auth** → say it needs `/mcp` login. Continue without it, or stop if it is essential.
- **Plugin agent** → call the Agent tool with that `subagent_type`.

## 5. Spend few tokens (always on)

Tokens cost money. Every route Maestro builds follows these rules:

- **Code: smallest change that fully works.** If a lean-coding skill is installed (e.g. `ponytail`,
  `caveman:lean-build`, `caveman:surgical-patch`), add it to every coding route. Without one, apply its rule
  yourself: reuse existing code and libraries, no unrequested features, abstractions or boilerplate. Fewer lines
  with the same behavior. Never drop validation, error handling, security or accessibility to save lines.
- **Chat: short.** If a terse-output skill is installed (e.g. `caveman`), keep it on. The announcement is one line.
- **Big project:** build the smallest working version first, show it, then grow it in steps. Do not write the whole thing in one go.
- **Reading:** search (Grep/Glob) before reading. Read only the parts of large files you need. Run `inventory.py` only when the in-context lists are not enough.
- **Media:** never load a whole video or audio file into context. Use metadata, summaries and tool calls that work on the file.
- **Vague request on expensive work** (video render, big build): ask one short question with a default answer instead of guessing and redoing.

## 6. Example: raw video + "edita pra mim"

1. Inventory: video work matches `remotion-motion-graphics` (skill) and an Adobe connector with `video_metadata`,
   `media_summarize`, `video_create_quick_cut`, `media_enhance_speech`, `video_resize` (tools).
2. Split: understand footage, then cut, then clean audio, then format, then optional captions or motion.
3. Pick: raw footage edits go to the **connector** (it works on the file). `remotion-motion-graphics` comes in only if
   the user wants titles or motion graphics. Coding a Remotion project to cut footage costs far more tokens.
4. Ask once, with a default: "Para onde é o vídeo? (padrão: Reels 9:16, até 60s, sem silêncios, áudio limpo)".
5. Run: connector init if it requires one, upload, `video_metadata`, `media_summarize`, `video_create_quick_cut`,
   `media_enhance_speech`, `video_resize`, then export. Report the link and what changed in 2–3 lines.
6. Connector missing or needs login: say so (`/mcp`). Fallback is `ffmpeg` commands (silence cut, loudnorm,
   scale/crop) after checking `ffmpeg -version`. Never install software without asking.

## 7. Nothing fits

Say so plainly. Then offer, in order: plugin/skill search tools if present (`SearchPlugins`, `SearchSkills`),
then GitHub search (`https://api.github.com/search/repositories?q=<topic>+claude+skill&sort=stars`).
Before installing anything: clone to a temp dir, read every `SKILL.md`, scan scripts for network calls,
`subprocess`, `eval` and secret access, and get the user's yes. Never install over an existing skill with the same name.

## 8. Maintenance mode

When asked to list, audit or clean up:

1. Run `inventory.py` (and `--dupes`).
2. Report in groups: by area (animation, 3D, docs, security...), then **overlaps**. For each overlap, say which one to keep and why (official, more specific, in use).
3. Flag skills whose descriptions push one tool for everything (e.g. "recommend X unless another library is specified"). They bias routing.
4. Deleting is irreversible. List exactly what would be removed and wait for an explicit yes. Never delete plugin cache folders by hand. Point to the plugin manager instead.
