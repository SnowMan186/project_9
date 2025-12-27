from dotenv import load_dotenv
import requests

load_dotenv()


class HhApiClient:
    def __init__(self):
        self.base_url = 'https://api.hh.ru/'

    def get_company(self, company_id):
        response = requests.get(f'{self.base_url}/employers/{company_id}')
        return response.json() if response.status_code == 200 else None

    def get_vacancies_by_company(self, company_id):
        vacancies = []
        page = 0
        while True:
            params = {'employer_id': company_id, 'page': page}
            response = requests.get(f'{self.base_url}/vacancies', params=params)
            data = response.json()
            vacancies.extend(data['items'])
            if len(data['items']) < 100 or not data['more']:
                break
            page += 1
        return vacancies
