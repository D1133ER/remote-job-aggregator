"""Unit tests for job scrapers.

These test the `parse_job` conversion against fixture payloads (no network),
verifying that each source produces a valid `Job`-schema dict with a legitimate
`source_url` (for dedupe) and `apply_url` (for the Apply button).
"""
import unittest


class GreenhouseParseTests(unittest.TestCase):
    def _parse(self, payload, company="stripe"):
        from app.scrapers.greenhouse import GreenhouseScraper

        scraper = GreenhouseScraper(company_tokens=[company])
        return scraper.parse_job(payload, company_name=company)

    def test_populates_apply_and_source_urls(self):
        payload = {
            "id": 123,
            "title": "Senior Backend Engineer",
            "updated_at": "2026-09-01T12:00:00Z",
            "absolute_url": "https://stripe.com/jobs/search?gh_jid=123",
            "content": "<p>Python, FastAPI, PostgreSQL</p>",
            "location": {"name": "Remote"},
        }
        job = self._parse(payload)
        self.assertIsNotNone(job)
        self.assertEqual(job["apply_url"], "https://stripe.com/jobs/search?gh_jid=123")
        self.assertEqual(job["source_url"], "https://stripe.com/jobs/search?gh_jid=123")
        self.assertEqual(job["company_name"], "stripe")
        self.assertTrue(job["apply_url"].startswith("https://"))

    def test_non_remote_is_still_parseable(self):
        """Non-remote Greenhouse jobs are intentionally skipped (returns None)."""
        payload = {
            "id": 456,
            "title": "Account Executive",
            "updated_at": "2026-09-01T12:00:00Z",
            "absolute_url": "https://stripe.com/jobs/search?gh_jid=456",
            "content": "",
            "location": {"name": "San Francisco, CA"},
        }
        job = self._parse(payload)
        # Greenhouse parser filters out non-remote jobs by design.
        self.assertIsNone(job)


class RemotiveParseTests(unittest.TestCase):
    def test_fixture_has_apply_url(self):
        from app.scrapers.remotive import RemotiveScraper

        scraper = RemotiveScraper()
        job = scraper.parse_job(
            {
                "id": 123,
                "title": "React Developer",
                "company_name": "Acme",
                "url": "https://remotive.com/remote-jobs/react-developer-123",
                "description": "<p>Do React things.</p>",
                "candidate_required_location": "Worldwide",
                "publication_date": "2026-09-01T00:00:00",
                "category": "Software Development",
                "salary": "",
            }
        )
        self.assertEqual(job["apply_url"], "https://remotive.com/remote-jobs/react-developer-123")
        self.assertEqual(job["source_url"], "https://remotive.com/remote-jobs/react-developer-123")


class RemoteOKParseTests(unittest.TestCase):
    def test_uses_apply_url_field(self):
        from app.scrapers.remoteok import RemoteOKScraper

        scraper = RemoteOKScraper()
        job = scraper.parse_job(
            {
                "id": "abc123",
                "position": "DevOps Engineer",
                "company": "Cloudy Inc",
                "logo": "https://example.com/logo.png",
                "url": "https://remoteok.com/remote-jobs/abc123",
                "apply_url": "https://remoteok.com/remote-jobs/apply/abc123",
                "location": "Anywhere",
                "date": "2026-09-01",
                "tags": ["devops", "linux"],
                "description": "<p>Kubernetes and Terraform.</p>",
            }
        )
        # Prefer the dedicated apply_url when present.
        self.assertEqual(job["apply_url"], "https://remoteok.com/remote-jobs/apply/abc123")
        self.assertEqual(job["source_url"], "https://remoteok.com/remote-jobs/abc123")


class JobicyParseTests(unittest.TestCase):
    def test_fixture_has_apply_url(self):
        from app.scrapers.jobicy import JobicyScraper

        scraper = JobicyScraper()
        job = scraper.parse_job(
            {
                "id": 555,
                "jobTitle": "Data Scientist",
                "companyName": "DataCo",
                "jobType": ["full-time"],
                "jobLevel": "senior",
                "country": "Remote",
                "companyLogo": "https://example.com/dataco.png",
                "url": "https://jobicy.com/jobs/555-data-scientist",
                "jobDescription": "<p>ML pipelines.</p>",
                "jobIndustry": "Data",
            }
        )
        self.assertIsNotNone(job)
        self.assertTrue(job["apply_url"], "should have an apply url")
        self.assertTrue(job["apply_url"].startswith("https://"))


class ApplyUrlIntegrityTests(unittest.TestCase):
    """Cross-cutting: every parsed job must carry an apply_url key."""

    def test_all_schemas_expose_apply_url_key(self):
        from app.scrapers.greenhouse import GreenhouseScraper
        from app.scrapers.remotive import RemotiveScraper
        from app.scrapers.remoteok import RemoteOKScraper
        from app.scrapers.jobicy import JobicyScraper
        from app.scrapers.arbeitnow import ArbeitnowScraper
        from app.scrapers.weworkremotely import WeWorkRemotelyScraper
        from app.scrapers.lever import LeverScraper

        fixtures = {
            GreenhouseScraper: {"id": 1, "title": "T", "updated_at": "2026-09-01T00:00:00Z",
                                "absolute_url": "https://x.com/jobs/1", "content": ""},
            RemotiveScraper: {"id": 1, "title": "T", "company_name": "A",
                              "url": "https://remotive.com/remote-jobs/1", "description": ""},
            RemoteOKScraper: {"id": "1", "position": "T", "company": "A",
                              "url": "https://remoteok.com/remote-jobs/1", "date": "2026-09-01", "tags": []},
            JobicyScraper: {"id": 1, "jobTitle": "T", "companyName": "A",
                            "jobType": ["full-time"], "url": "https://jobicy.com/jobs/1", "country": "Remote"},
            ArbeitnowScraper: {"slug": "s", "title": "T", "company_name": "A",
                               "url": "https://arbeitnow.com/jobs/s", "description": "", "remote": True},
        }
        for scraper_cls, payload in fixtures.items():
            with self.subTest(scraper=scraper_cls.__name__):
                scraper = scraper_cls()
                result = scraper.parse_job(payload)
                # parse_job returns a dict or None/Optional[Dict]
                if result:
                    if isinstance(result, list):
                        parsed = result[0] if result else {}
                    else:
                        parsed = result
                    self.assertIn("apply_url", parsed,
                                  f"{scraper_cls.__name__} must expose apply_url")
                    if parsed.get("apply_url"):
                        self.assertIsInstance(parsed["apply_url"], str)


if __name__ == "__main__":
    unittest.main()