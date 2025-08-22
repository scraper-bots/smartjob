#!/usr/bin/env python3
"""
Batch scraper for SmartJob.az - processes pages in smaller batches for better control
"""

from smartjob_scraper import SmartJobScraper
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description='Batch SmartJob.az Resume Scraper')
    parser.add_argument('--batch-size', type=int, default=10, help='Pages per batch (default: 10)')
    parser.add_argument('--start-page', type=int, default=1, help='Starting page (default: 1)')
    parser.add_argument('--end-page', type=int, default=93, help='Ending page (default: 93)')
    parser.add_argument('--batch-delay', type=int, default=30, help='Seconds to wait between batches (default: 30)')
    parser.add_argument('--output-dir', default='scraped_data', help='Output directory')
    
    args = parser.parse_args()
    
    scraper = SmartJobScraper(
        delay_range=(1, 3),
        output_dir=args.output_dir
    )
    
    print(f"Starting batch scraping...")
    print(f"Pages: {args.start_page} to {args.end_page}")
    print(f"Batch size: {args.batch_size} pages")
    print(f"Batch delay: {args.batch_delay} seconds")
    
    total_candidates = []
    
    for start_page in range(args.start_page, args.end_page + 1, args.batch_size):
        end_page = min(start_page + args.batch_size - 1, args.end_page)
        
        print(f"\n--- Processing batch: pages {start_page} to {end_page} ---")
        
        batch_candidates = scraper.scrape_pages(start_page, end_page)
        total_candidates.extend(batch_candidates)
        
        # Save batch results
        batch_filename = f"batch_pages_{start_page}_{end_page}"
        scraper.save_data(batch_candidates, batch_filename)
        
        print(f"Batch completed: {len(batch_candidates)} candidates")
        print(f"Total so far: {len(total_candidates)} candidates")
        
        # Wait between batches (except for the last one)
        if end_page < args.end_page:
            print(f"Waiting {args.batch_delay} seconds before next batch...")
            time.sleep(args.batch_delay)
    
    # Save final combined results
    final_filename = f"all_candidates_pages_{args.start_page}_{args.end_page}"
    scraper.save_data(total_candidates, final_filename)
    
    print(f"\n✅ Scraping completed!")
    print(f"Total candidates scraped: {len(total_candidates)}")
    print(f"Final data saved as: {final_filename}.json and {final_filename}.csv")

if __name__ == "__main__":
    main()