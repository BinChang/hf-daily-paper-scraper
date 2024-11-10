import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime
import argparse
import json
import os
from pathlib import Path
import time

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

def save_papers_to_json(papers: List[Dict[str, str]], date: str) -> str:
    """
    Save papers to a JSON file in the papers directory
    
    Args:
        papers (List[Dict[str, str]]): List of paper dictionaries
        date (str): Date string in YYYY-MM-DD format
    
    Returns:
        str: Path to the saved JSON file
    """
    # Create papers directory if it doesn't exist
    papers_dir = Path("papers")
    papers_dir.mkdir(exist_ok=True)
    
    # Create filename with date
    filename = papers_dir / f"papers_{date}.json"
    
    # Save papers to JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"date": date, "papers": papers}, f, indent=2, ensure_ascii=False)
    
    return str(filename)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Scrape papers from Hugging Face for a specific date')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format', default=datetime.now().strftime('%Y-%m-%d'))
    args = parser.parse_args()

    try:
        # Scrape papers
        papers = scrape_hf_papers(args.date)
        
        # Save to JSON file
        json_file = save_papers_to_json(papers, args.date)
        
        # Print results
        print(f"\nPapers for {args.date}:")
        for paper in papers:
            print(f"\nTitle: {paper['title']}")
            print(f"URL: {paper['url']}")
            print(f"Authors: {', '.join(paper['authors'])}")
            print(f"PDF URL: {paper['pdf_url']}")
            print(f"Abstract: {paper['abstract']}")
            print(f"Upvotes: {paper['upvotes']}")
        print(f"\nResults saved to: {json_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
