#!/usr/bin/env python3
"""Search LinkedIn for PM jobs, fetch JDs, tailor resumes, and generate PDFs."""

import copy
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from base_resume import BASE_CONTENT
from resume_template import generate_resume

TODAY = "2026-03-02"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TITLES = [
    "lead%20product%20manager",
    "staff%20product%20manager",
    "principal%20product%20manager",
    "group%20product%20manager",
    "senior%20product%20manager",
]

TITLE_PATTERNS = [
    "lead product manager",
    "staff product manager",
    "principal product manager",
    "group product manager",
    "senior product manager",
    "sr. product manager",
    "sr product manager",
]

LOCATIONS = {
    "Bangalore": "Bangalore%2C%20India",
    "Dubai": "Dubai%2C%20United%20Arab%20Emirates",
    "Netherlands": "Netherlands",
    "Remote India": "India",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def search_linkedin_jobs(title_encoded, location_encoded, is_remote=False):
    """Search LinkedIn for jobs and return raw HTML."""
    url = (
        f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={title_encoded}&location={location_encoded}&f_TPR=r86400"
    )
    if is_remote:
        url += "&f_WT=2"
    url += "&start=0"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"  HTTP {resp.status_code} for {title_encoded} in {location_encoded}")
            return ""
    except Exception as e:
        print(f"  Error: {e}")
        return ""


def parse_job_listings(html):
    """Parse LinkedIn job listing HTML and return list of job dicts."""
    jobs = []
    if not html or len(html.strip()) < 50:
        return jobs

    soup = BeautifulSoup(html, "html.parser")

    # LinkedIn guest API returns <li> cards with job info
    cards = soup.find_all("li")
    if not cards:
        # Try finding divs with base-card class
        cards = soup.find_all("div", class_=re.compile(r"base-card|job-search-card"))

    for card in cards:
        title_el = card.find("h3", class_=re.compile(r"base-search-card__title"))
        if not title_el:
            title_el = card.find("span", class_=re.compile(r"sr-only"))
        if not title_el:
            title_el = card.find("h3")

        company_el = card.find("h4", class_=re.compile(r"base-search-card__subtitle"))
        if not company_el:
            company_el = card.find("a", class_=re.compile(r"hidden-nested-link"))
        if not company_el:
            company_el = card.find("h4")

        link_el = card.find("a", class_=re.compile(r"base-card__full-link"))
        if not link_el:
            link_el = card.find("a", href=re.compile(r"linkedin.com/jobs/view"))
        if not link_el:
            link_el = card.find("a", href=True)

        location_el = card.find("span", class_=re.compile(r"job-search-card__location"))

        if title_el:
            title = title_el.get_text(strip=True)
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            link = link_el["href"] if link_el and link_el.get("href") else ""
            location = location_el.get_text(strip=True) if location_el else ""

            # Extract job ID from data-entity-urn (on inner div, not li)
            job_id = ""
            urn_el = card.find(attrs={"data-entity-urn": True})
            if urn_el:
                urn = urn_el["data-entity-urn"]
                match = re.search(r":(\d+)$", urn)
                if match:
                    job_id = match.group(1)

            # Fallback: extract from URL (last large number in path)
            if not job_id and link:
                # LinkedIn URLs: /view/slug-text-JOBID?params
                match = re.search(r"-(\d{7,})", link)
                if match:
                    job_id = match.group(1)
                else:
                    match = re.search(r"currentJobId=(\d+)", link)
                    if match:
                        job_id = match.group(1)

            jobs.append({
                "title": title,
                "company": company,
                "link": link,
                "location": location,
                "job_id": job_id,
            })

    return jobs


def matches_title_filter(title):
    """Check if a job title matches our target PM roles."""
    t = title.lower()
    for pattern in TITLE_PATTERNS:
        if pattern in t:
            return True
    return False


def fetch_job_description(job_id):
    """Fetch the full job description for a given job ID."""
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract the description
            desc_div = soup.find("div", class_=re.compile(r"description|show-more-less-html"))
            if desc_div:
                return desc_div.get_text(separator="\n", strip=True)

            # Fallback: get all text
            body = soup.find("body")
            if body:
                return body.get_text(separator="\n", strip=True)
            return soup.get_text(separator="\n", strip=True)
        else:
            print(f"  JD fetch HTTP {resp.status_code} for job {job_id}")
            return ""
    except Exception as e:
        print(f"  JD fetch error for {job_id}: {e}")
        return ""


