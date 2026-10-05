import asyncio
import re
import httpx

SOURCES = [
    {"company": "XM", "type": "lever", "slug": "xm"},
    {"company": "Welltech", "type": "ashby", "slug": "welltech"},
    {"company": "HyperHug", "type": "ashby", "slug": "hyperhug"},
]

CYPRUS_WORDS = ["cyprus", "limassol", "nicosia", "larnaca", "paphos"]

IT_PATTERN = re.compile(
    r"\b(engineer|engineers|developer|developers|qa|test|sdet|software|automation)\b",
    re.IGNORECASE,
)

SENIOR_PATTERN = re.compile(
    r"\b(senior|lead|head|principal|director|manager|chief|vp)\b",
    re.IGNORECASE,
)
JUNIOR_PATTERN = re.compile(
    r"\b(junior|trainee|intern|internship|graduate|entry)\b",
    re.IGNORECASE,
)


async def fetch_lever(client, company, slug):
    for host in ("api.eu.lever.co", "api.lever.co"):
        resp = await client.get(
            f"https://{host}/v0/postings/{slug}", params={"mode": "json"}
        )
        if resp.status_code == 200:
            return [
                {
                    "company": company,
                    "title": item.get("text", ""),
                    "location": (item.get("categories") or {}).get("location") or "",
                    "url": item.get("hostedUrl", ""),
                }
                for item in resp.json()
            ]
    return []


async def fetch_ashby(client, company, slug):
    resp = await client.get(
        f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    )
    if resp.status_code != 200:
        return []
    return [
        {
            "company": company,
            "title": job.get("title", ""),
            "location": job.get("location") or "",
            "url": job.get("jobUrl", ""),
        }
        for job in resp.json().get("jobs", [])
    ]


async def fetch_all():
    jobs = []
    async with httpx.AsyncClient(timeout=15) as client:
        for source in SOURCES:
            try:
                if source["type"] == "lever":
                    found = await fetch_lever(client, source["company"], source["slug"])
                else:
                    found = await fetch_ashby(client, source["company"], source["slug"])
            except Exception as error:
                print(f"{source['company']}: error - {error}")
                found = []
            print(f"{source['company']}: {len(found)} jobs fetched")
            jobs.extend(found)
    return jobs


def is_relevant(job):
    title = job["title"]
    location = job["location"].lower()
    in_cyprus = any(word in location for word in CYPRUS_WORDS)
    is_it = bool(IT_PATTERN.search(title))
    is_senior = bool(SENIOR_PATTERN.search(title))
    return in_cyprus and is_it and not is_senior


def is_junior(job):
    return bool(JUNIOR_PATTERN.search(job["title"]))


async def get_relevant_jobs():
    jobs = await fetch_all()
    relevant = [job for job in jobs if is_relevant(job)]
    relevant.sort(key=lambda job: not is_junior(job))
    return relevant


async def main():
    relevant = await get_relevant_jobs()
    print(f"\nRelevant for you: {len(relevant)}\n")
    for job in relevant:
        mark = "🟢 " if is_junior(job) else ""
        print(f"{mark}{job['company']} | {job['title']} | {job['location']}")
        print(f"  {job['url']}\n")


if __name__ == "__main__":
    asyncio.run(main())