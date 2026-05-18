BOT_NAME = "safqa_scraper"

SPIDER_MODULES = ["safqa_scraper.spiders"]
NEWSPIDER_MODULE = "safqa_scraper.spiders"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Safqa/1.0"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_BACKOFF_MIN = 5.0
RETRY_BACKOFF_MAX = 120.0
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
}

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}

ITEM_PIPELINES = {
    "safqa_scraper.pipelines.postgres_pipeline.PostgresPipeline": 300,
    "safqa_scraper.pipelines.meili_pipeline.MeilisearchPipeline": 400,
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
