import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime, timedelta
import argparse
import json
import os
from pathlib import Path
import time
import re

def get_paper_details(paper_url: str) -> Dict[str, Any]:
    """
    Fetch additional details from a paper's landing page
    
    Args:
        paper_url (str): URL of the paper's landing page
    
    Returns:
        Dict[str, any]: Dictionary containing paper details
    """
    # Add a small delay to avoid overwhelming the server
    time.sleep(0.5)
    
    response = requests.get(paper_url)
    if response.status_code != 200:
        return {}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get authors
    authors = []
    # Find the span with class "author"
    author_spans = soup.find_all('span', class_='author')
    for span in author_spans:
        # Find the button within the span
        button = span.find('button')
        if button:
            author_name = button.text.strip()
            if author_name and not any(c in author_name for c in [',', 'Authors:']):
                authors.append(author_name)
    
    # Get PDF link
    pdf_link = None
    arxiv_id = paper_url.split('/')[-1]
    if arxiv_id.startswith('24') or arxiv_id.startswith('23'):  # Simple check for arxiv IDs
        pdf_link = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    
    # Get abstract
    abstract = ""
    abstract_element = soup.find('p', class_='text-gray-700 dark:text-gray-400')
    if abstract_element:
        abstract = abstract_element.text.strip()
    
    # Get upvotes
    upvotes = 0
    upvote_element = soup.find('div', class_='font-semibold text-orange-500')
    if upvote_element:
        try:
            upvotes = int(upvote_element.text.strip())
        except ValueError:
            pass
    
    return {
        'authors': authors,
        'pdf_url': pdf_link,
        'abstract': abstract,
        'upvotes': upvotes
    }

def scrape_hf_papers(date: str) -> List[Dict[str, str]]:
    """
    Scrape papers from Hugging Face for a specific date
    
    Args:
        date (str): Date in format YYYY-MM-DD
    
    Returns:
        List[Dict[str, str]]: List of papers with their details
    """
    # Validate date format
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")

    # Construct the URL
    url = f"https://huggingface.co/papers?date={date}"
    
    # Make the request
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: Status code {response.status_code}")
    
    # Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all paper entries
    papers = []
    paper_elements = soup.find_all('article', class_='relative flex flex-col overflow-hidden rounded-xl border')
    
    for paper in paper_elements:
        # Find the title and link
        title_element = paper.find('h3')
        if title_element and title_element.find('a'):
            title = title_element.find('a').text.strip()
            paper_url = f"https://huggingface.co{title_element.find('a')['href']}"
            
            # Get additional details from the paper's landing page
            details = get_paper_details(paper_url)
            
            papers.append({
                'title': title,
                'url': paper_url,
                'authors': details.get('authors', []),
                'pdf_url': details.get('pdf_url', ''),
                'abstract': details.get('abstract', ''),
                'upvotes': details.get('upvotes', 0)
            })
    
    return papers

def clean_title(title: str) -> str:
    """
    Clean title to create a valid filename from the first 5 words
    
    Args:
        title (str): Paper title
    
    Returns:
        str: Cleaned filename
    """
    # Remove special characters and replace spaces with underscores
    title = re.sub(r'[^\w\s-]', '', title)
    # Get first 5 words
    words = title.split()[:5]
    # Join words and limit length
    return '_'.join(words)[:100]

def download_pdf(url: str, filepath: str) -> bool:
    """
    Download PDF file from URL
    
    Args:
        url (str): PDF URL
        filepath (str): Path to save the PDF
    
    Returns:
        bool: True if download successful, False otherwise
    """
    try:
        # Add delay to be nice to the server
        time.sleep(0.5)
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        return False
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def save_papers_to_json(papers: List[Dict[str, str]], date: str) -> str:
    """
    Save papers to a JSON file and PDFs in the papers directory
    
    Structure:
    papers/
        - YYYY-MM-DD.json    # Paper information
        - YYYY-MM-DD/        # PDF files
    
    Args:
        papers (List[Dict[str, str]]): List of paper dictionaries
        date (str): Date string in YYYY-MM-DD format
    
    Returns:
        str: Path to the saved JSON file
    """
    # Create base papers directory if it doesn't exist
    base_dir = Path("papers")
    base_dir.mkdir(exist_ok=True)
    
    # Create date-specific directory for PDFs
    pdf_dir = base_dir / date
    pdf_dir.mkdir(exist_ok=True)
    
    # Save JSON file in base directory
    json_file = base_dir / f"{date}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({"date": date, "papers": papers}, f, indent=2, ensure_ascii=False)
    
    # Download PDFs into date-specific directory
    print(f"\nDownloading PDFs to {pdf_dir}...")
    for i, paper in enumerate(papers, 1):
        if paper.get('pdf_url'):
            pdf_filename = clean_title(paper['title']) + '.pdf'
            pdf_path = pdf_dir / pdf_filename
            print(f"[{i}/{len(papers)}] Downloading: {pdf_filename}")
            if download_pdf(paper['pdf_url'], pdf_path):
                print(f"✓ Downloaded: {pdf_filename}")
            else:
                print(f"✗ Failed to download: {pdf_filename}")
    
    return str(json_file)

def get_date_range(start_date: str, end_date: str) -> List[str]:
    """
    Get list of dates between start_date and end_date (inclusive)
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    
    Returns:
        List[str]: List of dates in YYYY-MM-DD format
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Ensure start date is not after end date
    if start > end:
        start, end = end, start
    
    date_list = []
    current = start
    while current <= end:
        date_list.append(current.strftime('%Y-%m-%d'))
        current += timedelta(days=1)
    
    return date_list

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape papers from Hugging Face for a date range')
    parser.add_argument('--start-date', type=str, 
                      help='Start date in YYYY-MM-DD format (default: today)',
                      default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--end-date', type=str,
                      help='End date in YYYY-MM-DD format (default: same as start date)',
                      default=None)
    args = parser.parse_args()
    
    # If end date not provided, use start date
    end_date = args.end_date if args.end_date else args.start_date
    
    try:
        # Get list of dates to process
        dates = get_date_range(args.start_date, end_date)
        total_dates = len(dates)
        
        print(f"\nScraping papers from {dates[0]} to {dates[-1]} ({total_dates} day{'s' if total_dates > 1 else ''})")
        
        # Process each date
        for i, date in enumerate(dates, 1):
            print(f"\n[{i}/{total_dates}] Processing {date}...")
            
            # Scrape papers for this date
            papers = scrape_hf_papers(date)
            
            # Save to JSON file and download PDFs
            json_file = save_papers_to_json(papers, date)
            
            # Print summary for this date
            print(f"\nFound {len(papers)} papers for {date}")
            print(f"Results saved to: {json_file}")
            
            # Add delay between dates
            if i < total_dates:
                time.sleep(1)  # 1 second delay between dates
        
        print(f"\nCompleted! Processed {total_dates} date{'s' if total_dates > 1 else ''}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
