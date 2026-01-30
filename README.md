<p align="center">
  <h1 align="center">vibemem</h1>
  <p align="center">
    <strong>Universal memory layer for AI coding tools</strong>
  </p>
  <p align="center">
    Stop repeating yourself to Cursor, Claude Code, Copilot, and others.
  </p>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#supported-tools">Supported Tools</a> •
  <a href="#philosophy">Philosophy</a>
</p>

---

## The Problem

Every AI coding session, you waste time:

- Re-explaining your project architecture
- Correcting the same mistakes ("no, the API is on port 8002")
- Reminding about endpoints, credentials, gotchas
- Repeating coding preferences

**When conversations get compacted or sessions end, all that context is lost.**

## The Solution

**vibemem** captures what matters and syncs it to all your AI tools with intelligent compression.

```
┌─────────────────────────────────────────────────────────────┐
│                     One Source of Truth                      │
│                      .vibemem/memories                       │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ CLAUDE.md│   │.cursorrules│ │ copilot  │  ... + 5 more
    │ (10k tok)│   │ (6k tok) │   │ (3k tok) │
    └──────────┘   └──────────┘   └──────────┘
```

## Installation

```bash
pip install vibemem
```

## Quick Start

```bash
# Initialize in your project
vibemem init

# Add memories
vibemem add arch "SAST and DAST are separate systems"
vibemem add api "API runs on port 8002, not 8000"
vibemem add gotcha "Old WP plugins crash due to widget API changes"
vibemem add error "Don't use deprecated sanitize function" -p critical

# Sync to all AI tools
vibemem sync
```

**Output:**
```
✓ claude-code: CLAUDE.md (2,847 tokens)
✓ cursor: .cursorrules (2,102 tokens)
✓ copilot: .github/copilot-instructions.md (1,456 tokens)
✓ aider: .aider.conf.yml (1,891 tokens)
✓ windsurf: .windsurfrules (2,102 tokens)
✓ cline: .clinerules (1,943 tokens)
✓ continue: .continuerules (1,456 tokens)
✓ zed: .zed/prompt.md (1,456 tokens)
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. YOU CODE WITH ANY AI TOOL                                    │
│                                                                 │
│    AI: "I'll call the API on port 8000"                        │
│    You: "no, it's 8002"                                        │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CAPTURE THE MEMORY                                           │
│                                                                 │
│    $ vibemem add api "API runs on port 8002, not 8000"         │
│                                                                 │
│    OR auto-extract from conversation:                           │
│    $ vibemem learn ~/.claude/session.json                       │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. SYNC TO ALL TOOLS                                            │
│                                                                 │
│    $ vibemem sync                                               │
│                                                                 │
│    Each tool gets compressed version fitting its token budget   │
└───────────────────────────┬─────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. NEXT SESSION - AI ALREADY KNOWS                              │
│                                                                 │
│    AI reads CLAUDE.md / .cursorrules / etc. automatically       │
│    AI: "I'll call the API on port 8002..."                     │
└─────────────────────────────────────────────────────────────────┘
```

## Supported Tools

| Tool | Config File | Default Token Budget |
|------|-------------|---------------------|
| **Claude Code** | `CLAUDE.md` | 10,000 |
| **Cursor** | `.cursorrules` | 6,000 |
| **GitHub Copilot** | `.github/copilot-instructions.md` | 3,000 |
| **Aider** | `.aider.conf.yml` | 4,000 |
| **Windsurf** | `.windsurfrules` | 5,000 |
| **Cline** | `.clinerules` | 5,000 |
| **Continue** | `.continuerules` | 4,000 |
| **Zed** | `.zed/prompt.md` | 4,000 |

## Commands

| Command | Description |
|---------|-------------|
| `vibemem init` | Initialize in current project |
| `vibemem init --global` | Initialize global memory (shared across projects) |
| `vibemem add <category> <content>` | Add a memory |
| `vibemem add <category> <content> -p critical` | Add with priority |
| `vibemem show` | Show all memories |
| `vibemem show -c <category>` | Filter by category |
| `vibemem sync` | Sync to all AI tools |
| `vibemem sync -t cursor -t claude-code` | Sync to specific tools |
| `vibemem forget <id>` | Remove a memory |
| `vibemem learn <file>` | Auto-extract memories from conversation log |
| `vibemem context <query>` | Preview what context would load |
| `vibemem stats` | Show memory statistics |

