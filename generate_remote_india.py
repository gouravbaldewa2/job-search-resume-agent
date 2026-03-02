#!/usr/bin/env python3
"""Generate tailored resumes for additional Remote India jobs."""

import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from search_and_generate import (
    HEADERS, TODAY, OUTPUT_DIR, fetch_job_description,
    extract_keywords, tailor_resume, sanitize_company_name, short_title,
)
from resume_template import generate_resume

# Load the jobs found by the broader search
with open("/tmp/remote_india_jobs.json") as f:
    all_remote_jobs = json.load(f)

# Check which PDFs already exist
existing_pdfs = set(os.listdir(OUTPUT_DIR))

print(f"Found {len(all_remote_jobs)} Remote India jobs to process")

generated = []
for job in all_remote_jobs:
    company_safe = sanitize_company_name(job["company"])
    title_short = short_title(job["title"])
    filename = f"Remote_{company_safe}_{title_short}_{TODAY}.pdf"
    output_path = os.path.join(OUTPUT_DIR, filename)

    if filename in existing_pdfs:
        print(f"  Skipping (already exists): {filename}")
        generated.append({"filename": filename, "job": job})
        continue

    # Fetch JD
    jd_text = ""
    if job.get("job_id"):
        print(f"  Fetching JD for {job['title']} at {job['company']}...")
        jd_text = fetch_job_description(job["job_id"])
        if jd_text:
            print(f"    -> Got {len(jd_text)} chars")
        time.sleep(0.5)

    if not jd_text:
        jd_text = f"{job['title']} at {job['company']}"

    keywords = extract_keywords(jd_text)
    content = tailor_resume(job, jd_text, keywords)

    try:
        generate_resume(content, output_path)
        generated.append({"filename": filename, "job": job})
        print(f"  Generated: {filename}")
    except Exception as e:
        print(f"  ERROR generating {filename}: {e}")

print(f"\nTotal Remote India PDFs: {len(generated)}")

# Save the job list for summary generation
with open("/tmp/remote_india_generated.json", "w") as f:
    json.dump([{
        "filename": g["filename"],
        "title": g["job"]["title"],
        "company": g["job"]["company"],
        "link": g["job"].get("link", ""),
        "job_id": g["job"].get("job_id", ""),
        "location": g["job"].get("location", ""),
    } for g in generated], f, indent=2)
