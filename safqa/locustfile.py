from locust import HttpUser, task, between


class SafqaUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def search(self):
        self.client.get("/v1/tenders/search?q=construction&domain=1.15")

    @task(2)
    def search_empty(self):
        self.client.get("/v1/tenders/search")

    @task(1)
    def get_stats(self):
        self.client.get("/v1/tenders/stats")

    @task(1)
    def get_domains(self):
        self.client.get("/v1/tenders/domains")
