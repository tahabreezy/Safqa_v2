import scrapy
from scrapy.http import HtmlResponse

from safqa_scraper.items import TenderItem
from safqa_scraper.utils import parse_budget


class TendersSpider(scrapy.Spider):
    name = "tenders"
    allowed_domains = ["marchespublics.gov.ma"]
    BASE = "https://www.marchespublics.gov.ma"

    def start_requests(self):
        yield scrapy.Request(
            url=f"{self.BASE}/pmmp/",
            callback=self.parse_homepage,
        )

    def parse_homepage(self, response):
        for table in response.css("table.data"):
            for row in table.css("tr"):
                link = row.css("a[href*='domaineActivite']")
                if not link:
                    continue
                href = link.attrib["href"]
                domain_code = href.split("domaineActivite=")[-1].split("&")[0]
                domain_label = link.css("::text").get("").strip()
                search_url = (
                    f"{self.BASE}/index.php"
                    f"?page=entreprise.EntrepriseAdvancedSearch"
                    f"&AllCons&EnCours"
                    f"&domaineActivite={domain_code}"
                )
                yield scrapy.Request(
                    url=search_url,
                    callback=self.parse_search_results,
                    meta={
                        "domain_code": domain_code,
                        "domain_label": domain_label,
                        "playwright": True,
                        "playwright_include_page": True,
                    },
                )

    async def parse_search_results(self, response):
        page = response.meta["playwright_page"]
        domain_code = response.meta["domain_code"]
        domain_label = response.meta["domain_label"]

        await page.wait_for_load_state("networkidle")

        await self._submit_prado_search(page)

        await page.wait_for_timeout(2000)
        html = await page.content()
        current_url = page.url

        resp = HtmlResponse(
            url=current_url, body=html, encoding="utf-8", request=response.request
        )

        tender_links = resp.css("a[href*='Consultation'][href*='idConsultation']")
        if not tender_links:
            tender_links = resp.css("a[href*='consultation'][href*='id=']")
        if not tender_links:
            tender_links = resp.css("table.data a, table.items a, .results a")

        for link in tender_links:
            href = link.attrib["href"]
            if href.startswith("?"):
                href = f"{self.BASE}/index.php{href}"
            elif href.startswith("/"):
                href = f"{self.BASE}{href}"

            ref_text = link.css("::text").get("").strip()

            yield scrapy.Request(
                url=href,
                callback=self.parse_tender_detail,
                meta={
                    "domain_code": domain_code,
                    "domain_label": domain_label,
                    "reference_number_hint": ref_text,
                    "playwright": True,
                    "playwright_include_page": True,
                },
            )

        next_page = resp.css("a[href*='pageNo']:has-text('Suivant'), a[href*='pageNo']:has-text('>')")
        if next_page:
            next_href = next_page.attrib["href"]
            if next_href.startswith("?"):
                next_href = f"{self.BASE}/index.php{next_href}"
            yield scrapy.Request(
                url=next_href,
                callback=self.parse_search_results,
                meta={
                    "domain_code": domain_code,
                    "domain_label": domain_label,
                    "playwright": True,
                    "playwright_include_page": True,
                },
            )

        await page.close()

    async def _submit_prado_search(self, page):
        selectors = [
            "input.ok",
            "input[type='image']",
            "button:has-text('Rechercher')",
            "input[value='Rechercher']",
            "input[title*='chercher']",
            "#ctl0_CONTENU_PAGE_AdvancedSearch_buttonRefresh",
            "form input[type='submit']",
        ]
        for sel in selectors:
            btn = await page.query_selector(sel)
            if btn:
                try:
                    await btn.click()
                    await page.wait_for_load_state("networkidle")
                    return True
                except Exception:
                    continue
        return False

    async def parse_tender_detail(self, response):
        page = response.meta["playwright_page"]
        domain_code = response.meta["domain_code"]
        domain_label = response.meta["domain_label"]

        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)
        html = await page.content()
        current_url = page.url

        resp = HtmlResponse(
            url=current_url, body=html, encoding="utf-8", request=response.request
        )

        item = TenderItem()
        item["domain_code"] = domain_code
        item["domain_label"] = domain_label
        item["source_url"] = current_url

        body_text = resp.css("body *::text").getall()
        full_text = " ".join(t.strip() for t in body_text if t.strip())

        item["reference_number"] = self._extract_field(
            resp, full_text,
            ["Référence", "reference", "N° consultation", "Numéro"],
        )
        item["title"] = self._extract_field(
            resp, full_text,
            ["Objet", "Intitulé", "Titre", "objet"],
        )
        item["authority"] = self._extract_field(
            resp, full_text,
            ["Acheteur", "Autorité", "Maître d'ouvrage", "Personne publique"],
        )
        item["city"] = self._extract_field(
            resp, full_text,
            ["Ville", "Lieu d'exécution", "Localisation"],
        )
        item["procedure_type"] = self._extract_field(
            resp, full_text,
            ["Procédure", "Type", "Mode de passation"],
        )

        budget_raw = self._extract_field(
            resp, full_text,
            ["Budget", "Estimation", "Montant", "Coût"],
        )
        item["budget_raw"] = budget_raw
        item["budget_mad"] = parse_budget(budget_raw)

        published_raw = self._extract_field(
            resp, full_text,
            ["Date de publication", "Publié le", "Publication"],
        )
        deadline_raw = self._extract_field(
            resp, full_text,
            ["Date limite", "Date de remise", "Clôture", "Échéance"],
        )
        item["published_at"] = self._parse_date(published_raw)
        item["deadline_at"] = self._parse_date(deadline_raw)

        if not item.get("reference_number") or not item.get("title"):
            self.logger.warning(
                "Skipping incomplete tender at %s: ref=%s title=%s",
                current_url, item.get("reference_number"), item.get("title"),
            )
            await page.close()
            return

        yield item

        await page.close()

    def _extract_field(self, resp, full_text, labels):
        for label in labels:
            for sel in [
                f"th:has-text('{label}') + td",
                f"td:has-text('{label}') + td",
                f"th:has-text('{label}') ~ td",
                f"td:has-text('{label}') ~ td",
                f"tr:has(td:has-text('{label}')) td:last-child",
                f"tr:has(th:has-text('{label}')) td:last-child",
                f"div.field:has(label:has-text('{label}')) div.value",
                f"div:has(span:has-text('{label}')) span.value",
                f"label:has-text('{label}') + input",
                f"label:has-text('{label}') ~ input",
            ]:
                val = resp.css(f"{sel}::text").get()
                if val:
                    val = val.strip()
                    if val:
                        return val

            import re
            pattern = re.compile(
                re.escape(label) + r"\s*[:\-]?\s*(.+?)(?:\n|$)",
                re.IGNORECASE,
            )
            lines = full_text.split("\n")
            for line in lines:
                m = pattern.search(line.strip())
                if m:
                    val = m.group(1).strip()
                    if val:
                        return val

        return None

    def _parse_date(self, raw):
        if not raw:
            return None
        import re
        raw = raw.strip()
        for fmt in [
            "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d",
            "%d %B %Y", "%d %b %Y",
        ]:
            try:
                from datetime import datetime
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        m = re.search(r"(\d{2})[/\-](\d{2})[/\-](\d{4})", raw)
        if m:
            from datetime import date
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        return None
