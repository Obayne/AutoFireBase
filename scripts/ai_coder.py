#!/usr/bin/env python3
"""
AI Coder - Autonomous code implementation using local AI
Uses DeepSeek Coder via Ollama to implement tasks automatically
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import requests
import time


class AICoder:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.ollama_url = "http://localhost:11434"
        self.model = "deepseek-coder:latest"
        
    def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_code(self, prompt: str, temperature: float = 0.3) -> str:
        """Call Ollama to generate code"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 4096
            }
        }
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    
    def read_codebase_context(self) -> Dict[str, str]:
        """Read key files for context"""
        context = {}
        
        # Architecture docs
        arch_doc = self.repo_root / "docs" / "ARCHITECTURE.md"
        if arch_doc.exists():
            context["architecture"] = arch_doc.read_text(encoding="utf-8")
        
        # Agent guide
        agent_guide = self.repo_root / "AGENTS.md"
        if agent_guide.exists():
            context["agent_guide"] = agent_guide.read_text(encoding="utf-8")
        
        # Existing examples
        examples = {}
        for pattern in ["backend/*.py", "cad_core/*.py", "frontend/*.py"]:
            for file in self.repo_root.glob(pattern):
                if file.name != "__init__.py" and file.stat().st_size < 10000:
                    examples[str(file.relative_to(self.repo_root))] = file.read_text(encoding="utf-8")[:2000]
        
        context["examples"] = examples
        return context
    
    def create_implementation_plan(self, task_content: str, context: Dict) -> Dict:
        """Create implementation plan using AI"""
        
        prompt = f"""You are an expert Python developer working on LV CAD, a professional CAD application.

ARCHITECTURE:
{context.get('architecture', 'See AGENTS.md for guidelines')}

TASK TO IMPLEMENT:
{task_content}

CONSTRAINTS:
- Keep total changes under 300 lines
- Follow Black formatting (line-length=100)
- No Qt imports in backend/ or cad_core/
- Add pytest tests for all new functionality
- Use type hints (Python 3.11+)
- Follow existing patterns in codebase

Create a detailed implementation plan in JSON format:
{{
  "files_to_create": [
    {{
      "path": "path/to/new_file.py",
      "purpose": "Brief description",
      "dependencies": ["module1", "module2"]
    }}
  ],
  "files_to_modify": [
    {{
      "path": "path/to/existing.py",
      "changes": "What to change and why"
    }}
  ],
  "tests_to_add": [
    {{
      "path": "tests/path/test_feature.py",
      "test_cases": ["test_case_1", "test_case_2"]
    }}
  ],
  "implementation_order": [
    "Step 1: Create base classes",
    "Step 2: Implement core logic",
    "Step 3: Add tests",
    "Step 4: Update integration points"
  ]
}}

Respond with ONLY valid JSON, no markdown formatting."""

        print("🤖 Generating implementation plan...")
        response = self.generate_code(prompt, temperature=0.2)
        
        # Extract JSON from response (handle markdown code blocks)
        json_str = response.strip()
        if json_str.startswith("```"):
            lines = json_str.split("\n")
            json_str = "\n".join(lines[1:-1]) if len(lines) > 2 else json_str
            json_str = json_str.replace("```json", "").replace("```", "").strip()
        
        try:
            plan = json.loads(json_str)
            return plan
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse AI response as JSON: {e}")
            print(f"Response: {response[:500]}")
            return None
    
    def generate_file_content(self, file_path: str, purpose: str, context: Dict) -> str:
        """Generate content for a new file"""
        
        examples_text = "\n\n".join([
            f"Example from {path}:\n{content[:500]}"
            for path, content in list(context.get("examples", {}).items())[:3]
        ])
        
        prompt = f"""Generate Python code for: {file_path}

PURPOSE: {purpose}

STYLE GUIDELINES:
- Black formatting (line-length=100)
- Type hints required
- Docstrings for all public functions
- Python 3.11+

ARCHITECTURE:
{context.get('agent_guide', '')}

EXAMPLES FROM CODEBASE:
{examples_text}

Generate ONLY the Python code, no explanation or markdown:"""

        print(f"  📝 Generating: {file_path}")
        content = self.generate_code(prompt, temperature=0.4)
        
        # Clean up markdown if present
        if content.strip().startswith("```python"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            content = content.replace("```python", "").replace("```", "").strip()
        
        return content
    
    def generate_test_content(self, test_path: str, module_path: str, test_cases: List[str]) -> str:
        """Generate test file content"""
        
        prompt = f"""Generate pytest tests for: {module_path}

TEST FILE: {test_path}

TEST CASES TO IMPLEMENT:
{chr(10).join(f"- {tc}" for tc in test_cases)}

REQUIREMENTS:
- Use pytest framework
- Type hints required
- Test both success and error cases
- Use fixtures where appropriate
- Follow AAA pattern (Arrange, Act, Assert)

Generate ONLY the Python test code:"""

        print(f"  🧪 Generating tests: {test_path}")
        content = self.generate_code(prompt, temperature=0.4)
        
        # Clean up markdown
        if content.strip().startswith("```python"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content
            content = content.replace("```python", "").replace("```", "").strip()
        
        return content
    
    def implement_task(self, task_file: Path) -> bool:
        """Implement a task file fully autonomously"""
        
        print(f"\n{'='*80}")
        print(f"🚀 Implementing: {task_file.name}")
        print(f"{'='*80}\n")
        
        # Check Ollama
        if not self.check_ollama():
            print("❌ Ollama is not running. Start with: ollama serve")
            return False
        
        # Read task
        task_content = task_file.read_text(encoding="utf-8")
        
        # Get context
        print("📚 Reading codebase context...")
        context = self.read_codebase_context()
        
        # Create plan
        plan = self.create_implementation_plan(task_content, context)
        if not plan:
            print("❌ Failed to create implementation plan")
            return False
        
        print("\n📋 Implementation Plan:")
        print(json.dumps(plan, indent=2))
        
        # Execute plan
        print("\n🔨 Executing implementation...\n")
        
        # Create new files
        for file_spec in plan.get("files_to_create", []):
            file_path = self.repo_root / file_spec["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = self.generate_file_content(
                file_spec["path"],
                file_spec["purpose"],
                context
            )
            
            file_path.write_text(content, encoding="utf-8")
            print(f"  ✅ Created: {file_spec['path']}")
        
        # Generate tests
        for test_spec in plan.get("tests_to_add", []):
            test_path = self.repo_root / test_spec["path"]
            test_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Infer module path from test path
            module_path = test_spec["path"].replace("tests/", "").replace("test_", "").replace(".py", ".py")
            
            content = self.generate_test_content(
                test_spec["path"],
                module_path,
                test_spec.get("test_cases", [])
            )
            
            test_path.write_text(content, encoding="utf-8")
            print(f"  ✅ Created test: {test_spec['path']}")
        
        # Format code
        print("\n🎨 Formatting code...")
        subprocess.run(["black", ".", "--line-length", "100"], 
                      cwd=self.repo_root, capture_output=True)
        
        print("\n✅ Implementation complete!")
        return True


def main():
    repo_root = Path(__file__).parent.parent
    
    if len(sys.argv) < 2:
        print("Usage: ai_coder.py <task_file.md>")
        print("\nExample: python scripts/ai_coder.py tasks/task-db-connection-manager.md")
        return 1
    
    task_file = Path(sys.argv[1])
    if not task_file.exists():
        # Try relative to repo root
        task_file = repo_root / task_file
        if not task_file.exists():
            print(f"❌ Task file not found: {sys.argv[1]}")
            return 1
    
    coder = AICoder(repo_root)
    success = coder.implement_task(task_file)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
