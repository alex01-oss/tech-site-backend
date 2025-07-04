from locust import HttpUser, task, between
import random

class CatalogUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://127.0.0.1:8080"

    @task(2)
    def search_with_params(self):
        # Валідні search_type
        search_types = ["code", "shape", "dimensions", "machine"]
        search_values = {
            "code": random.choice(["3C3042", "3-3048", "W-0000"]),
            "shape": random.choice(["12V9-20", "14F1"]),
            "dimensions": random.choice(["100x10x2.3x4", "200x8x1.2x4x7x0.6"]),
            "machine": random.choice(["SW BA 80N", "PowerStar 850", ""])  # Порожній для продуктів без машин
        }
        search_type = random.choice(search_types)
        search_value = search_values[search_type]

        # Додаємо name_bond і grid_size як окремі параметри
        params = {
            "search": search_value,
            "search_type": search_type,
            "page": random.randint(1, 5),
            "items_per_page": 10,
            "name_bond": random.choice(["B9-00", "HSS02", ""]),  # Порожній для тестування без фільтра
            "grid_size": random.choice(["D64", "B107", ""])
        }
        self.client.get("/api/catalog", params=params, name=f"search_{search_type}")

    @task(1)
    def search_no_params(self):
        self.client.get("/api/catalog?page=1&items_per_page=10", name="search_no_params")

    @task(1)
    def pagination(self):
        page = random.randint(2, 10)
        self.client.get(f"/api/catalog?page={page}&items_per_page=10", name="pagination")

    @task(1)
    def get_item_by_code(self):
        codes = ["3C3042", "3-3048", "3-3045", "W-0000"]
        self.client.get(f"/api/catalog/{random.choice(codes)}", name="get_item_by_code")

    @task(1)
    def invalid_search(self):
        invalid_params = [
            {"search": "", "search_type": "code", "page": 0},
            {"search": "nonexistent", "search_type": "machine", "page": 1},
            {"search": "invalid", "search_type": "code", "page": -1}
        ]
        params = random.choice(invalid_params)
        self.client.get("/api/catalog", params=params, name="invalid_search")