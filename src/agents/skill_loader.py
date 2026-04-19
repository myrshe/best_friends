import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any


class SkillLoader:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self._cache: Dict[str, Dict] = {}

    def discover_skills(self) -> List[Dict]:
        skills = []
        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir():
                skill_file = skill_path / "SKILL.md"
                if skill_file.exists():
                    metadata = self._parse_frontmatter(skill_file)
                    skills.append({
                        "name": metadata.get("name"),
                        "description": metadata.get("description"),
                        "triggers": metadata.get("triggers", []),
                        "path": str(skill_path)
                    })
        return skills

    def _parse_frontmatter(self, file_path: Path) -> Dict:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                yaml_block = content[3:end].strip()
                return yaml.safe_load(yaml_block) or {}
        return {}

    def load_skill(self, skill_name: str) -> Dict[str, Any]:
        if skill_name in self._cache:
            return self._cache[skill_name]

        skill_path = self.skills_dir / skill_name
        skill_file = skill_path / "SKILL.md"

        if not skill_file.exists():
            for item in self.skills_dir.iterdir():
                if item.is_dir():
                    candidate_file = item / "SKILL.md"
                    if candidate_file.exists():
                        metadata = self._parse_frontmatter(candidate_file)
                        if metadata.get("name") == skill_name:
                            skill_path = item
                            skill_file = candidate_file
                            break
            else:
                available = [d.name for d in self.skills_dir.iterdir() if d.is_dir()]
                raise ValueError(f"Skill '{skill_name}' not found. Available: {available}")

        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()

        metadata = self._parse_frontmatter(skill_file)

        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                body = content[end + 3:].strip()
            else:
                body = content
        else:
            body = content

        skill = {
            "metadata": metadata,
            "instruction": body,
            "scripts": {},
            "path": str(skill_path)
        }

        self._cache[skill_name] = skill
        return skill

    def load_script(self, skill_name: str, script_name: str) -> str:
        skill = self.load_skill(skill_name)
        script_path = Path(skill["path"]) / "scripts" / script_name

        if not script_path.exists():
            raise ValueError(f"Script not found: {script_name} in {skill_name}")

        with open(script_path, "r", encoding="utf-8") as f:
            return f.read()

    def get_skill_for_trigger(self, trigger: str) -> Dict:
        for skill_meta in self.discover_skills():
            if trigger.lower() in [t.lower() for t in skill_meta.get("triggers", [])]:
                return self.load_skill(skill_meta["name"])
        return None