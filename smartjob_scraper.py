#!/usr/bin/env python3
"""
SmartJob.az Resume Scraper

This scraper extracts candidate information from smartjob.az including:
- Basic info from listing pages (name, category, salary, etc.)
- Detailed info from individual resume pages (skills, education, experience, etc.)

Usage:
    python smartjob_scraper.py [--pages N] [--output format]
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, List, Optional
import argparse
import logging
from pathlib import Path

class SmartJobScraper:
    def __init__(self, delay_range=(1, 3), output_dir="scraped_data"):
        self.base_url = "https://smartjob.az"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay_range = delay_range
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch a page with retries and error handling"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(random.uniform(*self.delay_range) * 2)
        
        self.logger.error(f"Failed to fetch {url} after {retries} attempts")
        return None

    def extract_candidates_from_listing(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract candidate basic info from listing page"""
        candidates = []
        
        # Find all candidate cards
        candidate_cards = soup.find_all('div', class_='candidate-list-layout')
        
        for card in candidate_cards:
            try:
                candidate = {}
                
                # Extract name and profile link
                name_link = card.find('h4').find('a') if card.find('h4') else None
                if name_link:
                    candidate['name'] = name_link.get_text(strip=True)
                    candidate['profile_url'] = urljoin(self.base_url, name_link['href'])
                    candidate['resume_id'] = name_link['href'].split('/')[-1] if '/' in name_link['href'] else None
                
                # Extract job category
                job_span = card.find('span', class_='')
                if job_span and job_span.find('i', class_='ti-briefcase'):
                    candidate['job_category'] = job_span.get_text(strip=True)
                
                # Extract category link
                category_link = card.find('a', href=re.compile(r'job_category_id'))
                if category_link:
                    candidate['category_name'] = category_link.get_text(strip=True)
                
                # Extract last updated
                time_elem = card.find('i', class_='ti-time')
                if time_elem and time_elem.parent:
                    candidate['last_updated'] = time_elem.parent.get_text(strip=True).replace('Yenilənib', '').strip()
                
                # Extract salary
                salary_elem = card.find('span', class_='salary-val')
                if salary_elem:
                    candidate['salary'] = salary_elem.get_text(strip=True)
                
                # Extract social media links
                social_links = []
                social_elements = card.find_all('a', class_='soc-ico')
                for social in social_elements:
                    if 'href' in social.attrs:
                        platform = 'linkedin' if 'linkedin' in social['href'] else 'github' if 'github' in social['href'] else 'other'
                        social_links.append({
                            'platform': platform,
                            'url': social['href']
                        })
                candidate['social_links'] = social_links
                
                if candidate.get('name') and candidate.get('profile_url'):
                    candidates.append(candidate)
                    
            except Exception as e:
                self.logger.error(f"Error extracting candidate from card: {e}")
                continue
        
        return candidates

    def extract_detailed_info(self, candidate: Dict) -> Dict:
        """Extract detailed information from individual resume page"""
        if not candidate.get('profile_url'):
            return candidate
        
        soup = self.get_page(candidate['profile_url'])
        if not soup:
            return candidate
        
        try:
            # Extract detailed description
            about_section = soup.find('h2', string='Mənim haqqımda')
            if about_section:
                about_div = about_section.find_next('div', class_='details-text')
                if about_div:
                    candidate['about'] = about_div.get_text(strip=True)
            
            # Extract languages
            languages = []
            lang_section = soup.find('h2', string='Dil bilikləriniz')
            if lang_section:
                lang_div = lang_section.find_next('div')
                if lang_div:
                    for lang_item in lang_div.find_next_siblings('div'):
                        lang_text = lang_item.get_text(strip=True)
                        if '—' in lang_text:
                            lang_parts = lang_text.split('—')
                            if len(lang_parts) >= 2:
                                languages.append({
                                    'language': lang_parts[0].strip(),
                                    'level': lang_parts[1].strip()
                                })
            candidate['languages'] = languages
            
            # Extract education
            education = []
            edu_section = soup.find('h2', string='Təhsil')
            if edu_section:
                edu_list = edu_section.find_next('ul', class_='trim-edu-list')
                if edu_list:
                    for edu_item in edu_list.find_all('li'):
                        edu_info = {}
                        
                        # Education level
                        level_div = edu_item.find('div')
                        if level_div:
                            edu_info['level'] = level_div.get_text(strip=True)
                        
                        # Institution and year
                        title_elem = edu_item.find('h4', class_='trim-edu-title')
                        if title_elem:
                            school_link = title_elem.find('a')
                            if school_link:
                                edu_info['institution'] = school_link.get_text(strip=True)
                            
                            year_span = title_elem.find('span', class_='title-est')
                            if year_span:
                                edu_info['year'] = year_span.get_text(strip=True)
                        
                        # Faculty and field
                        strong_elem = edu_item.find('strong')
                        if strong_elem:
                            faculty_field = strong_elem.get_text(strip=True)
                            if '/' in faculty_field:
                                parts = faculty_field.split('/')
                                edu_info['faculty'] = parts[0].strip()
                                edu_info['field'] = parts[1].strip() if len(parts) > 1 else ''
                        
                        if edu_info:
                            education.append(edu_info)
            candidate['education'] = education
            
            # Extract work experience
            experience = []
            exp_section = soup.find('h2', string='İş təcrübəsi')
            if exp_section:
                exp_list = exp_section.find_next('ul', class_='trim-edu-list')
                if exp_list:
                    for exp_item in exp_list.find_all('li'):
                        exp_info = {}
                        
                        # Company and dates
                        title_elem = exp_item.find('h4', class_='trim-edu-title')
                        if title_elem:
                            company_link = title_elem.find('a')
                            if company_link:
                                exp_info['company'] = company_link.get_text(strip=True)
                            
                            date_span = title_elem.find('span', class_='title-est')
                            if date_span:
                                exp_info['duration'] = date_span.get_text(strip=True)
                        
                        # Position
                        strong_elem = exp_item.find('strong')
                        if strong_elem:
                            exp_info['position'] = strong_elem.get_text(strip=True)
                        
                        if exp_info:
                            experience.append(exp_info)
            candidate['experience'] = experience
            
            # Extract skills from sidebar
            skills = []
            skills_section = soup.find('div', class_='browse-resume-skills')
            if skills_section:
                skill_links = skills_section.find_all('a')
                for skill_link in skill_links:
                    skill_span = skill_link.find('span')
                    if skill_span:
                        skills.append(skill_span.get_text(strip=True))
            candidate['skills'] = skills
            
            # Extract additional info from sidebar
            info_list = soup.find('ul', class_='ove-detail-list')
            if info_list:
                for info_item in info_list.find_all('li'):
                    h5_elem = info_item.find('h5')
                    span_elem = info_item.find('span')
                    
                    if h5_elem and span_elem:
                        key = h5_elem.get_text(strip=True)
                        value = span_elem.get_text(strip=True)
                        
                        if 'Telefon' in key:
                            candidate['phone'] = value
                        elif 'Yaş' in key:
                            candidate['age'] = value
                        elif 'İş stajı' in key:
                            candidate['work_experience'] = value
                        elif 'Təhsil' in key:
                            candidate['education_level'] = value
            
        except Exception as e:
            self.logger.error(f"Error extracting detailed info from {candidate['profile_url']}: {e}")
        
        return candidate

    def scrape_pages(self, start_page: int = 1, end_page: int = 93) -> List[Dict]:
        """Scrape multiple pages of candidates"""
        all_candidates = []
        
        for page in range(start_page, end_page + 1):
            self.logger.info(f"Scraping page {page}/{end_page}")
            
            url = f"{self.base_url}/resumes?page={page}"
            soup = self.get_page(url)
            
            if not soup:
                continue
            
            candidates = self.extract_candidates_from_listing(soup)
            self.logger.info(f"Found {len(candidates)} candidates on page {page}")
            
            # Extract detailed info for each candidate
            for i, candidate in enumerate(candidates, 1):
                self.logger.info(f"Processing candidate {i}/{len(candidates)} on page {page}: {candidate.get('name', 'Unknown')}")
                
                detailed_candidate = self.extract_detailed_info(candidate)
                all_candidates.append(detailed_candidate)
                
                # Rate limiting
                time.sleep(random.uniform(*self.delay_range))
            
            # Save progress periodically
            if page % 5 == 0:
                self.save_data(all_candidates, f"candidates_pages_{start_page}-{page}")
            
            # Rate limiting between pages
            time.sleep(random.uniform(*self.delay_range))
        
        return all_candidates

    def save_data(self, candidates: List[Dict], filename: str):
        """Save candidates data to JSON and CSV files"""
        # Save as JSON
        json_file = self.output_dir / f"{filename}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        
        # Save as CSV
        if candidates:
            csv_file = self.output_dir / f"{filename}.csv"
            fieldnames = set()
            for candidate in candidates:
                fieldnames.update(candidate.keys())
            
            # Define priority order for important fields
            priority_fields = [
                'name', 'phone', 'salary', 'age', 'job_category', 'category_name',
                'work_experience', 'education_level', 'profile_url', 'resume_id',
                'last_updated', 'skills', 'social_links', 'about', 'languages', 
                'education', 'experience'
            ]
            
            # Order fields: priority first, then alphabetical for the rest
            ordered_fields = []
            remaining_fields = set(fieldnames)
            
            for field in priority_fields:
                if field in remaining_fields:
                    ordered_fields.append(field)
                    remaining_fields.remove(field)
            
            # Add any remaining fields alphabetically
            ordered_fields.extend(sorted(list(remaining_fields)))
            fieldnames = ordered_fields
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for candidate in candidates:
                    # Convert lists and dicts to strings for CSV
                    row = {}
                    for key, value in candidate.items():
                        if isinstance(value, (list, dict)):
                            row[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            row[key] = value
                    writer.writerow(row)
        
        self.logger.info(f"Saved {len(candidates)} candidates to {filename}.json and {filename}.csv")

def main():
    parser = argparse.ArgumentParser(description='SmartJob.az Resume Scraper')
    parser.add_argument('--pages', type=int, default=5, help='Number of pages to scrape (default: 5)')
    parser.add_argument('--start-page', type=int, default=1, help='Starting page number (default: 1)')
    parser.add_argument('--output-dir', default='scraped_data', help='Output directory (default: scraped_data)')
    parser.add_argument('--delay', type=float, nargs=2, default=[1, 3], help='Delay range between requests (default: 1 3)')
    
    args = parser.parse_args()
    
    scraper = SmartJobScraper(
        delay_range=tuple(args.delay),
        output_dir=args.output_dir
    )
    
    end_page = min(args.start_page + args.pages - 1, 93)
    
    print(f"Starting scraper...")
    print(f"Pages to scrape: {args.start_page} to {end_page}")
    print(f"Delay between requests: {args.delay[0]}-{args.delay[1]} seconds")
    print(f"Output directory: {args.output_dir}")
    
    candidates = scraper.scrape_pages(args.start_page, end_page)
    
    # Final save
    filename = f"smartjob_candidates_pages_{args.start_page}-{end_page}"
    scraper.save_data(candidates, filename)
    
    print(f"\nScraping completed!")
    print(f"Total candidates scraped: {len(candidates)}")
    print(f"Data saved to: {args.output_dir}/{filename}.json and {args.output_dir}/{filename}.csv")

if __name__ == "__main__":
    main()