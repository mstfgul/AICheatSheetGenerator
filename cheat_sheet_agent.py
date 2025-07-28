import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

import openai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from config import Config

load_dotenv()

class CheatSheetConfig(BaseModel):
    topic: str = Field(..., description="The technology or topic for the cheat sheet")
    difficulty_level: str = Field(default="intermediate", description="beginner, intermediate, or advanced")
    sections: Optional[list] = Field(default=None, description="Specific sections to include")
    format_style: str = Field(default="comprehensive", description="quick-reference or comprehensive")
    include_examples: bool = Field(default=True, description="Include code examples")

class CheatSheetAgent:
    def __init__(self):
        self.config = Config()
        api_key = self.config.get_api_key()
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env file or config.")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.console = Console()
        
        output_dir_name = self.config.get("output_directory", "cheat_sheets")
        self.output_dir = Path(output_dir_name)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_cheat_sheet(self, config: CheatSheetConfig) -> str:
        prompt = self._create_prompt(config)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert technical writer and educator who creates comprehensive, well-structured cheat sheets for various technologies. Your cheat sheets are accurate, practical, and beautifully formatted in Markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 16000)
            )
            
            content = response.choices[0].message.content
            
            # Check if content is too short and retry with more explicit instructions
            if len(content) < 5000:
                self.console.print("[yellow]⚠️ Content seems short, requesting more comprehensive version...[/yellow]")
                
                enhanced_prompt = f"""
The previous response was too brief. Please create a MUCH MORE COMPREHENSIVE cheat sheet for {config.topic}.

REQUIREMENTS:
- Write EVERYTHING in ENGLISH language only
- Minimum 8000+ words
- Include at least 75 code examples
- Cover ALL major aspects in detail
- Add extensive explanations for each concept
- Include multiple approaches for each task
- Add real-world scenarios and use cases
- For libraries: Include TOP 50+ most used methods with complete documentation

{prompt}

IMPORTANT: Make this substantially longer and more detailed than a typical cheat sheet. This should be a complete learning resource.
"""
                
                response = self.client.chat.completions.create(
                    model=self.config.get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert technical writer who creates extremely comprehensive, detailed reference documents. Never provide brief or summary content - always create extensive, complete guides."
                        },
                        {
                            "role": "user",
                            "content": enhanced_prompt
                        }
                    ],
                    temperature=self.config.get("temperature", 0.7),
                    max_tokens=self.config.get("max_tokens", 16000)
                )
                content = response.choices[0].message.content
            
            return content
            
        except Exception as e:
            self.console.print(f"[red]Error generating cheat sheet: {str(e)}[/red]")
            return None
    
    def _create_prompt(self, config: CheatSheetConfig) -> str:
        base_prompt = f"""
Create an EXTREMELY COMPREHENSIVE and DETAILED cheat sheet for {config.topic} targeted at {config.difficulty_level} level users.

CRITICAL REQUIREMENTS:
- Write EVERYTHING in ENGLISH language only
- This must be a COMPLETE, PROFESSIONAL-GRADE reference document
- Format: Rich, well-structured Markdown with extensive content
- Style: {config.format_style} - but always err on the side of MORE content
- Include examples: {config.include_examples} - provide MULTIPLE examples for each concept
- Use proper Markdown syntax with headers, code blocks, tables, and lists
- Add emojis for visual appeal and better organization
- Include a detailed table of contents with clickable links
- Organize content logically with MANY clear sections and subsections
- Minimum 75+ code examples across different use cases
- Include edge cases, advanced techniques, and real-world scenarios
- For libraries: Focus extensively on the MOST COMMONLY USED and PRACTICAL methods/functions
- For libraries: Include comprehensive method reference with parameters, return values, and examples

"""
        
        if config.sections:
            base_prompt += f"Focus extensively on these sections with deep detail: {', '.join(config.sections)}\n"
        
        structure_guide = f"""
MANDATORY STRUCTURE - Each section must be COMPREHENSIVE:

# 🔥 {config.topic} - Complete Reference Guide

## 📑 Table of Contents
(Detailed TOC with all sections and subsections)

## 🚀 Installation & Setup
- Multiple installation methods
- Environment setup
- Version compatibility
- Common installation issues and solutions

## 🎯 Quick Start Guide  
- Basic setup
- First steps
- Hello world examples
- Initial configuration

## 📊 Core Concepts & Fundamentals
- Key terminology and definitions
- Underlying principles
- Architecture overview
- How it works internally

## 🔧 Basic Syntax & Operations
- Fundamental syntax
- Basic operations
- Data types and structures
- Essential functions/methods

## 💡 Intermediate Concepts
- Advanced syntax
- Complex operations
- Design patterns
- Best practices

## 🚀 Advanced Techniques
- Expert-level features
- Performance optimization
- Advanced patterns
- Complex scenarios

## 📝 Comprehensive Code Examples
- Beginner examples (15+ examples)
- Intermediate examples (20+ examples) 
- Advanced examples (15+ examples)
- Real-world use cases (15+ examples)
- Complete mini-projects (5+ projects)

## 📋 Essential Methods/Functions Reference
- TOP 50 most commonly used methods/functions with full details
- Complete parameter lists with types and descriptions
- Return value specifications
- Multiple usage examples for each method
- Performance considerations for each method
- Common use cases and patterns

## 🔧 Method Categories (for libraries)
- Data Creation & Loading methods
- Data Inspection & Information methods
- Data Selection & Filtering methods
- Data Transformation & Manipulation methods
- Data Aggregation & Grouping methods
- Data Cleaning & Preprocessing methods
- Data Export & Saving methods
- Performance & Memory methods

## 🔍 Common Use Cases & Patterns
- Typical workflows
- Standard patterns
- Problem-solving approaches
- Industry best practices

## ⚡ Performance & Optimization
- Performance tips
- Memory management
- Speed optimization
- Profiling techniques

## 🐛 Debugging & Troubleshooting
- Common errors and solutions
- Debugging techniques
- Logging and monitoring
- Error handling patterns

## ⚠️ Common Pitfalls & Gotchas
- Frequent mistakes
- What to avoid
- Edge cases
- Security considerations

## 🔗 Integration & Ecosystem
- Related tools and libraries
- Integration patterns
- Ecosystem overview
- Complementary technologies

## 📚 Additional Resources
- Official documentation
- Tutorials and courses
- Books and articles
- Community resources
- Tools and extensions

## 🎓 Practice Exercises
- Hands-on exercises
- Project ideas
- Challenges by difficulty level

CONTENT REQUIREMENTS:
- Write EVERYTHING in ENGLISH language - no other languages
- Each section must have substantial content (not just bullet points)
- Provide detailed explanations for every concept in English
- Include practical, working code examples with English comments
- Add tips, warnings, and best practices throughout
- Use tables for comparisons and reference data
- Include diagrams in ASCII art where helpful
- Provide multiple approaches to solve common problems
- Cover both theory and practical application
- Include version differences where relevant
- Add performance considerations
- Include security aspects where applicable
- For programming libraries: Include the TOP 50+ most essential and frequently used methods
- For each method: parameter types, descriptions, return values, and 2-3 usage examples
- Focus on methods that 80% of users will need in daily work
- Include method chaining examples and common patterns
- Add memory usage and performance tips for each major operation

SPECIAL FOCUS FOR LIBRARIES (like pandas, numpy, requests, etc.):
- Dedicate 40% of content to essential methods documentation
- Create comprehensive method reference tables
- Include method categories by functionality
- Show real-world usage patterns for each method
- Include troubleshooting for common method errors

The cheat sheet should be so comprehensive that someone could learn the technology from scratch using only this document, while also serving as a complete reference for experienced users.

MINIMUM LENGTH: This should be a substantial document with 150+ distinct pieces of information, examples, and explanations.
TARGET: 8000+ words for truly comprehensive coverage.
"""
        
        return base_prompt + structure_guide
    
    def save_cheat_sheet(self, content: str, topic: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic.lower().replace(' ', '_')}_{timestamp}.md"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return str(filepath)
        except Exception as e:
            self.console.print(f"[red]Error saving file: {str(e)}[/red]")
            return None
    
    def preview_cheat_sheet(self, content: str):
        md = Markdown(content)
        panel = Panel(md, title="📋 Cheat Sheet Preview", border_style="blue")
        self.console.print(panel)
    
    def create_cheat_sheet(self, topic: str, difficulty: str = "intermediate", 
                          sections: Optional[list] = None, format_style: str = "comprehensive",
                          include_examples: bool = True, preview: bool = False) -> Optional[str]:
        
        config = CheatSheetConfig(
            topic=topic,
            difficulty_level=difficulty,
            sections=sections,
            format_style=format_style,
            include_examples=include_examples
        )
        
        self.console.print(f"[yellow]🤖 Generating cheat sheet for: {topic}[/yellow]")
        self.console.print(f"[dim]Difficulty: {difficulty} | Style: {format_style}[/dim]")
        
        content = self.generate_cheat_sheet(config)
        
        if not content:
            return None
        
        if preview:
            self.preview_cheat_sheet(content)
        
        filepath = self.save_cheat_sheet(content, topic)
        
        if filepath:
            self.console.print(f"[green]✅ Cheat sheet saved to: {filepath}[/green]")
            return filepath
        
        return None