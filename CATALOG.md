# Catálogo

Skills e plugins que uso junto com o Maestro. Nada disso é copiado aqui: cada item aponta para o repositório
original, com a licença dele. Leia o código antes de instalar, principalmente os que têm scripts.

Instalar uma coleção de skills (macOS/Linux; no Windows troque `cp -r` por `Copy-Item -Recurse`):

```bash
git clone --depth 1 https://github.com/<dono>/<repo> /tmp/<repo>
cp -r /tmp/<repo>/<pasta-das-skills>/* ~/.claude/skills/
```

Plugins: no Claude Code, `/plugin marketplace add <dono>/<repo>` e depois `/plugin install <nome>@<marketplace>`.

## Coleções de skills

| Coleção | Pasta das skills | Licença | O que tem | Atenção |
|---|---|---|---|---|
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | `skills/` | MIT | 15 skills de design e animação: `animate`, `apple-design`, `mobile-native`, `review-animations`, `break-ui`... | só markdown |
| [greensock/gsap-skills](https://github.com/greensock/gsap-skills) | `skills/` | MIT | 8 skills oficiais do GSAP: core, timeline, ScrollTrigger, plugins, React, performance | as descrições recomendam GSAP por padrão |
| [CloudAI-X/threejs-skills](https://github.com/CloudAI-X/threejs-skills) | `skills/` | MIT | 13 skills de Three.js: fundamentos, materiais, shaders, R3F, performance... | só markdown |
| [freshtechbro/claudedesignskills](https://github.com/freshtechbro/claudedesignskills) | `.claude/skills/` | MIT | 23 skills de 3D, scroll e animação: Babylon, PixiJS, Lottie, Barba, Locomotive... | 46 scripts Python; no Windows clone com `git -c core.longpaths=true`; `gsap-scrolltrigger` e `skill-creator` duplicam outras |
| [BowTiedSwan/rive-skills](https://github.com/BowTiedSwan/rive-skills) | raiz (`SKILL.md` + `references/`) | sem licença declarada | Rive: state machines, scripting Luau, runtimes | instale numa pasta `rive/` |
| [diffusionstudio/lottie](https://github.com/diffusionstudio/lottie) | `skills/text-to-lottie/` | MIT | Criar e editar Lottie JSON com player Skottie local | usa `npx degit` + `npm run dev` para preview |
| [talknerdytome-labs/wiggle-claude-skill](https://github.com/talknerdytome-labs/wiggle-claude-skill) | raiz | Apache-2.0 | Animar logos: Lottie, GIF, MP4 | precisa `pip install -r requirements.txt`; ffmpeg e potrace opcionais; scripts chamam `python3` |
| [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) | `remotion-motion-graphics/` | MIT | Vídeos com Remotion (React) e motion profissional | descrição bem ampla, pode disparar em qualquer animação |

## Plugins

| Plugin | Repositório | O que faz |
|---|---|---|
| superpowers | [obra/superpowers](https://github.com/obra/superpowers) | Processo: brainstorming, planos, TDD, debugging sistemático, code review |
| ponytail | [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Código mínimo: a menor mudança que resolve (economiza tokens) |
| caveman | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Respostas curtas (economiza tokens) |
| design, marketing, productivity | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Plugins oficiais da Anthropic: crítica de design, UX copy, campanhas, tarefas |
| vantage | [tinoimammp/vantage-security-agent](https://github.com/tinoimammp/vantage-security-agent) | Auditoria de segurança (SAST) web e mobile |
| singularity-claude | [shmayro/singularity-claude](https://github.com/shmayro/singularity-claude) | Cria, pontua e conserta skills |
| miro | [miroapp/miro-ai](https://github.com/miroapp/miro-ai) | Integração com quadros do Miro |
| claude-pace | [Astro-Han/claude-pace](https://github.com/Astro-Han/claude-pace) | Statusline com ritmo de uso |

## Sobreposições conhecidas

Com tudo instalado, várias skills cobrem o mesmo assunto. O Maestro desempata, mas para menos ruído escolha uma de cada:

- `rive` ou `rive-interactive`
- `threejs-fundamentals` ou `threejs-webgl`; `threejs-react-three-fiber` ou `react-three-fiber`
- `lottie-animations`, `text-to-lottie` ou `wiggle` (este último é para logos)
- `animate` (Emil), `gsap-*`, `motion-framer`, `animejs`, `react-spring-physics`: animação web em geral
