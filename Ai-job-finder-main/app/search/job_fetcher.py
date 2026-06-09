import requests
import time
from app.utils.logger import get_logger

logger = get_logger(__name__)

JOB_CACHE = {}

def fetch_jobicy_jobs(search_term: str, limit: int = 10):
    """
    Fetches jobs from Jobicy API.
    """
    # 1. Clean the tag (Jobicy needs "data-science", not "Data Science")
    if not search_term:
        return []
        
    clean_tag = search_term.lower().replace(" ", "-")
    
    url = f"https://jobicy.com/api/v2/remote-jobs?tag={clean_tag}&count={limit}"
    
    try:
        # Check Cache first
        if url in JOB_CACHE:
            return JOB_CACHE[url]

        logger.info(f"Querying Jobicy API for tag: '{clean_tag}'")
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Jobicy returned status {response.status_code}")
            return []

        data = response.json()
        jobs_list = data.get('jobs', [])
        formatted_jobs = []

        for job in jobs_list:
            formatted_jobs.append({
                "title": job.get("jobTitle"),
                "company": job.get("companyName"),
                "location": job.get("jobGeo", "Remote"),
                "url": job.get("url"),
                "description": job.get("jobDescription", "") + " " + job.get("jobTitle", ""),
                "source": "Jobicy"
            })
            
        JOB_CACHE[url] = formatted_jobs
        return formatted_jobs
    except Exception as e:
        logger.error(f"Jobicy API failed: {e}")
        return []

def fetch_jobs(query: str, source: str = "both", limit: int = 10):
    """
    Smart Fetcher with Fallback
    """
    all_jobs = []
    
    # 1. Try the specific skill from resume (e.g. "Python")
    logger.info(f"Attempting search for specific skill: {query}")
    jobs = fetch_jobicy_jobs(query, limit)
    
    if jobs:
        all_jobs.extend(jobs)
    else:
        # 2. SAFETY NET: If specific skill found 0 jobs, search for broad terms
        logger.warning(f"0 jobs found for '{query}'. Trying fallback 'dev'...")
        fallback_jobs = fetch_jobicy_jobs("dev", limit)
        if fallback_jobs:
            all_jobs.extend(fallback_jobs)
            
    return all_jobs