def extract_keywords(jd_text):
    """Extract relevant keywords from a job description."""
    keywords = {
        "domains": [],
        "skills": [],
        "themes": [],
    }

    jd_lower = jd_text.lower()

    domain_terms = [
        "fintech", "marketplace", "e-commerce", "ecommerce", "consumer", "b2b", "b2c",
        "saas", "payments", "banking", "insurance", "healthcare", "edtech", "logistics",
        "mobility", "travel", "media", "advertising", "adtech", "social", "gaming",
        "enterprise", "platform", "cloud", "data", "ai", "machine learning", "ml",
        "supply chain", "retail", "foodtech", "proptech", "real estate", "crypto",
        "blockchain", "iot", "telecom", "cybersecurity", "security", "devtools",
        "developer tools", "hr tech", "legaltech", "agritech", "cleantech",
    ]
    skill_terms = [
        "a/b testing", "experimentation", "user research", "data analytics",
        "sql", "python", "agile", "scrum", "kanban", "okr", "kpi",
        "roadmap", "road-mapping", "stakeholder management", "cross-functional",
        "product strategy", "product vision", "go-to-market", "gtm",
        "user acquisition", "retention", "engagement", "monetization",
        "funnel optimization", "funnel optimisation", "conversion",
        "pricing", "segmentation", "personalization", "personalisation",
        "design thinking", "lean", "customer discovery", "prototyping",
        "api", "microservices", "system design", "technical architecture",
        "mobile", "web", "ios", "android", "react", "growth",
        "product-led growth", "plg", "product analytics", "behavioural analytics",
        "behavioral analytics", "customer journey",
    ]
    theme_terms = [
        "consumer experience", "digital transformation", "scale", "high-traffic",
        "regulated", "compliance", "international", "global", "multi-market",
        "two-sided marketplace", "supply and demand", "network effects",
        "subscription", "freemium", "enterprise sales", "self-serve",
        "platform thinking", "ecosystem", "integrations", "partnerships",
        "localization", "internationalisation", "emerging markets",
        "customer-centric", "user-centric", "impact", "innovation",
        "startup", "hypergrowth", "zero to one", "0 to 1",
    ]

    for term in domain_terms:
        if term in jd_lower:
            keywords["domains"].append(term)
    for term in skill_terms:
        if term in jd_lower:
            keywords["skills"].append(term)
    for term in theme_terms:
        if term in jd_lower:
            keywords["themes"].append(term)

    return keywords


def sanitize_company_name(name):
    """Create a filesystem-safe company name."""
    name = re.sub(r"[^a-zA-Z0-9]", "", name.replace(" ", ""))
    return name[:30] if name else "Unknown"


def short_title(title):
    """Shorten a job title for filenames."""
    t = title.lower()
    if "lead" in t:
        return "LeadPM"
    if "staff" in t:
        return "StaffPM"
    if "principal" in t:
        return "PrincipalPM"
    if "group" in t:
        return "GroupPM"
    if "senior" in t:
        return "SeniorPM"
    return "PM"


