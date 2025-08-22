#!/usr/bin/env python3
"""
Full SmartJob.az scraper - scrapes all 93 pages with optimized settings
"""

from smartjob_scraper import SmartJobScraper
import time
from datetime import datetime

def main():
    print("🚀 Starting FULL SmartJob.az scraping...")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Pages to scrape: 1-93 (~9,300 candidates)")
    print("Estimated time: 6-8 hours")
    print("=" * 60)
    
    # Initialize scraper with optimized settings
    scraper = SmartJobScraper(
        delay_range=(1.5, 2.5),  # Respectful but efficient delays
        output_dir="full_scrape_results"
    )
    
    # Process in batches for better memory management
    batch_size = 10
    all_candidates = []
    
    for start_page in range(1, 94, batch_size):
        end_page = min(start_page + batch_size - 1, 93)
        
        print(f"\n📄 Processing batch: pages {start_page}-{end_page}")
        print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            batch_candidates = scraper.scrape_pages(start_page, end_page)
            all_candidates.extend(batch_candidates)
            
            # Save batch progress
            batch_filename = f"batch_{start_page:02d}_{end_page:02d}"
            scraper.save_data(batch_candidates, batch_filename)
            
            print(f"✅ Batch completed: {len(batch_candidates)} candidates")
            print(f"📊 Total progress: {len(all_candidates)} candidates")
            print(f"📈 Progress: {end_page}/93 pages ({end_page/93*100:.1f}%)")
            
            # Save cumulative progress
            if end_page % 20 == 0 or end_page == 93:  # Save every 20 pages or at end
                cumulative_filename = f"progress_pages_01_{end_page:02d}"
                scraper.save_data(all_candidates, cumulative_filename)
                print(f"💾 Saved cumulative progress: {cumulative_filename}")
            
            # Rest between batches (except last)
            if end_page < 93:
                rest_time = 30  # 30 seconds between batches
                print(f"⏸️  Resting {rest_time} seconds before next batch...")
                time.sleep(rest_time)
                
        except Exception as e:
            print(f"❌ Error in batch {start_page}-{end_page}: {e}")
            print("Continuing with next batch...")
            continue
    
    # Final save
    final_filename = "smartjob_all_candidates_complete"
    scraper.save_data(all_candidates, final_filename)
    
    # Summary
    end_time = datetime.now()
    print("\n" + "=" * 60)
    print("🎉 SCRAPING COMPLETED!")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total candidates: {len(all_candidates)}")
    print(f"Final files: {final_filename}.json and {final_filename}.csv")
    print("=" * 60)

if __name__ == "__main__":
    main()