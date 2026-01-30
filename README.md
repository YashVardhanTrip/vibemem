<div align="center">

# 🧠 vibemem

### **Your AI finally remembers.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

*Universal memory layer for AI coding assistants.*
*One command. All your tools. Zero repetition.*

[Installation](#-installation) • [Quick Start](#-quick-start) • [How It Works](#-how-it-works) • [Supported Tools](#-supported-tools)

---

</div>

## 😤 The Problem

```
You: "The API runs on port 8002"
AI:  "Got it!"

... 10 minutes later ...

AI:  "I'll call the API on port 8000"
You: "I JUST TOLD YOU IT'S 8002"
```

Every. Single. Session.

- 🔄 Re-explaining your architecture
- 🤦 Correcting the same mistakes
- 📝 Repeating endpoints, ports, credentials
- 😩 Context lost after compaction

**AI tools don't remember. You pay the tax.**

---

## 💡 The Solution

**vibemem** = One memory → All tools → Smart compression

```
                    ┌─────────────────────┐
                    │   vibemem memory    │
                    │   (single source)   │
                    └──────────┬──────────┘
                               │
        ┌──────────┬───────────┼───────────┬──────────┐
        ▼          ▼           ▼           ▼          ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Claude  │ │ Cursor  │ │ Copilot │ │  Aider  │ │   +4    │
   │  Code   │ │         │ │         │ │         │ │  more   │
   │ 10k tok │ │ 6k tok  │ │ 3k tok  │ │ 4k tok  │ │         │
   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
```

Each tool gets **optimally compressed** context that fits its budget.

---

## 📦 Installation

```bash
pip install vibemem
```

---

## 🚀 Quick Start

```bash
# 1. Initialize
vibemem init

# 2. Add memories
vibemem add arch "Microservices: API (8002) → Queue (Redis) → Workers"
vibemem add api "Auth endpoint: POST /api/v2/auth (not v1)"
vibemem add gotcha "Old WP plugins crash - widget API deprecated"
vibemem add error "NEVER use md5 for passwords" -p critical

# 3. Sync everywhere
vibemem sync
```

**Output:**
```
✓ claude-code    CLAUDE.md                         (2,847 tokens)
✓ cursor         .cursorrules                      (2,102 tokens)
✓ copilot        .github/copilot-instructions.md   (1,456 tokens)
✓ aider          .aider.conf.yml                   (1,891 tokens)
✓ windsurf       .windsurfrules                    (2,102 tokens)
✓ cline          .clinerules                       (1,943 tokens)
✓ continue       .continuerules                    (1,456 tokens)
✓ zed            .zed/prompt.md                    (1,456 tokens)
```

**Next session:** AI already knows everything. No repetition.

---

## ⚙️ How It Works

```
╭──────────────────────────────────────────────────────────────────╮
│  STEP 1: You're coding, AI screws up                             │
│                                                                  │
│  AI:  "Connecting to database on port 5432..."                   │
│  You: "No idiot, we use 5433 in dev"                             │
╰──────────────────────────────────────────────────────────────────╯
                              ▼
╭──────────────────────────────────────────────────────────────────╮
│  STEP 2: Capture it (2 seconds)                                  │
│                                                                  │
│  $ vibemem add api "Dev DB port: 5433 (not default 5432)"        │
╰──────────────────────────────────────────────────────────────────╯
                              ▼
╭──────────────────────────────────────────────────────────────────╮
│  STEP 3: Sync once                                               │
│                                                                  │
│  $ vibemem sync                                                  │
│                                                                  │
│  → Writes to CLAUDE.md, .cursorrules, copilot, aider, etc.       │
│  → Each file compressed to fit tool's token limit                │
╰──────────────────────────────────────────────────────────────────╯
                              ▼
╭──────────────────────────────────────────────────────────────────╮
│  STEP 4: Never repeat yourself again                             │
│                                                                  │
│  AI:  "Connecting to database on port 5433..."                   │
│  You: 😎                                                         │
╰──────────────────────────────────────────────────────────────────╯
```

---

## 🛠 Supported Tools

| Tool | Config File | Token Budget |
|:-----|:------------|:------------:|
| **Claude Code** | `CLAUDE.md` | 10,000 |
| **Cursor** | `.cursorrules` | 6,000 |
| **GitHub Copilot** | `.github/copilot-instructions.md` | 3,000 |
| **Aider** | `.aider.conf.yml` | 4,000 |
| **Windsurf** | `.windsurfrules` | 5,000 |
| **Cline** | `.clinerules` | 5,000 |
| **Continue** | `.continuerules` | 4,000 |
| **Zed AI** | `.zed/prompt.md` | 4,000 |

> Budgets are configurable. These are sensible defaults.

---

## 📋 Commands

| Command | What it does |
|:--------|:-------------|
| `vibemem init` | Initialize in current project |
| `vibemem init --global` | Initialize global memory (all projects) |
| `vibemem add <cat> "text"` | Add a memory |
| `vibemem add <cat> "text" -p critical` | Add as critical (never dropped) |
| `vibemem show` | List all memories |
| `vibemem sync` | Push to all tool configs |
| `vibemem learn <file>` | Auto-extract from conversation log |
| `vibemem forget <id>` | Remove a memory |
| `vibemem stats` | Show token usage stats |

---

## 🏷 Categories

| Category | Use for | Example |
|:---------|:--------|:--------|
| `arch` | Architecture, design | `"Event-driven with Kafka"` |
| `api` | Endpoints, ports | `"API v2 on port 8002"` |
| `gotcha` | Watch out for... | `"Redis times out after 30s"` |
| `error` | Don't repeat this | `"Don't use SELECT *"` |
| `cred` | Secrets (encrypted) | `"API key in .env.local"` |
| `style` | Preferences | `"Always use TypeScript"` |
| `platform` | Platform-specific | `"HackerOne: use CVSS 3.1"` |

---

## 🗜 Smart Compression

When memories exceed token budget, vibemem compresses **intelligently**:

```
Your memories: 15,000 tokens

┌─────────────────────────────────────────────────────────────┐
│ Claude Code (10k budget)                                    │
├─────────────────────────────────────────────────────────────┤
│ ✓ Critical items          → kept full                       │
│ ✓ Architecture/errors     → kept full                       │
│ ✓ Recent memories         → kept full                       │
│ ~ Old low-priority        → summarized                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Copilot (3k budget)                                         │
├─────────────────────────────────────────────────────────────┤
│ ✓ Critical only           → kept full                       │
│ ~ Architecture            → summarized                      │
│ ✗ Low priority            → dropped                         │
└─────────────────────────────────────────────────────────────┘
```

**Priority levels:**
- `critical` — Never touched. Ever.
- `normal` — Compressed if needed
- `low` — First to go

---

## 🌍 Global vs Project Memory

```bash
# Global = shared across ALL your projects
vibemem init --global
vibemem add --global style "Always use conventional commits"
vibemem add --global platform:hackerone "Template: ## Summary\n..."

# Project = just this repo
vibemem init
vibemem add arch "Django + Celery + Postgres"
```

**Sync merges both.** Global context everywhere, project-specific where needed.

---

## 🤖 Auto-Learn from Conversations

Don't manually add everything. Extract from past sessions:

```bash
vibemem learn ./claude-session.json
```

**Automatically detects:**
- ✅ Corrections (*"no, it's 8002 not 8000"*)
- ✅ Specifications (*"the endpoint is /api/v2/..."*)
- ✅ Gotchas (*"careful, this breaks on Safari"*)
- ✅ Preferences (*"always use async/await"*)

---

## 🔧 Configuration

`.vibemem/config.yml`:

```yaml
token_budgets:
  claude-code: 12000    # customize per tool
  cursor: 8000
  copilot: 4000

compression:
  strategy: smart
  preserve_categories:
    - critical
    - arch
    - error

sync:
  auto_detect_tools: true
  include_global: true
```

---

## 🧬 Philosophy

Built on principles from [Manus AI's Context Engineering](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus):

| Principle | How vibemem implements it |
|:----------|:--------------------------|
| File system as context | Memories in files, not stuffed in prompts |
| Restorable compression | Pointers preserved when content dropped |
| Smart retrieval | Only relevant memories loaded |
| Keep errors | Past mistakes prevent future ones |
| Token awareness | Each tool gets optimized version |

---

## 🗺 Roadmap

- [ ] **Hooks** — Auto-capture after Claude Code sessions
- [ ] **Encryption** — Secure credential storage
- [ ] **Semantic search** — Find memories by meaning
- [ ] **VS Code extension** — Capture without leaving editor
- [ ] **Team sync** — Shared memories across team

---

## 🤝 Contributing

PRs welcome. High-impact areas:

- New tool adapters
- Better compression algorithms
- LLM extraction improvements
- Documentation & examples

---

## 📄 License

MIT

---

<div align="center">

**Built because AI keeps forgetting what you said 5 minutes ago.**

[Report Bug](https://github.com/YashVardhanTrip/vibemem/issues) · [Request Feature](https://github.com/YashVardhanTrip/vibemem/issues)

</div>
