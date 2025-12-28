from src.api import HhApiClient
from src.db_manager import DBManager
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


def main():
    """Главная функция проекта."""
    logger.info("Начало работы...")

    # Загружаем настройки из .env
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")

    # Создаем экземпляр менеджеров
    db_manager = DBManager(db_name, db_host, db_port, db_user, db_pass)
    api_client = HhApiClient()

    # Меню взаимодействия с пользователем
    while True:
        print("\nВыберите действие:")
        print("1. Загрузить данные о компаниях и вакансиях")
        print("2. Показать статистику по данным")
        print("3. Очистить базу данных")
        print("4. Выйти из программы")
        choice = input("Ваш выбор: ").strip().lower()

        if choice == "1":
            load_data(api_client, db_manager)
        elif choice == "2":
            show_statistics(db_manager)
        elif choice == "3":
            clear_database(db_manager)
        elif choice == "4":
            logger.info("Программа завершена.")
            break
        else:
            print("Неверный выбор. Выберите пункт из меню.")


def load_data(api_client: HhApiClient, db_manager: DBManager):
    """Загружает данные о компаниях и вакансиях."""
    logger.info("Начинаем загрузку данных...")

    # Пример реальных ID компаний с hh.ru
    company_ids = ["1740", "78638", "3529"]

    for company_id in company_ids:
        company_data = api_client.get_company(company_id)
        if company_data:
            company_id_in_db = db_manager.insert_company(company_data)
            vacancies = api_client.get_vacancies_by_company(company_id)
            for vacancy in vacancies:
                db_manager.insert_vacancy(vacancy, company_id_in_db)
        else:
            logger.warning(
                f"Не удалось получить данные о компании {company_id}. Пропускаем."
            )

    logger.info("Данные успешно загружены.")


def show_statistics(db_manager: DBManager):
    """Показывает статистику по данным в базе."""
    stats = db_manager.get_statistics()
    print("\nСтатистика по данным:")
    print(f"- Количество компаний: {stats['num_companies']}")
    print(f"- Количество вакансий: {stats['num_vacancies']}\n")


def clear_database(db_manager: DBManager):
    """Очищает всю информацию из базы данных."""
    confirm = input("Вы точно хотите очистить базу данных? (yes/no): ").strip().lower()
    if confirm == "yes":
        db_manager.clear_database()
        print("База данных очищена.")
    else:
        print("Операция отменена.")


if __name__ == "__main__":
    main()
