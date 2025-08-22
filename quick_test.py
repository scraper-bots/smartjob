#!/usr/bin/env python3
"""
Quick test script for SmartJob scraper - processes just a few candidates for testing
"""

from smartjob_scraper import SmartJobScraper
import json

def main():
    scraper = SmartJobScraper(delay_range=(0.5, 1), output_dir="test_results")
    
    print("Testing scraper with page 1 (first 5 candidates only)...")
    
    # Get first page
    url = "https://smartjob.az/resumes?page=1"
    soup = scraper.get_page(url)
    
    if soup:
        candidates = scraper.extract_candidates_from_listing(soup)
        print(f"Found {len(candidates)} candidates on listing page")
        
        # Process only first 5 candidates
        test_candidates = candidates[:5]
        
        detailed_candidates = []
        for i, candidate in enumerate(test_candidates, 1):
            print(f"Processing candidate {i}/5: {candidate.get('name', 'Unknown')}")
            detailed = scraper.extract_detailed_info(candidate)
            detailed_candidates.append(detailed)
        
        # Save results
        scraper.save_data(detailed_candidates, "test_sample")
        
        # Print sample data
        print(f"\nSample candidate data:")
        if detailed_candidates:
            sample = detailed_candidates[0]
            print(f"Name: {sample.get('name')}")
            print(f"Job Category: {sample.get('job_category')}")
            print(f"Salary: {sample.get('salary')}")
            print(f"Skills: {sample.get('skills', [])[:5]}")  # First 5 skills
            print(f"Education: {len(sample.get('education', []))} entries")
            print(f"Experience: {len(sample.get('experience', []))} entries")
        
        print("\nTest completed successfully!")
    else:
        print("Failed to fetch page")

if __name__ == "__main__":
    main()