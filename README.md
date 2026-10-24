# Maestro

Skill para Claude Code que escolhe sozinha a melhor skill, plugin ou conector (MCP) instalado para cada pedido.
Você descreve o que quer, sem lembrar nomes. O Maestro lê o que está instalado, escolhe, avisa numa linha e executa.

*English: a Claude Code skill that routes each request to the best installed skill, plugin or MCP connector, and keeps token use low.*

## O que ele faz

1. **Lê o inventário:** skills, plugins e conectores que o Claude já vê na sessão. Se precisar, roda `scripts/inventory.py` no disco.
2. **Quebra a tarefa** nos passos reais (planejar, construir, animar, testar...).
3. **Escolhe uma skill por passo**, no máximo três, e avisa numa linha.
4. **Executa:** chama a skill, carrega o conector ou o agente do plugin.
5. **Nada serve?** Procura no GitHub, revisa o código e só instala com o seu ok.

Regras de desempate: a biblioteca que você citou ganha; depois o que o projeto já usa; skill específica ganha da genérica; oficial ganha de terceiros.

### Gasta pouco token

- Código: a menor mudança que resolve. Se houver uma skill enxuta instalada (ex.: `ponytail`), ela entra em toda tarefa de código.
- Projeto grande: primeiro a menor versão que funciona, depois cresce em etapas.
- Busca antes de ler. Vídeo e áudio nunca entram inteiros no contexto.
- Pedido vago em trabalho caro: uma pergunta com resposta padrão, em vez de adivinhar e refazer.

### Exemplo: "edita esse vídeo pra mim"

1. Vê um conector de vídeo (ex.: Adobe: `video_create_quick_cut`, `media_enhance_speech`, `video_resize`) e a skill `remotion-motion-graphics`.
2. Escolhe o conector para vídeo cru (trabalha no arquivo). Remotion só se você quiser títulos e motion.
3. Pergunta uma vez: "Para onde é? (padrão: Reels 9:16, até 60s, sem silêncios)".
4. Corta silêncios, limpa a voz, ajusta o formato e devolve o link com o resumo do que mudou.

## Instalar

Precisa do [Claude Code](https://claude.com/claude-code). Python 3 só é usado pelo scanner de disco.

**macOS / Linux**

```bash
git clone https://github.com/tarcisiobardeja/claude-maestro
cp -r claude-maestro/maestro ~/.claude/skills/
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/tarcisiobardeja/claude-maestro
Copy-Item -Recurse claude-maestro\maestro $HOME\.claude\skills\
```

Abra uma sessão nova do Claude Code. Teste: `python ~/.claude/skills/maestro/scripts/test_inventory.py` (dentro da pasta `scripts`) deve imprimir `ok`.

## Usar

Só peça o que quer: "quero um site de roleta animado", "anima esse logo", "lista minhas skills", "acha skills duplicadas".

Scanner direto:

```bash
python ~/.claude/skills/maestro/scripts/inventory.py           # catálogo
python ~/.claude/skills/maestro/scripts/inventory.py --dupes   # sobreposições
python ~/.claude/skills/maestro/scripts/inventory.py --json
```

O scanner só lê. Não envia nada para fora e não apaga nada.

## Skills e plugins recomendados

Veja [CATALOG.md](CATALOG.md): o conjunto que eu uso junto com o Maestro, com link para o repositório original e o comando de instalação de cada um. Instale só o que quiser.

## Limites

- Conectores web do claude.ai (Gmail, Drive, Agenda) não ficam no disco. O Maestro só os vê dentro da sessão.
- Conectores que pedem login ficam inutilizáveis até rodar `/mcp`.
- O detector de duplicatas compara palavras das descrições, então também aponta pares parecidos que não são duplicatas. Revise antes de apagar.

## Licença

MIT. Veja [LICENSE](LICENSE).
