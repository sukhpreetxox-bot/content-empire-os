# 🧰 Tool Map — free tools to upscale (researched: web, GitHub, Reddit)

Legend: **MCP** = add as a connector Claude can call · **API** = call from the pipeline (cron-safe) · **Skill/Agent** = Claude Code skill/subagent · **Repo** = open-source code to reuse.

## ⭐ Game-changers (free, automatable, highest impact)

| Tool | Free? | Plug-in | Why it matters |
|---|---|---|---|
| **Pollinations AI** | ✅ **no API key** | MCP `npx @pollinations_ai/mcp` **or** HTTP API (cron-safe) | The big one. Free **image** (Flux, seedream, nanobanana), **VIDEO** (veo, seedance, wan), **TTS**, text. Solves free AI b-roll *and* AI video/animation. Rate: anon 1/15s, free signup 1/5s → throttle. |
| **whisper-timestamped / faster-whisper** | ✅ local | API/Repo in pipeline | **Word-level timestamps** of the Kokoro voice → frame-accurate karaoke captions (vs our current estimate). Runs CPU on Actions. |
| **YouTube Data API + Google Trends (pytrends)** | ✅ (10k units/day) | API in pipeline | **Find winning topics** by search velocity/opportunity instead of random topics → directly drives VIEWS. |

## 🎬 Video / image / animation
| Tool | Free? | Plug-in | Notes |
|---|---|---|---|
| Pollinations (above) | ✅ | MCP/API | best free all-rounder |
| FLUX.1 schnell (Together) | ✅ tier | API | high-quality stills, commercial OK |
| Manim MCP | ✅ | MCP | programmatic math/data animations (great for finance charts) |
| Higgsfield MCP | 💳 credits | MCP (connected) | cinematic hero shots; paid credits — use sparingly |
| mcp-kling | 💳 | MCP | Kling video; paid |
| Remotion (ours) | ✅ | code | the compositor that ties it together |

## 🎙️ Voice / audio
| Kokoro (ours) | ✅ | code | primary TTS |
| Pollinations TTS / Piper | ✅ | MCP/API | extra voices/variety |
| Pixabay Music / YouTube Audio Library / Freesound CC0 | ✅ | drop files | background music (ours mixes+ducks) |

## 🔎 Research / SEO / growth
| YouTube Data API v3 | ✅ 10k/day | API | trend search, competitor titles, tags |
| Google Trends (pytrends) | ✅ | API | rising queries |
| KeywordTool.io / autocomplete scrape | ✅ basic | API | long-tail titles |

## 🤖 Claude Code skills & subagents (the "agents beside you")
| Source | What |
|---|---|
| `wshobson/agents` | 192 agents / 156 skills marketplace |
| `VoltAgent/awesome-claude-code-subagents` | 100+ specialised subagents |
| `rohitg00/awesome-claude-code-toolkit` | agents + 35 skills + MCP configs |
| awesome-skills.com / awesomeclaude.ai | curated skill directories |
| **Custom (ours)** | I can author project subagents: `trend-researcher`, `seo-titler`, `thumbnail-art-director`, `script-critic`, `policy-qa` in `.claude/agents/` |

## 📌 Recommended build order (all free, I can implement)
1. **Pollinations images** → AI scene visuals per script beat (replace generic b-roll) — biggest visual jump.
2. **Whisper word-level captions** → perfectly synced karaoke.
3. **Trend-research step** → topics chosen for views, not random.
4. **Custom subagents** (research / SEO titles / thumbnail / critic).
5. **Pollinations video** → short AI motion clips for Shorts hero moments.

## Sources
- https://github.com/punkpeye/awesome-mcp-servers · https://mcpservers.org/
- https://pollinations.ai/ · https://github.com/pollinations/pollinations · https://github.com/pollinations/pollinations/blob/main/APIDOCS.md
- https://github.com/absadiki/subsai · https://github.com/linto-ai/whisper-timestamped · https://github.com/tmoroney/auto-subs
- https://github.com/wshobson/agents · https://github.com/VoltAgent/awesome-claude-code-subagents · https://github.com/rohitg00/awesome-claude-code-toolkit
- https://apify.com/sleek_waveform/youtube-trend-spotter · https://vidiq.com/blog/post/find-trending-topics-youtube-videos/
