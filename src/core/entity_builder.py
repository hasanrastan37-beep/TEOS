# اضافه می‌شود به فایل قبلی
import re
from typing import Any

class EntityValidator:
    @staticmethod
    def validate(data: dict, schema: List[dict]) -> dict:
        errors = {}
        for field_def in schema:
            name = field_def.get("name")
            field_type = field_def.get("type", "string")
            required = field_def.get("required", False)
            min_length = field_def.get("min_length")
            max_length = field_def.get("max_length")
            pattern = field_def.get("pattern")
            value = data.get(name)

            if required and (value is None or value == ""):
                errors[name] = "این فیلد الزامی است."
                continue

            if value is not None and value != "":
                if field_type == "integer":
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        errors[name] = "باید عدد صحیح باشد."
                elif field_type == "email":
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", str(value)):
                        errors[name] = "ایمیل نامعتبر است."
                # سایر تایپ‌ها...

        return errors
