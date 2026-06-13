import pytest
from src.core.rule_engine import RuleEngine

@pytest.mark.asyncio
async def test_rule_engine_eq():
    engine = RuleEngine()
    rule = {"type": "condition", "field": "user.level", "operator": "eq", "value": "vip"}
    context = {"user": {"level": "vip"}}
    result = await engine.evaluate(rule, context)
    assert result is True

@pytest.mark.asyncio
async def test_rule_engine_group_and():
    engine = RuleEngine()
    rule = {
        "type": "group",
        "operator": "and",
        "conditions": [
            {"type": "condition", "field": "age", "operator": "gte", "value": 18},
            {"type": "condition", "field": "age", "operator": "lt", "value": 65}
        ]
    }
    context = {"age": 30}
    assert await engine.evaluate(rule, context) is True
