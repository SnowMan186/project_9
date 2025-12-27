import os
from dotenv import load_dotenv
import psycopg2
from contextlib import closing

load_dotenv()


class DBManager:
    def __init__(self):
        """Инициализация менеджера базы данных."""
        self.conn_params = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }

    def create_tables(self):
        """Создание необходимых таблиц в базе данных."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS companies (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        description TEXT
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS vacancies (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255),
                        salary INT,
                        link VARCHAR(255),
                        company_id INT REFERENCES companies(id)
                    );
                """)

            conn.commit()

    def insert_company(self, company_data):
        """Вставка данных о компании в таблицу companies."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO companies (name, description) VALUES (%s, %s) RETURNING id;
                    """,
                    (company_data['name'], company_data['description'])
                )
                new_company_id = cur.fetchone()[0]
            conn.commit()
            return new_company_id

    def insert_vacancy(self, vacancy_data, company_id):
        """Вставка данных о вакансии в таблицу vacancies."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO vacancies (title, salary, link, company_id) VALUES (%s, %s, %s, %s);
                    """,
                    (vacancy_data['title'], vacancy_data['salary'], vacancy_data['link'], company_id)
                )
            conn.commit()

    def get_companies_and_vacancies_count(self):
        """Возвращает список всех компаний и количество вакансий у каждой компании."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT companies.name, COUNT(vacancies.id) AS vacancies_count
                    FROM companies LEFT JOIN vacancies ON companies.id = vacancies.company_id
                    GROUP BY companies.id;
                """)
                rows = cur.fetchall()
                return [(row[0], row[1]) for row in rows]

    def get_all_vacancies(self):
        """Возвращает список всех вакансий с названием компании,
         названием вакансии, зарплатой и ссылкой на вакансию."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT companies.name, vacancies.title, vacancies.salary, vacancies.link
                    FROM vacancies INNER JOIN companies ON vacancies.company_id = companies.id;
                """)
                rows = cur.fetchall()
                return [
                    {"Company": row[0],
                     "Vacancy Title": row[1],
                     "Salary": row[2],
                     "Link": row[3]} for row in rows
                ]

    def get_avg_salary(self):
        """Возвращает среднюю зарплату по всем вакансиям."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT AVG(salary)::INTEGER FROM vacancies;
                """)
                avg_salary = cur.fetchone()[0]
                return avg_salary

    def get_vacancies_with_higher_salary(self):
        """Возвращает список вакансий с зарплатой выше среднего уровня."""
        average_salary = self.get_avg_salary()
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT companies.name, vacancies.title, vacancies.salary, vacancies.link
                    FROM vacancies INNER JOIN companies ON vacancies.company_id = companies.id
                    WHERE vacancies.salary > %s;
                """, (average_salary,))
                rows = cur.fetchall()
                return [
                    {"Company": row[0],
                     "Vacancy Title": row[1],
                     "Salary": row[2],
                     "Link": row[3]} for row in rows
                ]

    def get_vacancies_with_keyword(self, keyword):
        """Возвращает список вакансий, содержащих указанное ключевое слово в названии."""
        with closing(psycopg2.connect(**self.conn_params)) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT companies.name, vacancies.title, vacancies.salary, vacancies.link
                    FROM vacancies INNER JOIN companies ON vacancies.company_id = companies.id
                    WHERE LOWER(vacancies.title) LIKE LOWER(%s);
                """, ('%' + keyword + '%',))
                rows = cur.fetchall()
                return [
                    {"Company": row[0],
                     "Vacancy Title": row[1],
                     "Salary": row[2],
                     "Link": row[3]} for row in rows
                ]
