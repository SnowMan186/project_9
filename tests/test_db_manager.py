import unittest
from src.db_manager import DBManager
from dotenv import load_dotenv
import os
import psycopg2
from contextlib import closing

load_dotenv()


class TestDBManager(unittest.TestCase):
    def setUp(self):
        """Инициализация тестового окружения."""
        # Загружаем настройки из .env
        db_name = os.getenv("TEST_DB_NAME")
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASSWORD")

        # Устанавливаем соединение с временной базой данных
        self.db_manager = DBManager(db_name, db_host, db_port, db_user, db_pass)
        self.db_manager.create_database()
        self.db_manager.create_tables()

    def tearDown(self):
        """Освобождаем ресурсы после теста."""
        self.db_manager.clear_database()

    def test_create_database(self):
        """Проверяет создание базы данных."""
        # Мы ожидаем, что база данных уже создана в setUp(), проверим это
        with closing(psycopg2.connect(**self.db_manager.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT datname FROM pg_database WHERE datistemplate = false;"
                )
                databases = [d[0] for d in cur.fetchall()]
                self.assertIn(self.db_manager.conn_params["dbname"], databases)

    def test_create_tables(self):
        """Проверяет создание таблиц."""
        with closing(psycopg2.connect(**self.db_manager.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
                )
                tables = [t[0] for t in cur.fetchall()]
                self.assertIn("companies", tables)
                self.assertIn("vacancies", tables)

    def test_insert_company(self):
        """Проверяет вставку компании в базу данных."""
        company_data = {
            "name": "Яндекс",
            "description": "Крупнейший поисковик в России",
        }
        company_id = self.db_manager.insert_company(company_data)
        self.assertIsInstance(company_id, int)

    def test_insert_vacancy(self):
        """Проверяет вставку вакансии в базу данных."""
        company_id = self.db_manager.insert_company(
            {"name": "Google", "description": "Компания Google"}
        )
        vacancy_data = {
            "name": "Backend-разработчик",
            "salary": {"from": 100000, "to": 150000},
            "alternate_url": "https://hh.ru/vacancy/12345",
        }
        self.db_manager.insert_vacancy(vacancy_data, company_id)

    def test_get_statistics(self):
        """Проверяет получение статистики по базе данных."""
        # Вставляем тестовые данные
        company_id = self.db_manager.insert_company(
            {"name": "Apple", "description": "Производитель iPhone"}
        )
        vacancy_data = {
            "name": "Frontend-разработчик",
            "salary": {"from": 120000, "to": 180000},
            "alternate_url": "https://hh.ru/vacancy/54321",
        }
        self.db_manager.insert_vacancy(vacancy_data, company_id)

        # Получаем статистику
        stats = self.db_manager.get_statistics()
        self.assertEqual(stats["num_companies"], 1)
        self.assertEqual(stats["num_vacancies"], 1)

    def test_clear_database(self):
        """Проверяет очистку базы данных."""
        # Предварительная очистка базы данных
        self.db_manager.clear_database()
        stats = self.db_manager.get_statistics()
        self.assertEqual(stats["num_companies"], 0)
        self.assertEqual(stats["num_vacancies"], 0)


if __name__ == "__main__":
    unittest.main()
