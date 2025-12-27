import unittest
from src.db_manager import DBManager


class TestDBManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Подготовка среды тестирования"""
        cls.db_manager = DBManager()
        cls.db_manager.create_tables()

    def test_create_tables(self):
        """Проверяем создание таблиц"""
        with self.db_manager.conn.cursor() as cur:
            cur.execute("SELECT to_regclass('public.companies');")
            self.assertEqual(cur.fetchone()[0], 'companies')
            cur.execute("SELECT to_regclass('public.vacancies');")
            self.assertEqual(cur.fetchone()[0], 'vacancies')

    def test_insert_company(self):
        """Проверяем вставку компании"""
        inserted_id = self.db_manager.insert_company({
            'name': 'Test Company',
            'description': 'A test company'
        })
        self.assertIsInstance(inserted_id, int)

    def test_insert_vacancy(self):
        """Проверяем вставку вакансии"""
        company_id = self.db_manager.insert_company({
            'name': 'Test Company',
            'description': 'A test company'
        })
        inserted_id = self.db_manager.insert_vacancy({
            'title': 'Software Engineer',
            'salary': 100000,
            'link': 'http://example.com/vacancy'
        }, company_id)
        self.assertTrue(isinstance(inserted_id, int))

    def test_get_companies_and_vacancies_count(self):
        """Проверяем получение списка компаний и количества вакансий"""
        result = self.db_manager.get_companies_and_vacancies_count()
        self.assertGreater(len(result), 0)

    def test_get_all_vacancies(self):
        """Проверяем получение всех вакансий"""
        result = self.db_manager.get_all_vacancies()
        self.assertGreater(len(result), 0)

    def test_get_avg_salary(self):
        """Проверяем вычисление средней зарплаты"""
        avg_salary = self.db_manager.get_avg_salary()
        self.assertIsInstance(avg_salary, float)

    def test_get_vacancies_with_higher_salary(self):
        """Проверяем выбор вакансий с зарплатой выше средней"""
        result = self.db_manager.get_vacancies_with_higher_salary()
        self.assertGreater(len(result), 0)

    def test_get_vacancies_with_keyword(self):
        """Проверяем поиск вакансий по ключевым словам"""
        result = self.db_manager.get_vacancies_with_keyword('Engineer')
        self.assertGreater(len(result), 0)


if __name__ == '__main__':
    unittest.main()