def tailor_resume(job, jd_text, keywords):
    """Create a tailored resume content dict for a specific job."""
    content = copy.deepcopy(BASE_CONTENT)

    company = job["company"]
    title = job["title"]
    jd_lower = jd_text.lower()

    # Determine primary domain focus from JD
    domain_focus = []
    if any(d in jd_lower for d in ["fintech", "payments", "banking", "financial"]):
        domain_focus.append("fintech")
    if any(d in jd_lower for d in ["marketplace", "two-sided", "supply and demand"]):
        domain_focus.append("marketplace")
    if any(d in jd_lower for d in ["consumer", "b2c", "user experience", "consumer experience"]):
        domain_focus.append("consumer")
    if any(d in jd_lower for d in ["e-commerce", "ecommerce", "retail", "catalog"]):
        domain_focus.append("ecommerce")
    if any(d in jd_lower for d in ["saas", "b2b", "enterprise"]):
        domain_focus.append("enterprise")
    if any(d in jd_lower for d in ["growth", "acquisition", "retention", "engagement"]):
        domain_focus.append("growth")
    if any(d in jd_lower for d in ["platform", "api", "infrastructure", "developer"]):
        domain_focus.append("platform")
    if any(d in jd_lower for d in ["mobile", "app", "ios", "android"]):
        domain_focus.append("mobile")
    if any(d in jd_lower for d in ["ai", "machine learning", "ml", "data science"]):
        domain_focus.append("ai/ml")
    if any(d in jd_lower for d in ["logistics", "supply chain", "operations"]):
        domain_focus.append("logistics")
    if any(d in jd_lower for d in ["healthcare", "health", "wellness"]):
        domain_focus.append("healthcare")
    if any(d in jd_lower for d in ["travel", "mobility", "transport"]):
        domain_focus.append("mobility")

    if not domain_focus:
        domain_focus = ["consumer", "marketplace"]

    # Build tailored summary
    primary = ", ".join(domain_focus[:3])
    summary_parts = [
        f"Senior product leader with 9+ years building high-traffic, consumer-facing digital products across {primary} domains.",
    ]

    if "marketplace" in domain_focus or "ecommerce" in domain_focus:
        summary_parts.append(
            "Led end-to-end product lifecycles spanning research, discovery, design, and continuous optimisation "
            "for marketplace and commerce products serving 10Mn+ users across India, Europe, and Latin America."
        )
    elif "fintech" in domain_focus:
        summary_parts.append(
            "Led end-to-end product lifecycles for fintech and digital banking products, from research and discovery "
            "through design and continuous optimisation, serving 10Mn+ users across India and Europe."
        )
    elif "platform" in domain_focus:
        summary_parts.append(
            "Led end-to-end product lifecycles for platform and API-driven products, from research and discovery "
            "through design and continuous optimisation, serving 10Mn+ users across India, Europe, and Latin America."
        )
    else:
        summary_parts.append(
            "Led end-to-end product lifecycles spanning research, discovery, design, and continuous optimisation "
            "for products serving 10Mn+ users across India, Europe (Amsterdam-based at Freenow), and Latin America."
        )

    if "growth" in domain_focus or "experimentation" in keywords.get("skills", []):
        summary_parts.append(
            "Comfortable championing experimentation culture, driving data-informed decisions, "
            "and mentoring product managers to raise the bar on product practices."
        )
    else:
        summary_parts.append(
            "Comfortable influencing senior stakeholders without direct authority, championing experimentation "
            "culture across engineering and design, and mentoring product managers to raise the bar."
        )

    content["summary"] = " ".join(summary_parts)

    # Tailor skills
    jd_skills = keywords.get("skills", [])
    base_skills = [
        "A/B testing", "design thinking", "lean product", "agile/scrum", "SQL",
        "behavioural analytics", "funnel optimisation", "road-mapping", "stakeholder management"
    ]
    extra_skills = []
    if "product strategy" in jd_skills:
        extra_skills.append("product strategy")
    if "go-to-market" in jd_skills or "gtm" in jd_skills:
        extra_skills.append("go-to-market")
    if "user research" in jd_skills:
        extra_skills.append("user research")
    if "pricing" in jd_skills:
        extra_skills.append("pricing strategy")
    if "growth" in jd_skills or "product-led growth" in jd_skills:
        extra_skills.append("product-led growth")
    if "mobile" in jd_skills:
        extra_skills.append("mobile product development")
    if "customer journey" in jd_skills:
        extra_skills.append("customer journey mapping")
    if "okr" in jd_skills:
        extra_skills.append("OKRs")

    all_skills = base_skills + extra_skills
    content["skills"] = ", ".join(all_skills[:10])

    # Tailor domain
    domain_labels = {
        "fintech": "Fintech",
        "marketplace": "Marketplace",
        "consumer": "Consumer products",
        "ecommerce": "E-commerce",
        "enterprise": "Enterprise SaaS",
        "growth": "Growth",
        "platform": "Platform/API",
        "mobile": "Mobile",
        "ai/ml": "AI/ML products",
        "logistics": "Logistics",
        "healthcare": "Healthcare",
        "mobility": "Mobility",
    }
    domain_list = [domain_labels.get(d, d.title()) for d in domain_focus[:4]]
    domain_list.extend(["customer segmentation", "experimentation", "regulated environments"])
    content["domain"] = ", ".join(domain_list[:6])

    # Tailor role descriptions based on JD themes
    roles = content["roles"]

    # Mahindra Finance role
    if "marketplace" in domain_focus:
        roles[0]["blocks"][0]["text"] = "Consumer experience at scale in a high-traffic marketplace environment"
    elif "growth" in domain_focus:
        roles[0]["blocks"][0]["text"] = "Consumer growth and acquisition in a high-traffic environment"
    elif "platform" in domain_focus:
        roles[0]["blocks"][0]["text"] = "Platform-driven consumer experience at scale"

    if "growth" in domain_focus or "acquisition" in jd_lower:
        roles[0]["blocks"][2]["text"] = "Growth, experimentation, and data-driven optimisation"
    elif "experimentation" in jd_lower:
        roles[0]["blocks"][2]["text"] = "Experimentation-led growth and conversion optimisation"

    # Freenow role - emphasize marketplace/pricing/international
    if "marketplace" in domain_focus:
        roles[1]["tagline"] = "Two-sided marketplace | Amsterdam-based | 5Mn+ rides daily | Multi-country European and LatAm markets"
    elif "international" in keywords.get("themes", []) or "global" in keywords.get("themes", []):
        roles[1]["tagline"] = "Global marketplace platform | Amsterdam-based | Multi-country European and LatAm expansion"

    # Walmart role - emphasize platform/ML/ecommerce
    if "ecommerce" in domain_focus or "ai/ml" in domain_focus:
        roles[2]["tagline"] = "Consumer marketplace | ML-driven product discovery across 250Mn+ SKUs"
    elif "platform" in domain_focus:
        roles[2]["tagline"] = "Platform product at scale | Catalogue and data infrastructure across 250Mn+ SKUs"

    # Bounce role - emphasize consumer/mobility
    if "consumer" in domain_focus or "mobile" in domain_focus:
        roles[3]["tagline"] = "Consumer mobile product for young urban commuters"
    elif "growth" in domain_focus:
        roles[3]["tagline"] = "Consumer marketplace | Growth-stage product for urban commuters"

    # McKinsey role
    if "enterprise" in domain_focus or "saas" in domain_focus:
        roles[4]["tagline"] = "Enterprise digital transformation across 5+ clients in India, Singapore, Thailand, and Indonesia"
    elif "fintech" in domain_focus:
        roles[4]["tagline"] = "Digital product strategy for banking, fintech, and insurance clients across 4 countries"

    return content


