#!/usr/bin/env python3

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from cheat_sheet_agent import CheatSheetAgent

console = Console()

@click.group()
def cli():
    """🤖 AI Cheat Sheet Generator - Create comprehensive cheat sheets for any technology!"""
    pass

@cli.command()
@click.option('--topic', '-t', help='Technology/topic for the cheat sheet', required=True)
@click.option('--difficulty', '-d', 
              type=click.Choice(['beginner', 'intermediate', 'advanced']),
              default='intermediate',
              help='Difficulty level')
@click.option('--format-style', '-f',
              type=click.Choice(['quick-reference', 'comprehensive']),
              default='comprehensive',
              help='Format style')
@click.option('--no-examples', is_flag=True, help='Exclude code examples')
@click.option('--preview', '-p', is_flag=True, help='Preview before saving')
@click.option('--sections', '-s', help='Comma-separated list of specific sections to include')
def generate(topic, difficulty, format_style, no_examples, preview, sections):
    """Generate a cheat sheet for a specific technology or topic."""
    
    console.print(Panel.fit(
        f"[bold blue]🚀 AI CHEAT SHEET GENERATOR[/bold blue]\n"
        f"[dim]Creating cheat sheet for: [bold]{topic}[/bold][/dim]",
        border_style="blue"
    ))
    
    agent = CheatSheetAgent()
    
    sections_list = None
    if sections:
        sections_list = [s.strip() for s in sections.split(',')]
    
    filepath = agent.create_cheat_sheet(
        topic=topic,
        difficulty=difficulty,
        sections=sections_list,
        format_style=format_style,
        include_examples=not no_examples,
        preview=preview
    )
    
    if filepath:
        console.print(f"\n[green]🎉 Successfully created cheat sheet![/green]")
        console.print(f"[dim]File location: {filepath}[/dim]")
    else:
        console.print("[red]❌ Failed to generate cheat sheet[/red]")

@cli.command()
def interactive():
    """Interactive mode for creating cheat sheets."""
    
    console.print(Panel.fit(
        "[bold blue]🤖 INTERACTIVE CHEAT SHEET GENERATOR[/bold blue]\n"
        "[dim]Let's create your perfect cheat sheet![/dim]",
        border_style="blue"
    ))
    
    topic = Prompt.ask("[bold]What technology/topic would you like a cheat sheet for?[/bold]")
    
    difficulty = Prompt.ask(
        "[bold]Difficulty level[/bold]",
        choices=['beginner', 'intermediate', 'advanced'],
        default='intermediate'
    )
    
    format_style = Prompt.ask(
        "[bold]Format style[/bold]",
        choices=['quick-reference', 'comprehensive'],
        default='comprehensive'
    )
    
    include_examples = Confirm.ask("[bold]Include code examples?[/bold]", default=True)
    
    sections_input = Prompt.ask(
        "[bold]Specific sections to include[/bold] (comma-separated, or press Enter for all)",
        default=""
    )
    
    sections_list = None
    if sections_input.strip():
        sections_list = [s.strip() for s in sections_input.split(',')]
    
    preview = Confirm.ask("[bold]Preview before saving?[/bold]", default=False)
    
    agent = CheatSheetAgent()
    filepath = agent.create_cheat_sheet(
        topic=topic,
        difficulty=difficulty,
        sections=sections_list,
        format_style=format_style,
        include_examples=include_examples,
        preview=preview
    )
    
    if filepath:
        console.print(f"\n[green]🎉 Successfully created cheat sheet![/green]")
        console.print(f"[dim]File location: {filepath}[/dim]")
    else:
        console.print("[red]❌ Failed to generate cheat sheet[/red]")

@cli.command()
def examples():
    """Show example commands and topics."""
    
    console.print("[bold blue]📚 Example Topics & Commands[/bold blue]\n")
    
    table = Table(title="Popular Topics")
    table.add_column("Category", style="cyan")
    table.add_column("Examples", style="green")
    
    table.add_row("Python Libraries", "pandas, numpy, matplotlib, scikit-learn, tensorflow")
    table.add_row("Web Frameworks", "React, Vue.js, Django, Flask, FastAPI")
    table.add_row("Databases", "PostgreSQL, MongoDB, Redis, SQLite")
    table.add_row("DevOps", "Docker, Kubernetes, AWS, Git, Linux")
    table.add_row("Machine Learning", "PyTorch, Hugging Face, OpenCV, NLTK")
    table.add_row("Languages", "JavaScript, Python, Go, Rust, TypeScript")
    
    console.print(table)
    
    console.print("\n[bold yellow]Example Commands:[/bold yellow]")
    console.print("• [dim]python main.py generate -t 'pandas' -d intermediate[/dim]")
    console.print("• [dim]python main.py generate -t 'React Hooks' -f quick-reference --preview[/dim]")
    console.print("• [dim]python main.py generate -t 'Docker' -s 'commands,dockerfile,compose'[/dim]")
    console.print("• [dim]python main.py interactive[/dim]")

@cli.command()
def setup():
    """Setup the environment and API key."""
    
    console.print("[bold blue]🔧 Environment Setup[/bold blue]\n")
    
    console.print("1. Install dependencies:")
    console.print("   [dim]pip install -r requirements.txt[/dim]\n")
    
    console.print("2. Set up your OpenAI API key:")
    console.print("   [dim]cp .env.example .env[/dim]")
    console.print("   [dim]# Edit .env file and add your API key[/dim]\n")
    
    console.print("3. Create your first cheat sheet:")
    console.print("   [dim]python main.py interactive[/dim]\n")
    
    console.print("[yellow]💡 Get your OpenAI API key from: https://platform.openai.com/api-keys[/yellow]")

if __name__ == '__main__':
    cli()