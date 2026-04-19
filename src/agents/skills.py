# src/agents/skills.py
from src.agents.skill_loader import SkillLoader

skill_loader = SkillLoader()


def execute_skill(skill_name: str, inputs: dict, config: dict) -> dict:
    skill = skill_loader.load_skill(skill_name)

    if skill_name == "search_knowledge_base":
        script_code = skill_loader.load_script(skill_name, "qdrant_search.py")
        namespace = {"config": config, **inputs}
        exec(script_code, namespace)
        results = namespace["search"](**inputs, config=config)
        return {"chunks": results, "count": len(results)}

    elif skill_name == "classify_query":
        prompt_template = skill_loader.load_script(skill_name, "router_prompt.md")
        return {"prompt": prompt_template.format(query=inputs.get("query", ""))}

    elif skill_name == "evaluate_context":
        script_code = skill_loader.load_script(skill_name, "quality_check.py")
        namespace = {"config": config, **inputs}
        exec(script_code, namespace)
        result = namespace["evaluate"](inputs["chunks"], inputs.get("query", ""))
        return result

    else:
        raise ValueError(f"Unknown skill: {skill_name}")