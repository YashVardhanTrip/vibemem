"""vibemem CLI - Universal memory for AI coding tools."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .core.memory import MemoryStore
from .core.config import Config
from .sync.engine import SyncEngine

console = Console()

@click.group()
@click.version_option()
def main():
    """vibemem - Universal memory layer for AI coding tools.

    Stop repeating yourself. Your AI remembers now.
    """
    pass


@main.command()
@click.option('--global', 'is_global', is_flag=True, help='Initialize global memory instead of project')
def init(is_global: bool):
    """Initialize vibemem in current project or globally."""
    if is_global:
        path = Config.global_path()
        scope = "global"
    else:
        path = Path.cwd() / ".vibemem"
        scope = "project"

    if path.exists():
        console.print(f"[yellow]vibemem already initialized at {path}[/yellow]")
        return

    MemoryStore.initialize(path)
    console.print(f"[green]Initialized {scope} vibemem at {path}[/green]")
    console.print("\nNext steps:")
    console.print("  vibemem add arch 'Your architecture overview'")
    console.print("  vibemem add gotcha 'Something to remember'")
    console.print("  vibemem sync")


@main.command()
@click.argument('category')
@click.argument('content')
@click.option('--priority', '-p', type=click.Choice(['critical', 'normal', 'low']), default='normal')
@click.option('--global', 'is_global', is_flag=True, help='Add to global memory')
def add(category: str, content: str, priority: str, is_global: bool):
    """Add a memory item.

    Categories: arch, gotcha, api, cred, style, error, platform, or custom.

    Examples:
        vibemem add arch "SAST and DAST are separate systems"
        vibemem add gotcha "API runs on port 8002, not 8000"
        vibemem add error "Don't use deprecated widget API"
        vibemem add platform:hackerone "Report format: ..."
    """
    store = MemoryStore.load(is_global=is_global)
    store.add(category, content, priority)
    store.save()

    tokens = store.estimate_tokens(content)
    console.print(f"[green]Added to {category}[/green] ({tokens} tokens)")


@main.command()
@click.option('--category', '-c', help='Filter by category')
@click.option('--global', 'is_global', is_flag=True, help='Show global memory')
def show(category: str, is_global: bool):
    """Show current memory."""
    store = MemoryStore.load(is_global=is_global)

    table = Table(title="vibemem" + (" (global)" if is_global else ""))
    table.add_column("Category", style="cyan")
    table.add_column("Priority", style="yellow")
    table.add_column("Content", style="white", max_width=60)
    table.add_column("Tokens", style="dim")

    for item in store.list(category=category):
        table.add_row(
            item['category'],
            item['priority'],
            item['content'][:60] + "..." if len(item['content']) > 60 else item['content'],
            str(item['tokens'])
        )

    console.print(table)
    console.print(f"\n[dim]Total: {store.total_tokens()} tokens[/dim]")


@main.command()
@click.option('--tools', '-t', multiple=True, help='Specific tools to sync (default: all detected)')
@click.option('--dry-run', is_flag=True, help='Show what would be synced without writing')
def sync(tools: tuple, dry_run: bool):
    """Sync memory to all AI coding tools.

    Generates tool-specific config files with appropriate compression:
    - CLAUDE.md (Claude Code)
    - .cursorrules (Cursor)
    - .github/copilot-instructions.md (GitHub Copilot)
    - .aider.conf.yml (Aider)
    - .windsurfrules (Windsurf)
    - .clinerules (Cline)
    """
    engine = SyncEngine()
    results = engine.sync(tools=tools or None, dry_run=dry_run)

    if dry_run:
        console.print("[yellow]Dry run - no files written[/yellow]\n")

    for tool, result in results.items():
        status = "[green]✓[/green]" if result['success'] else "[red]✗[/red]"
        console.print(f"{status} {tool}: {result['path']} ({result['tokens']} tokens)")
        if result.get('compressed'):
            console.print(f"  [dim]Compressed from {result['original_tokens']} tokens[/dim]")


@main.command()
@click.argument('item_id')
@click.option('--global', 'is_global', is_flag=True, help='Remove from global memory')
def forget(item_id: str, is_global: bool):
    """Remove a memory item by ID or content match."""
    store = MemoryStore.load(is_global=is_global)
    removed = store.remove(item_id)

    if removed:
        store.save()
        console.print(f"[green]Removed: {removed['content'][:50]}...[/green]")
    else:
        console.print(f"[red]No matching item found[/red]")


@main.command()
@click.argument('query')
def context(query: str):
    """Preview what memory would be loaded for a query.

    Useful for debugging what context the AI would see.
    """
    store = MemoryStore.load()
    global_store = MemoryStore.load(is_global=True)

    # Merge and filter relevant memories
    relevant = store.get_relevant(query) + global_store.get_relevant(query)

    console.print(f"[cyan]Query:[/cyan] {query}\n")
    console.print("[cyan]Would load:[/cyan]")

    for item in relevant:
        console.print(f"  • [{item['category']}] {item['content'][:60]}...")

    total = sum(item['tokens'] for item in relevant)
    console.print(f"\n[dim]Total context: {total} tokens[/dim]")


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--model', '-m', default='claude', help='Model to use for extraction')
def learn(file: str, model: str):
    """Extract memories from a conversation log or session file.

    Automatically identifies corrections, specifications, and important context.
    """
    from .extract.extractor import extract_memories

    console.print(f"[cyan]Analyzing {file}...[/cyan]")

    memories = extract_memories(Path(file), model=model)

    if not memories:
        console.print("[yellow]No new memories extracted[/yellow]")
        return

    console.print(f"\n[green]Found {len(memories)} potential memories:[/green]\n")

    for i, mem in enumerate(memories, 1):
        console.print(f"{i}. [{mem['category']}] {mem['content']}")

    if click.confirm("\nAdd these to memory?"):
        store = MemoryStore.load()
        for mem in memories:
            store.add(mem['category'], mem['content'], mem.get('priority', 'normal'))
        store.save()
        console.print("[green]Memories added![/green]")


@main.command()
def stats():
    """Show memory statistics."""
    store = MemoryStore.load()
    global_store = MemoryStore.load(is_global=True)
    config = Config.load()

    console.print("[cyan]Memory Statistics[/cyan]\n")

    console.print(f"Project memories: {len(store.list())} ({store.total_tokens()} tokens)")
    console.print(f"Global memories: {len(global_store.list())} ({global_store.total_tokens()} tokens)")
    console.print(f"Combined: {store.total_tokens() + global_store.total_tokens()} tokens")

    console.print("\n[cyan]Token Budgets:[/cyan]")
    for tool, budget in config.token_budgets.items():
        console.print(f"  {tool}: {budget} tokens")


if __name__ == "__main__":
    main()
