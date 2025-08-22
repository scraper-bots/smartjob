# SmartJob.az Resume Scraper

A comprehensive Python scraper for extracting candidate information from smartjob.az, including both basic listing data and detailed resume information.

## Features

- **Multi-page scraping**: Scrapes all 93 pages (~9,300 candidates)
- **Detailed extraction**: Gets comprehensive candidate data including:
  - Basic info (name, job category, salary, contact)
  - Skills and experience
  - Education history
  - Work experience
  - Languages
  - Social media links
- **Data export**: Saves data in both JSON and CSV formats
- **Rate limiting**: Respectful scraping with configurable delays
- **Error handling**: Robust error handling and retry mechanisms
- **Progress tracking**: Detailed logging and periodic saves

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Full Scraping (All 93 Pages)
```bash
python3 full_scrape.py
```

### Scrape Specific Pages
```bash
# Scrape first 5 pages
python3 smartjob_scraper.py --pages 5

# Scrape pages 10-15
python3 smartjob_scraper.py --start-page 10 --pages 6

# Scrape all pages (will take several hours)
python3 smartjob_scraper.py --start-page 1 --pages 93
```

### Advanced Options
```bash
# Custom delay and output directory
python3 smartjob_scraper.py --pages 10 --delay 2 5 --output-dir my_data

# Faster scraping (be careful not to overload the server)
python3 smartjob_scraper.py --pages 5 --delay 0.5 1
```

## Data Structure

### Candidate Data Fields

```json
{
  "name": "Candidate Name",
  "profile_url": "https://smartjob.az/resume/...",
  "resume_id": "12345-job-title",
  "job_category": "Frontend Development",
  "category_name": "Web development",
  "last_updated": "22.08.2025",
  "salary": "2 700 AZN",
  "phone": "994795760002",
  "age": "21",
  "work_experience": "2 il",
  "education_level": "Magistr",
  "social_links": [
    {"platform": "github", "url": "..."},
    {"platform": "linkedin", "url": "..."}
  ],
  "about": "Detailed description...",
  "skills": ["React.js", "JavaScript", "..."],
  "languages": [
    {"language": "English", "level": "B2"}
  ],
  "education": [
    {
      "level": "Magistr",
      "institution": "University Name",
      "year": "2024",
      "faculty": "Faculty Name",
      "field": "Field of Study"
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "duration": "01.2023 - 12.2023",
      "position": "Job Title"
    }
  ]
}
```

## Output Files

- `candidates_pages_X-Y.json` - Complete data in JSON format
- `candidates_pages_X-Y.csv` - Flattened data for Excel/analysis
- `scraper.log` - Detailed scraping log

## Performance Notes

- **Full scraping**: ~93 pages × 100 candidates = ~9,300 candidates
- **Estimated time**: 6-12 hours (depending on delay settings)
- **Rate limiting**: 1-3 second delays between requests (configurable)
- **Memory usage**: Moderate (saves progress every 5 pages)

## Best Practices

1. **Start small**: Test with a few pages first
2. **Respect the server**: Don't set delays too low
3. **Monitor logs**: Check scraper.log for any issues
4. **Resume capability**: The scraper can resume from where it left off

## Example Batch Processing

```python
from smartjob_scraper import SmartJobScraper

# Initialize scraper
scraper = SmartJobScraper(delay_range=(1, 2))

# Process in smaller batches
for start_page in range(1, 94, 10):  # Process 10 pages at a time
    end_page = min(start_page + 9, 93)
    candidates = scraper.scrape_pages(start_page, end_page)
    scraper.save_data(candidates, f"batch_{start_page}_{end_page}")
```

## Legal and Ethical Considerations

- This scraper is for educational and research purposes
- Respect the website's robots.txt and terms of service
- Use reasonable delays to avoid overloading the server
- Consider the privacy of the scraped data