## Categories

| Category | Use For |
|----------|---------|
| `arch` | Architecture, system design, data flow |
| `api` | Endpoints, ports, URLs, request/response formats |
| `gotcha` | Things to watch out for, edge cases |
| `error` | Past mistakes to avoid repeating |
| `cred` | Credentials, API keys (supports encryption) |
| `style` | Coding preferences, conventions |
| `platform` | Platform-specific (hackerone, github, etc.) |

## Intelligent Compression

When memories exceed a tool's token budget, vibemem compresses intelligently:

```
Total memories: 15,000 tokens

Claude Code (10k budget):
├── Critical items ──────────── kept full
├── Architecture/errors ─────── kept full
├── Recent items ────────────── kept full
└── Old low-priority ────────── summarized

Copilot (3k budget):
├── Critical items ──────────── kept full
├── Architecture ────────────── summarized
└── Everything else ─────────── pointers or dropped
```

**Priority system:**
- `critical` — never compressed, never dropped
- `normal` — compressed if needed
- `low` — dropped first when over budget

## Global vs Project Memory

```bash
# Global memory (shared across ALL projects)
vibemem init --global
vibemem add --global style "Always use type hints"
vibemem add --global platform:hackerone "Report format: ..."

# Project memory (this project only)
vibemem init
vibemem add arch "Microservices with gRPC"
```

Both are merged at sync time. Global memories appear in every project.

## Auto-Learning from Conversations

Extract memories automatically from conversation logs:

```bash
vibemem learn ./session.json
```

Detects:
- Corrections ("no, it's port 8002 not 8000")
- Specifications ("the API endpoint is...")
- Gotchas ("watch out for...")
- Architecture decisions

## Configuration

`.vibemem/config.yml`:

```yaml
token_budgets:
  claude-code: 12000
  cursor: 8000
  copilot: 4000

compression:
  strategy: smart          # smart, summarize, truncate
  preserve_categories:     # never compress these
    - critical
    - arch
    - error

sync:
  auto_detect_tools: true
  include_global: true
```

## Philosophy

Inspired by [Manus AI's Context Engineering](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus):

| Principle | Implementation |
|-----------|----------------|
| **File system as extended context** | Memories stored in files, not crammed into prompts |
| **Restorable compression** | Keep pointers when dropping content |
| **Smart retrieval** | Load only what's relevant to current task |
| **Leave errors in** | Past mistakes help avoid future ones |
| **Token budget awareness** | Each tool gets optimally compressed version |

## Project Structure

```
.vibemem/
├── memories.json     # Source of truth
├── hot.md            # Pre-rendered always-load context
├── index.md          # Pointers to detailed memories
└── config.yml        # Your settings

# Generated files (gitignore these or commit them)
CLAUDE.md
.cursorrules
.github/copilot-instructions.md
.aider.conf.yml
.windsurfrules
.clinerules
.continuerules
.zed/prompt.md
```

## Why Not Just Use CLAUDE.md Directly?

You could. But then:
- You're manually maintaining 8 different files
- No compression for tools with smaller context windows
- No global memories shared across projects
- No auto-extraction from conversations
- No priority system for what to keep vs drop

vibemem gives you **one source of truth** that works everywhere.

## Roadmap

- [ ] Hook integration for auto-capture after sessions
- [ ] Encrypted credential storage
- [ ] Semantic search for memory retrieval
- [ ] VSCode/Cursor extension for inline memory capture
- [ ] Team memory sharing (shared memories across team)

## Contributing

PRs welcome! Areas of interest:
- Additional tool adapters
- Better compression algorithms
- LLM-based memory extraction improvements

## License

MIT

---

<p align="center">
  <sub>Built because AI keeps forgetting what you told it 5 minutes ago.</sub>
</p>
