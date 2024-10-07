import requests
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import time
from data_management_module import DataManager

class APIIntegration:
    def __init__(self, app_id: str, api_key: str, db_name: str = 'job_search.db', base_url: str = "http://api.adzuna.com/v1/api/jobs"):
        self.app_id = app_id
        self.api_key = api_key
        self.base_url = base_url
        self.data_manager = DataManager(db_name)
        self.logger = logging.getLogger(__name__)

    def fetch_jobs(self, what: str, where: str, days_old: int = 30, page: int = 1, results_per_page: int = 50) -> Optional[List[Dict]]:
        url = f"{self.base_url}/gb/search/{page}"
        params = {
            "app_id": self.app_id,
            "app_key": self.api_key,
            "results_per_page": results_per_page,
            "what": what,
            "where": where,
            "content-type": "application/json",
            "days_old": days_old
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except requests.RequestException as e:
            self.logger.error(f"Error fetching jobs: {e}")
            return None

    def process_job(self, job: Dict) -> Dict:
        return {
            "job_id": job.get("id"),
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "description": job.get("description"),
            "salary": f"{job.get('salary_min')} - {job.get('salary_max')}",
            "url": job.get("redirect_url"),
            "date_posted": job.get("created")
        }

    def fetch_and_store_jobs(self, what: str, where: str, days_old: int = 30, max_jobs: int = 1000) -> int:
        page = 1
        total_stored = 0
        jobs_per_page = min(max_jobs, 50)  # Adzuna API limit is 50 per page

        while total_stored < max_jobs:
            jobs = self.fetch_jobs(what, where, days_old, page, jobs_per_page)
            if not jobs:
                break

            for job in jobs:
                processed_job = self.process_job(job)
                result = self.data_manager.add_job(processed_job)
                if result:
                    total_stored += 1
                    self.logger.info(f"Stored job: {processed_job['title']}")
                else:
                    self.logger.info(f"Failed to store job: {processed_job['title']}")

                if total_stored >= max_jobs:
                    break

            page += 1
            time.sleep(1)  # Respect API rate limits

        return total_stored

    def schedule_job_updates(self, what: str, where: str, interval_hours: int = 24):
        while True:
            self.logger.info(f"Fetching job updates for '{what}' in '{where}'")
            jobs_stored = self.fetch_and_store_jobs(what, where)
            self.logger.info(f"Stored {jobs_stored} jobs")
            
            next_update = datetime.now() + timedelta(hours=interval_hours)
            self.logger.info(f"Next update scheduled for {next_update}")
            
            time.sleep(interval_hours * 3600)

    def close(self):
        self.data_manager.close()
