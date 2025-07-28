import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

import openai
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from config import Config

load_dotenv()

class PracticeConfig(BaseModel):
    topic: str = Field(..., description="The technology or topic for practice exercises")
    difficulty_level: str = Field(default="intermediate", description="beginner, intermediate, or advanced")
    exercise_count: int = Field(default=20, description="Number of exercises to generate")
    include_solutions: bool = Field(default=True, description="Include detailed solutions")
    exercise_types: Optional[List[str]] = Field(default=None, description="Types of exercises to include")
    focus_areas: Optional[List[str]] = Field(default=None, description="Specific areas to focus on")

class PracticeGenerator:
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
        
        # Create practices subdirectory
        self.practice_dir = self.output_dir / "practices"
        self.practice_dir.mkdir(exist_ok=True)
    
    def generate_practice_exercises(self, config: PracticeConfig) -> str:
        prompt = self._create_practice_prompt(config)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.get("model", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator and practical coding instructor who creates comprehensive, progressive practice exercises. Your exercises are designed to build real-world skills through hands-on learning, ranging from basic concepts to complex applications. You create exercises that simulate actual work scenarios and challenges developers face."
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
            
            # Check if content needs to be more comprehensive
            if len(content) < 6000:
                self.console.print("[yellow]⚠️ Generating more comprehensive exercises...[/yellow]")
                
                enhanced_prompt = f"""
The previous response was too brief. Please create a MUCH MORE COMPREHENSIVE practice document for {config.topic}.

REQUIREMENTS:
- Write EVERYTHING in ENGLISH language only
- Minimum 10,000+ words
- Include at least {config.exercise_count} detailed exercises
- Progressive difficulty from basic to advanced
- Real-world scenarios and projects
- Complete solutions with explanations
- Multiple approaches for complex problems
- Industry-standard practices and patterns

{prompt}

IMPORTANT: Make this a complete practical learning resource with extensive exercises and detailed solutions.
"""
                
                response = self.client.chat.completions.create(
                    model=self.config.get("model", "gpt-4o"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert practical coding instructor who creates extremely comprehensive, detailed practice documents. Never provide brief content - always create extensive, complete practical learning resources."
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
            self.console.print(f"[red]Error generating practice exercises: {str(e)}[/red]")
            return None
    
    def _create_practice_prompt(self, config: PracticeConfig) -> str:
        exercise_types = config.exercise_types or [
            "Basic Concepts", 
            "Practical Applications", 
            "Problem Solving", 
            "Real-world Projects", 
            "Code Debugging", 
            "Performance Optimization",
            "Best Practices",
            "Integration Challenges"
        ]
        
        base_prompt = f"""
Create an EXTREMELY COMPREHENSIVE and PRACTICAL exercise document for {config.topic} targeted at {config.difficulty_level} level learners.

CRITICAL REQUIREMENTS:
- Write EVERYTHING in ENGLISH language only
- This must be a COMPLETE, HANDS-ON learning resource
- Format: Rich, well-structured Markdown with extensive practical content
- Difficulty Level: {config.difficulty_level} - but include progressive difficulty
- Include solutions: {config.include_solutions} - provide DETAILED solutions with explanations
- Number of exercises: {config.exercise_count}+ exercises across different categories
- Use proper Markdown syntax with headers, code blocks, tables, and lists
- Add emojis for visual appeal and better organization
- Include a detailed table of contents with clickable links
- Organize exercises by category and difficulty
- Include real-world scenarios and industry-standard problems
- Provide multiple solution approaches where applicable
- Include code reviews and best practice explanations
"""
        
        if config.focus_areas:
            base_prompt += f"Focus extensively on these areas: {', '.join(config.focus_areas)}\n"
        
        structure_guide = f"""
MANDATORY STRUCTURE - Each section must be COMPREHENSIVE:

# 🎯 {config.topic} - Comprehensive Practice Exercises

## 📑 Table of Contents
(Detailed TOC with all exercise categories and individual exercises)

## 🚀 Getting Started
- Setup instructions for practice environment
- Required tools and dependencies
- How to use this practice guide
- Recommended learning path

## 📊 Skill Assessment
- Pre-assessment quiz (10 questions)
- Skill level determination
- Personalized learning recommendations
- Progress tracking guide

## 🎓 Exercise Categories

### 🌱 Beginner Level ({config.exercise_count//4} exercises)
**Category 1: Fundamentals & Basic Syntax**
- Exercise 1: [Title] - [Brief description]
  - **Objective**: Clear learning goal
  - **Difficulty**: ⭐☆☆☆☆
  - **Time Estimate**: X minutes
  - **Prerequisites**: What you need to know
  - **Problem Statement**: Detailed problem description
  - **Input/Output Examples**: Clear examples
  - **Hints**: Progressive hints
  - **Solution**: Complete solution with explanation
  - **Alternative Solutions**: Different approaches
  - **Code Review**: Best practices and improvements
  - **Extension Challenges**: Ways to extend the exercise

**Category 2: Basic Operations**
[Similar structure for each exercise]

### 🌿 Intermediate Level ({config.exercise_count//3} exercises)
**Category 3: Practical Applications**
**Category 4: Data Manipulation & Processing**
**Category 5: Problem Solving Patterns**

### 🌳 Advanced Level ({config.exercise_count//3} exercises)
**Category 6: Complex Scenarios**
**Category 7: Performance Optimization**
**Category 8: Integration & Real-world Projects**

### 🚀 Expert Level ({config.exercise_count//4} exercises)
**Category 9: Advanced Techniques**
**Category 10: System Design & Architecture**

## 🏗️ Mini Projects (5-7 complete projects)
Each project should include:
- **Project Overview**: What you'll build
- **Learning Objectives**: Skills you'll develop
- **Requirements**: Functional and technical requirements
- **Architecture**: System design and structure
- **Step-by-step Implementation**: Detailed implementation guide
- **Testing Strategy**: How to test your solution
- **Deployment Guide**: How to deploy/run the project
- **Extensions**: Ways to improve and extend

### Project 1: [Name] - Beginner Project
### Project 2: [Name] - Intermediate Project
### Project 3: [Name] - Advanced Project
etc.

## 🔧 Code Review Exercises (10+ exercises)
- Common code issues to identify and fix
- Performance problems to optimize
- Security vulnerabilities to address
- Best practice violations to correct

## 🐛 Debugging Challenges (10+ exercises)
- Broken code to fix
- Logic errors to identify
- Performance issues to resolve
- Integration problems to solve

## 🏆 Coding Challenges & Competitions
- Algorithm challenges
- Time-limited exercises
- Optimization competitions
- Creative problem-solving tasks

## 📈 Progress Tracking
- Skill progression checklist
- Exercise completion tracker
- Performance metrics
- Next steps recommendations

## 🎯 Real-world Scenarios
- Industry-specific use cases
- Common workplace problems
- Client requirement simulations
- Team collaboration exercises

## 💡 Tips & Best Practices
- Development workflow tips
- Common pitfalls to avoid
- Performance optimization tips
- Code quality guidelines

## 📚 Additional Challenges
- Bonus exercises for extra practice
- Competition-style problems
- Open-ended creative challenges
- Research and exploration tasks

## 🔗 Resources & Next Steps
- Additional learning resources
- Advanced topics to explore
- Community and forums
- Professional development paths

EXERCISE FORMAT REQUIREMENTS:
Each exercise must include:
1. **Clear Title & Description**
2. **Learning Objectives** - What skills will be developed
3. **Difficulty Rating** - Visual star rating (⭐⭐⭐☆☆)
4. **Time Estimate** - Realistic completion time
5. **Prerequisites** - Required knowledge
6. **Problem Statement** - Clear, detailed problem description
7. **Input/Output Examples** - Multiple test cases
8. **Constraints** - Any limitations or requirements
9. **Hints Section** - Progressive hints (3-5 hints per exercise)
10. **Complete Solution** - Full working solution with comments
11. **Explanation** - Detailed solution explanation
12. **Alternative Approaches** - Different ways to solve the problem
13. **Code Review** - Best practices and improvements
14. **Testing Strategy** - How to test the solution
15. **Extension Challenges** - Ways to make it more complex
16. **Real-world Applications** - Where this skill is used

CONTENT REQUIREMENTS:
- Write EVERYTHING in ENGLISH language
- Each exercise must be substantial and educational
- Provide working, tested code examples
- Include detailed explanations for every solution
- Add practical tips and best practices throughout
- Use realistic data and scenarios
- Include error handling and edge cases
- Provide multiple solution approaches where applicable
- Add performance considerations
- Include security aspects where relevant
- For libraries: Focus on practical, real-world usage patterns
- Create exercises that simulate actual work scenarios
- Include collaborative coding exercises
- Add exercises for different development environments

SPECIAL FOCUS AREAS:
{', '.join(exercise_types)}

The practice document should be so comprehensive that someone could master {config.topic} through these exercises alone, progressing from complete beginner to advanced practitioner.

MINIMUM REQUIREMENTS:
- {config.exercise_count}+ individual exercises
- 5+ complete mini-projects
- 10+ debugging challenges
- 10+ code review exercises
- Multiple difficulty levels with clear progression
- Real-world scenarios and applications
- Complete solutions with detailed explanations

TARGET: 10,000+ words for truly comprehensive practical learning.
"""
        
        return base_prompt + structure_guide
    
    def save_practice_document(self, content: str, topic: str, difficulty: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic.lower().replace(' ', '_')}_practice_{difficulty}_{timestamp}.md"
        filepath = self.practice_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return str(filepath)
        except Exception as e:
            self.console.print(f"[red]Error saving practice document: {str(e)}[/red]")
            return None
    
    def preview_practice_document(self, content: str):
        # Show only first 2000 characters for preview
        preview_content = content[:2000] + "\n\n... [Document continues with full exercises and solutions]"
        md = Markdown(preview_content)
        panel = Panel(md, title="🎯 Practice Document Preview", border_style="green")
        self.console.print(panel)
    
    def create_practice_document(self, topic: str, difficulty: str = "intermediate",
                                exercise_count: int = 20, include_solutions: bool = True,
                                focus_areas: Optional[List[str]] = None,
                                exercise_types: Optional[List[str]] = None,
                                preview: bool = False) -> Optional[str]:
        
        config = PracticeConfig(
            topic=topic,
            difficulty_level=difficulty,
            exercise_count=exercise_count,
            include_solutions=include_solutions,
            focus_areas=focus_areas,
            exercise_types=exercise_types
        )
        
        self.console.print(f"[yellow]🎯 Generating practice exercises for: {topic}[/yellow]")
        self.console.print(f"[dim]Difficulty: {difficulty} | Exercises: {exercise_count}[/dim]")
        
        content = self.generate_practice_exercises(config)
        
        if not content:
            return None
        
        if preview:
            self.preview_practice_document(content)
        
        filepath = self.save_practice_document(content, topic, difficulty)
        
        if filepath:
            self.console.print(f"[green]✅ Practice document saved to: {filepath}[/green]")
            return filepath
        
        return None
    
    def interactive_practice_creation(self):
        """Interactive mode for creating practice documents"""
        
        self.console.print(Panel.fit(
            "[bold green]🎯 INTERACTIVE PRACTICE GENERATOR[/bold green]\n"
            "[dim]Let's create comprehensive practice exercises![/dim]",
            border_style="green"
        ))
        
        topic = Prompt.ask("[bold]What topic would you like to practice?[/bold]")
        
        difficulty = Prompt.ask(
            "[bold]Difficulty level[/bold]",
            choices=['beginner', 'intermediate', 'advanced', 'mixed'],
            default='intermediate'
        )
        
        exercise_count = int(Prompt.ask(
            "[bold]Number of exercises[/bold]",
            default="20"
        ))
        
        include_solutions = Confirm.ask(
            "[bold]Include detailed solutions?[/bold]", 
            default=True
        )
        
        focus_areas_input = Prompt.ask(
            "[bold]Specific focus areas[/bold] (comma-separated, or press Enter for all)",
            default=""
        )
        
        focus_areas = None
        if focus_areas_input.strip():
            focus_areas = [area.strip() for area in focus_areas_input.split(',')]
        
        preview = Confirm.ask("[bold]Preview before saving?[/bold]", default=False)
        
        return self.create_practice_document(
            topic=topic,
            difficulty=difficulty,
            exercise_count=exercise_count,
            include_solutions=include_solutions,
            focus_areas=focus_areas,
            preview=preview
        )