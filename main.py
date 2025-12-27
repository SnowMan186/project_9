from src.api import HhApiClient
from src.db_manager import DBManager


def main():
    client = HhApiClient()
    manager = DBManager()
    manager.create_tables()

    for company_id in ['company_1', 'company_2', ..., 'company_10']:
        company_data = client.get_company(company_id)
        manager.insert_company(company_data)
        vacancies = client.get_vacancies_by_company(company_id)
        for vacancy in vacancies:
            manager.insert_vacancy(vacancy, company_data['id'])


if __name__ == '__main__':
    main()
