# Hugging Face Daily Papers Scraper

A Python script to scrape and collect papers from [Hugging Face's Daily Papers](https://huggingface.co/papers) page. The scraper extracts comprehensive information about each paper and saves it in JSON format.

## Features

- Scrape papers for any specific date
- Extract detailed paper information:
  - Title
  - Landing page URL
  - Complete list of authors
  - PDF link (arxiv)
  - Full abstract
  - Upvote count
- Save results in JSON format
- Rate limiting to be server-friendly
- Command-line interface with date parameter

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd hf-daily-paper-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Run the script without parameters to scrape today's papers:
```bash
python hf_paper_scraper.py
```

### Specify a Date
Use the `--date` parameter to scrape papers from a specific date:
```bash
python hf_paper_scraper.py --date 2024-01-06
```

### Output
The script will:
1. Create a `papers` directory if it doesn't exist
2. Save the results in `papers/papers_YYYY-MM-DD.json`
3. Display the results in the console

Example JSON output structure:
```json
{
  "date": "2024-01-06",
  "papers": [
    {
      "title": "Paper Title",
      "url": "https://huggingface.co/papers/paper-id",
      "authors": ["Author 1", "Author 2"],
      "pdf_url": "https://arxiv.org/pdf/paper-id.pdf",
      "abstract": "Paper abstract...",
      "upvotes": 42
    }
  ]
}
```

## Dependencies

- Python 3.6+
- requests==2.31.0
- beautifulsoup4==4.12.2

## Features

- Date validation
- Error handling for failed requests
- Rate limiting (0.5s delay between requests)
- Automatic JSON file organization

## Contributing

Feel free to:
1. Open issues for bugs or feature requests
2. Submit pull requests with improvements
3. Add documentation or examples

## License

[Your chosen license]

## Acknowledgments

- Thanks to Hugging Face for their daily papers feature
- Built with BeautifulSoup4 for HTML parsing
