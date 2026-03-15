
import unittest
import requests
import BeautifulSoup

class APITestCase(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000"


    USERS_PATH = "/main"
    ADMIN_PATH = "/main"
    LOGIN_PATH = "/main"
    REGIST_PATH = "/main"

    TIMEOUT = 10

    @classmethod
    def setUpClass(cls):
        cls.s = requests.Session()
        try:
            r = cls.s.get(f"{cls.BASE_URL}/", timeout=3)
        except requests.RequestException as e:
            raise unittest.SkipTest(f"Сервер недоступен: {e}")

        if r.status_code >= 500:
            raise unittest.SkipTest(f"Сервер отвечает {r.status_code} на /")

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def _debug_response(self, r, title="Response"):
        content_type = r.headers.get("Content-Type", "")
        body = r.text

        if "application/json" in content_type:
            try:
                body = r.json()
            except Exception:
                body = r.text

        if isinstance(body, str) and len(body) > 2000:
            body = body[:2000] + " ...<truncated>..."

        return f"{title}: status={r.status_code}, content-type={content_type}, body={body}"

    def _url(self, path: str) -> str:
        return f"{self.BASE_URL}{path}"

    def _req(self, method: str, path: str, **kwargs):
        kwargs.setdefault("timeout", self.TIMEOUT)
        return self.s.request(method, self._url(path), **kwargs)

    def test_index_ok(self):
        r = self._req("GET", "/")
        self.assertEqual(r.status_code, 200,
                self._debug_response(r, "GET / - главная страница"))
        self.assertIn("text/html", r.headers.get("Content-Type", ""),
                     "Главная страница должна быть HTML")
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.find('title')
        self.assertIsNotNone(title, "На главной странице нет title")
        self.assertGreater(len(r.text), 50,
                          "Страница слишком короткая (меньше 50 символов)")

    def test_404_handler(self):
        r = self._req("GET", "/no-such-page")
        self.assertEqual(r.status_code, 404, self._debug_response(r, "GET /no-such-page"))

        data = r.json()
        self.assertEqual(data.get("err"), "Not found", self._debug_response(r, "GET /no-such-page (bad json)"))

    def test_get_users_list(self):
        r = self._req("GET", self.USERS_PATH)

        self.assertIn(
            r.status_code, (200, 404),
            "Ожидаем 200 или 404 (если эндпоинт не подключён).\n"
            + self._debug_response(r, f"GET {self.USERS_PATH}")
        )

        if r.status_code == 200:
            data = r.json()
            self.assertIsInstance(data, list, self._debug_response(r, "Users list is not list"))
        
    def test_get_users_list(self):
        r = self._req("GET", self.ADMIN_PATH)


        self.assertIn(
            r.status_code, (200, 404),
            "Ожидаем 200 или 404 (если эндпоинт не подключён).\n"
            + self._debug_response(r, f"GET {self.ADMIN_PATH}")
        )

        if r.status_code == 200:
            data = r.json()
            self.assertIsInstance(data, list, self._debug_response(r, "Users list is not list"))

    def test_login_wrong_credentials(self):
        payload = {"email": "nope@example.com", "password": "wrong"}
        r = self._req("POST", self.REGIST_PATH, json=payload)

        self.assertEqual(r.status_code, 401, self._debug_response(r, f"POST {self.REGIST_PATH} wrong"))
        self.assertIn("err", r.json(), self._debug_response(r, "POST login wrong (no err)"))

    def test_login_success_if_seeded(self):
        payload = {"role": "admin", "password": "1234"}
        r = self._req("POST", self.LOGIN_PATH, json=payload)

        self.assertIn(r.status_code, (200, 401), self._debug_response(r, f"POST {self.LOGIN_PATH} seeded"))

        if r.status_code == 200:
            data = r.json()
            self.assertIn("access_token", data, self._debug_response(r, "POST login seeded (no token)"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
