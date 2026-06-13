import json
import operator
from typing import Any, Dict

class RuleEngine:
    """موتور ارزیابی قوانین بر اساس ساختار JSON (قابل تعریف از پنل)."""
    
    OPERATORS = {
        "eq": operator.eq,
        "neq": operator.ne,
        "gt": operator.gt,
        "lt": operator.lt,
        "gte": operator.ge,
        "lte": operator.le,
        "contains": lambda a, b: b in a,
        "in": lambda a, b: a in b,
        "and": all,
        "or": any,
    }

    async def evaluate(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        if not rule:
            return True
        rule_type = rule.get("type")
        if rule_type == "group":
            op = rule.get("operator", "and")
            conditions = rule.get("conditions", [])
            results = [await self.evaluate(cond, context) for cond in conditions]
            if op == "and":
                return all(results)
            elif op == "or":
                return any(results)
        elif rule_type == "condition":
            field = rule.get("field")
            op = rule.get("operator")
            value = rule.get("value")
            # دریافت مقدار واقعی از context (پشتیبانی از مسیرهای تو در تو)
            actual = self._get_field_value(context, field)
            op_func = self.OPERATORS.get(op)
            if op_func:
                return op_func(actual, value)
            return False
        return True

    def _get_field_value(self, context: Dict, field_path: str) -> Any:
        keys = field_path.split(".")
        val = context
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return None
        return val

rule_engine = RuleEngine()
