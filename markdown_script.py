#!/usr/bin/env python3
"""
Web Page to Markdown Downloader

This script downloads a webpage and converts it to markdown format.
Requires: requests, beautifulsoup4, html2text

Install dependencies:
pip install requests beautifulsoup4 html2text
"""

import requests
import html2text
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urlparse, urljoin
import sys
import argparse
from email.utils import formatdate

def clean_filename(url):
    """Generate a clean filename from URL"""
    parsed = urlparse(url)
    # Use domain + path, replace invalid characters
    filename = f"{parsed.netloc}{parsed.path}"
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    filename = re.sub(r'_+', '_', filename)  # Replace multiple underscores
    filename = filename.strip('_')
    
    if not filename or filename == '':
        filename = 'webpage'
    
    return f"{filename}.md"


def download_and_convert(url, output_file=None, include_links=True, body_only=True):
    print("proceeding to download and convert")
    """
    Download webpage and convert to markdown
    
    Args:
        url: URL to download
        output_file: Output filename (optional)
        include_links: Whether to preserve links
        body_only: Extract only main content (removes nav, footer, etc.)
    """
    try:
        # Download the webpage
        print(f"Downloading: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        # soup contains all the html content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()
        
        # Extract main content if body_only is True
        if body_only:
            # Try to find main content area
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_=re.compile(r'content|main|article', re.I)) or
                soup.find('div', id=re.compile(r'content|main|article', re.I)) or
                soup.body
            )
            if main_content:
                html_content = str(main_content)
            else:
                html_content = str(soup)
        else:
            html_content = str(soup)
        
        # Configure html2text
        h = html2text.HTML2Text()
        h.ignore_links = not include_links
        h.ignore_images = False
        h.body_width = 0  # Don't wrap lines
        h.protect_links = True
        h.wrap_links = False
        
        # Convert to markdown
        markdown_content = h.handle(html_content)
        
        # Clean up the markdown
        markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)  # Remove excessive newlines
        markdown_content = markdown_content.strip()
        
        # Add title and metadata
        title = soup.title.string if soup.title else "Webpage"
        header = f"# {title.strip()}\n\n**Source:** {url}\n**Downloaded:** {formatdate()}\n\n---\n\n"
        markdown_content = header + markdown_content
        
        # Determine output filename
        if not output_file:
            output_file = clean_filename(url)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Successfully converted and saved to: {output_file}")
        print(f"File size: {len(markdown_content)} characters")
        
        return output_file
        
    except requests.RequestException as e:
        print(f"Error downloading webpage: {e}")
        return None
    except Exception as e:
        print(f"Error converting to markdown: {e}")
        return None
    
def validate_url(url):
    """Basic URL validation"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def main():
    print("Reaches main method")

    # method call for retrieving the pitchfork urls | return list of urls

    # method call for retrieving the alexnet articles | return list of urls

    parser = argparse.ArgumentParser(description='Download webpage and convert to markdown')
    parser.add_argument('-urls', help='Additional URLs to download', nargs='*', required=True)
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('--no-links', action='store_true', help='Remove links from output')
    parser.add_argument('--full-page', action='store_true', help='Include full page (not just main content)')
    
    args = parser.parse_args()

    result = None

    print("Reaches main method")
    print(f"args.urls: {args.urls}")
    
    # only runs if the user specifies the --urls flag
    if args.urls:
        for url in args.urls:
            print(url)
            url = validate_url(url)
            print(f"validated url: {url}")
            download_and_convert(
                url, 
                include_links=not args.no_links,
                body_only=not args.full_page
            )
    
        # Download and convert
        result = download_and_convert(
            url, 
            args.output, 
            include_links=not args.no_links,
            body_only=not args.full_page
        )
        
    if result:
        print(f"\n✓ Conversion complete: {result}")
    else:
        print("\n✗ Conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    # Example usage if run without arguments
    if len(sys.argv) == 1:
        print("Usage examples:")
        print("python webpage_to_markdown.py https://example.com")
        print("python webpage_to_markdown.py https://example.com -o my_file.md")
        print("python webpage_to_markdown.py https://example.com --no-links")
        print("python webpage_to_markdown.py https://example.com --full-page")
        sys.exit(1)
    
    main()