def main():
    all_jobs = {
        "Bangalore": [],
        "Dubai": [],
        "Netherlands": [],
        "Remote India": [],
    }
    blocked = False

    print("=" * 60)
    print("STEP 1: Searching LinkedIn for PM jobs")
    print("=" * 60)

    for location_label, location_encoded in LOCATIONS.items():
        is_remote = (location_label == "Remote India")
        print(f"\n--- Searching in {location_label} ---")

        for title_encoded in TITLES:
            title_readable = title_encoded.replace("%20", " ")
            print(f"  Searching: {title_readable} in {location_label}...")

            html = search_linkedin_jobs(title_encoded, location_encoded, is_remote=is_remote)
            if not html or len(html.strip()) < 50:
                if "captcha" in (html or "").lower() or "authwall" in (html or "").lower():
                    blocked = True
                    print("  -> LinkedIn appears to be blocking requests")
                else:
                    print("  -> No results or empty response")
                continue

            if "captcha" in html.lower() or "authwall" in html.lower():
                blocked = True
                print("  -> LinkedIn blocking detected")
                continue

            jobs = parse_job_listings(html)
            print(f"  -> Found {len(jobs)} raw listings")

            for job in jobs:
                if matches_title_filter(job["title"]):
                    # Avoid duplicates
                    existing_ids = [j["job_id"] for j in all_jobs[location_label] if j.get("job_id")]
                    if job["job_id"] and job["job_id"] not in existing_ids:
                        job["location_group"] = location_label
                        all_jobs[location_label].append(job)
                        print(f"     + {job['title']} at {job['company']}")

            time.sleep(1)  # Rate limiting

    # For remote India, try additional pagination to get more results
    if len(all_jobs["Remote India"]) < 10:
        print("\n--- Trying additional pagination for Remote India ---")
        for start in [25, 50]:
            for title_encoded in TITLES:
                url = (
                    f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                    f"?keywords={title_encoded}&location=India&f_TPR=r86400&f_WT=2&start={start}"
                )
                try:
                    resp = requests.get(url, headers=HEADERS, timeout=15)
                    if resp.status_code == 200 and len(resp.text.strip()) > 50:
                        jobs = parse_job_listings(resp.text)
                        for job in jobs:
                            if matches_title_filter(job["title"]):
                                existing_ids = [j["job_id"] for j in all_jobs["Remote India"] if j.get("job_id")]
                                if job["job_id"] and job["job_id"] not in existing_ids:
                                    job["location_group"] = "Remote India"
                                    all_jobs["Remote India"].append(job)
                                    print(f"     + {job['title']} at {job['company']}")
                except Exception:
                    pass
                time.sleep(1)
            if len(all_jobs["Remote India"]) >= 10:
                break

    total = sum(len(v) for v in all_jobs.values())
    print(f"\nTotal matching jobs found: {total}")
    for loc, jobs in all_jobs.items():
        print(f"  {loc}: {len(jobs)}")

    # Print summary
    print("\n" + "=" * 60)
    print("STEP 2: Fetching job descriptions")
    print("=" * 60)

    jd_data = {}  # job_id -> jd_text
    for location_label, jobs in all_jobs.items():
        for job in jobs:
            if job.get("job_id"):
                print(f"  Fetching JD for {job['title']} at {job['company']}...")
                jd = fetch_job_description(job["job_id"])
                if jd:
                    jd_data[job["job_id"]] = jd
                    print(f"    -> Got {len(jd)} chars")
                else:
                    print(f"    -> Empty/failed")
                time.sleep(0.5)

    print(f"\nFetched {len(jd_data)} job descriptions")

    print("\n" + "=" * 60)
    print("STEPS 3 & 4: Tailoring resumes and generating PDFs")
    print("=" * 60)

    generated = []
    for location_label, jobs in all_jobs.items():
        for job in jobs:
            jid = job.get("job_id", "")
            jd_text = jd_data.get(jid, "")
            if not jd_text:
                jd_text = f"{job['title']} at {job['company']}"

            keywords = extract_keywords(jd_text)
            content = tailor_resume(job, jd_text, keywords)

            company_safe = sanitize_company_name(job["company"])
            title_short = short_title(job["title"])
            prefix = "Remote_" if location_label == "Remote India" else ""
            filename = f"{prefix}{company_safe}_{title_short}_{TODAY}.pdf"
            output_path = os.path.join(OUTPUT_DIR, filename)

            try:
                generate_resume(content, output_path)
                generated.append({
                    "filename": filename,
                    "job": job,
                    "location_group": location_label,
                })
                print(f"  Generated: {filename}")
            except Exception as e:
                print(f"  ERROR generating {filename}: {e}")

    print(f"\nGenerated {len(generated)} PDFs")

    # Write summary.md
    print("\n" + "=" * 60)
    print("STEP 5: Writing summary.md")
    print("=" * 60)

    with open("summary.md", "w") as f:
        f.write(f"# Job Search Summary - {TODAY}\n\n")

        if blocked and total == 0:
            f.write("**Note:** LinkedIn blocked automated requests. No jobs could be fetched.\n")
            f.write("This is expected when running from a server/CI environment without browser cookies.\n\n")
        elif blocked:
            f.write("**Note:** Some LinkedIn requests were blocked. Results may be incomplete.\n\n")

        for location_label in ["Bangalore", "Dubai", "Netherlands", "Remote India"]:
            jobs = all_jobs[location_label]
            f.write(f"## {location_label}\n\n")
            if not jobs:
                f.write("No matching jobs found in this location.\n\n")
                continue
            for job in jobs:
                link = job.get("link", "")
                if link and not link.startswith("http"):
                    link = "https://www.linkedin.com" + link
                job_url = link if link else f"https://www.linkedin.com/jobs/view/{job.get('job_id', '')}"
                f.write(f"- **{job['title']}** at {job['company']}")
                if job_url:
                    f.write(f" - [View Job]({job_url})")
                f.write("\n")
            f.write("\n")

        f.write(f"## Generated Resumes\n\n")
        if generated:
            for g in generated:
                f.write(f"- `{g['filename']}` - {g['job']['title']} at {g['job']['company']} ({g['location_group']})\n")
        else:
            f.write("No resumes were generated (no matching jobs found or LinkedIn blocked requests).\n")
        f.write("\n")
        f.write(f"---\n*Generated on {TODAY} by Oz agent*\n")

    print("summary.md written")

    # Return data for commit step
    return {
        "total_jobs": total,
        "generated": len(generated),
        "blocked": blocked,
        "all_jobs": all_jobs,
    }


if __name__ == "__main__":
    result = main()
    # Save result as JSON for potential use by other scripts
    with open("search_result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nDone. Total jobs: {result['total_jobs']}, PDFs generated: {result['generated']}")
