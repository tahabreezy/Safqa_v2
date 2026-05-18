import scrapy


class TenderItem(scrapy.Item):
    reference_number = scrapy.Field()
    title = scrapy.Field()
    authority = scrapy.Field()
    city = scrapy.Field()
    domain_code = scrapy.Field()
    domain_label = scrapy.Field()
    procedure_type = scrapy.Field()
    budget_raw = scrapy.Field()
    budget_mad = scrapy.Field()
    published_at = scrapy.Field()
    deadline_at = scrapy.Field()
    source_url = scrapy.Field()
