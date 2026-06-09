import argparse
import sys
import csv
from app.parsers.pdf_parser import parse_resume_pdf
from app.nlp.extractor import extract_info
from app.search.job_fetcher import fetch_jobs
from app.matching.matcher import rank_jobs
from app.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    parser = argparse.ArgumentParser(description="AI Resume Parser & Job Finder CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search Command
    search_parser = subparsers.add_parser("search", help="Parse resume and find jobs")
    search_parser.add_argument("--resume", required=True, help="Path to the PDF resume")
    search_parser.add_argument("--top", type=int, default=5, help="Number of results to show")
    search_parser.add_argument("--save-csv", help="Path to save results as CSV")
    search_parser.add_argument("--open", action="store_true", help="Open top result in browser")

    args = parser.parse_args()

    if args.command == "search":
        try:
            # 1. Parse PDF
            logger.info(f"Parsing resume: {args.resume}")
            resume_text = parse_resume_pdf(args.resume)
            if not resume_text:
                logger.error("Failed to extract text from PDF.")
                sys.exit(1)

            # 2. Extract Info
            logger.info("Extracting skills and keywords...")
            extracted_data = extract_info(resume_text)
            
            # 3. Fetch Jobs (Smart logic handled in job_fetcher)
            skills = extracted_data['skills']
            if skills:
                search_query = skills[0] # Use top skill
            elif extracted_data['designation']:
                search_query = extracted_data['designation'][0]
            else:
                search_query = "dev"

            logger.info(f"Fetching jobs for: '{search_query}'...")
            
            jobs = fetch_jobs(search_query, limit=20)
            if not jobs:
                logger.warning("No jobs found even after fallback.")
                sys.exit(0)
            
            # 4. Rank Jobs
            logger.info("Ranking jobs using AI embeddings...")
            ranked_jobs = rank_jobs(resume_text, jobs, top_k=args.top)

            # 5. Display
            print(f"\n=== Top {len(ranked_jobs)} Matches ===")
            for i, job in enumerate(ranked_jobs, 1):
                print(f"{i}. [{job['score']:.2f}% Match] {job['title']} @ {job['company']}")
                print(f"   Location: {job['location']}")
                print(f"   Link: {job['url']}")
                print("-" * 40)

            # 6. Save CSV
            if args.save_csv:
                keys = ranked_jobs[0].keys()
                with open(args.save_csv, 'w', newline='', encoding='utf-8') as f:
                    dict_writer = csv.DictWriter(f, fieldnames=keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(ranked_jobs)
                logger.info(f"Results saved to {args.save_csv}")

            # 7. Open Browser
            if args.open and ranked_jobs:
                import webbrowser
                webbrowser.open(ranked_jobs[0]['url'])

        except Exception as e:
            logger.error(f"An error occurred: {e}", exc_info=True)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()