from src.api import HhApiClient
from src.db_manager import DBManager
from dotenv import load_dotenv
import os
import argparse
import logging

# Настраиваем логгер
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения из .env
load_dotenv()


def main():
    """Главная функция проекта."""
    parser = argparse.ArgumentParser(
        description="Сбор данных о вакансиях с hh.ru и хранение в PostgreSQL."
    )
    parser.add_argument(
        "--action",
        choices=["load", "show", "clean"],
        help="Действие: load - загрузить данные, show - "
        "показать статистику, clean - очистить базу данных.",
    )
    args = parser.parse_args()

    # Читаем параметры из переменных окружения
    db_name = os.getenv("DB_NAME")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")

    # Создаем экземпляр менеджера базы данных
    db_manager = DBManager(db_name, db_host, db_port, db_user, db_pass)

    # Создаем клиент API hh.ru
    api_client = HhApiClient()

    # Действия в зависимости от выбранного параметра
    if args.action == "load":
        logger.info("Начинаем загрузку данных...")
        load_data(api_client, db_manager)
    elif args.action == "show":
        logger.info("Получаем статистику...")
        show_statistics(db_manager)
    elif args.action == "clean":
        logger.info("Очищаем базу данных...")
        clear_database(db_manager)
    else:
        logger.error("Не выбрано действие. Используйте аргумент '--help' для справки.")


def load_data(api_client: HhApiClient, db_manager: DBManager):
    """Загружает данные о компаниях и вакансиях в базу данных."""
    # Список реальных ID компаний с hh.ru
    company_ids = ["1740", "78638", "3529"]  # Добавьте сюда реальные ID компаний

    # Начинаем создавать базу данных и таблицы
    db_manager.create_database()
    db_manager.create_tables()

    # Загружаем данные
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
    """Показывает статистику по данным в базе данных."""
    statistics = db_manager.get_statistics()
    print(f"Количество компаний: {statistics['num_companies']}")
    print(f"Количество вакансий: {statistics['num_vacancies']}")


def clear_database(db_manager: DBManager):
    """Очищает базу данных."""
    db_manager.clear_database()
    logger.info("База данных очищена.")


if __name__ == "__main__":
    main()
