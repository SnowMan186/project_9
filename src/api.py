import requests
from typing import Optional, List, Dict


class HhApiClient:
    """Клиент для работы с API hh.ru."""

    def __init__(self):
        self.base_url = "https://api.hh.ru/"

    def get_company(self, company_id: str) -> Optional[Dict]:
        """Получает данные о компании по её ID."""
        response = requests.get(f"{self.base_url}/employers/{company_id}")
        if response.ok:
            return response.json()
        return None

    def get_vacancies_by_company(self, company_id: str) -> List[Dict]:
        """Получает список вакансий для определенной компании."""
        vacancies = []
        page = 0
        per_page = 100
        while True:
            response = requests.get(
                f"{self.base_url}/vacancies",
                params={"employer_id": company_id, "per_page": per_page, "page": page},
            )
            if response.ok:
                data = response.json()
                vacancies.extend(data["items"])
                if len(data["items"]) < per_page:
                    break
                page += 1
            else:
                break
        return vacancies
