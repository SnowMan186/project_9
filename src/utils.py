from typing import Dict, Optional


def normalize_salary(salary_dict: Dict) -> Optional[int]:
    """Нормализует значение зарплаты из API."""
    if salary_dict is None:
        return None
    return salary_dict.get("from") or salary_dict.get("to")
