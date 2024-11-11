# Hugging Face Daily Papers Scraper

A Python script to scrape and collect papers from [Hugging Face's Daily Papers](https://huggingface.co/papers) page. The scraper extracts comprehensive information about each paper, downloads PDFs, and organizes them by date.

## Features

- Scrape papers for a single date or date range
- Extract detailed paper information:
  - Title
  - Landing page URL
  - Complete list of authors
  - PDF link (arxiv)
  - Full abstract
  - Upvote count
- Automatic PDF downloads
- Organized file structure
- Progress tracking for downloads
- Rate limiting to be server-friendly
- Command-line interface with date parameters

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

### Basic Usage (Today's Papers)
Run the script without parameters to scrape today's papers:
```bash
python hf_paper_scraper.py
```

### Single Date
Use the `--start-date` parameter to scrape papers from a specific date:
```bash
python hf_paper_scraper.py --start-date 2024-01-06
```

### Date Range
Use both `--start-date` and `--end-date` to scrape papers from a range of dates:
```bash
python hf_paper_scraper.py --start-date 2024-01-01 --end-date 2024-01-06
```

### Output Structure
The script creates an organized directory structure:
```
papers/
├── YYYY-MM-DD.json         # Paper metadata for each date
├── YYYY-MM-DD/            # PDF files for each date
│   ├── paper1.pdf
│   ├── paper2.pdf
│   └── ...
├── next-date.json
└── next-date/
    └── ...
```

### JSON Format
Each date's JSON file contains:
```json
{
  "date": "YYYY-MM-DD",
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

- Date validation and range support
- Error handling for failed requests
- Rate limiting (0.5s between requests)
- Progress tracking:
  - Overall date progress
  - Per-date PDF download progress
  - Success/failure indicators
- Automatic file organization
- PDF downloads with clean filenames

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
