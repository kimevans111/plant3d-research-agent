from pathlib import Path

from skills.registry import SkillRegistry


ROOT = Path(__file__).resolve().parents[1]


def test_registry_loads_all_skills() -> None:
    registry = SkillRegistry(ROOT / "skills")

    skills = registry.list_skills()

    assert {skill.name for skill in skills} == {
        "training_log_analysis",
        "rag_research_qa",
        "rag_evaluation",
        "report_generation",
        "plant3d_domain_explanation",
    }


def test_skill_schemas_have_required_fields() -> None:
    registry = SkillRegistry(ROOT / "skills")

    for skill in registry.list_skills():
        assert skill.skill_md_path.exists()
        assert skill.schema_path.exists()
        registry.validate_skill_schema(skill.schema)
        assert skill.recommended_tools
        assert skill.description
