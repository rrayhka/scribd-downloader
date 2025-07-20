#!/usr/bin/env python3
"""
Scribd Link Extractor using Google Search + undetected Chrome (Selenium)
"""

import time
import random
import argparse
import csv
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
ua = UserAgent()
user_agent = ua.random


def extract_scribd_links_from_html(html):
    """
    Extract Scribd links from HTML content.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    links = []
    
    # Method 1: Try to find specific divs with class "MjjYud" first
    try:
        # Use soup.select which is more reliable than find_all
        mjjyud_divs = soup.select('div.MjjYud')
        
        if mjjyud_divs:
            for div in mjjyud_divs:
                try:
                    # Look for anchor tags with class "zReHs" first
                    a_tags = div.select('a.zReHs')  # Using div instead of soup to ensure we're looking within each div
                    
                    # If none found, try to find any anchor tag in the MjjYud divs
                    if not a_tags:
                        a_tags = div.select('a')
                        
                    for a_tag in a_tags:
                        href = a_tag.get('href')
                        if href and 'scribd.com' in href:
                            # Extract title if available
                            title = ""
                            h3_elements = a_tag.select('h3')
                            if h3_elements:
                                title = h3_elements[0].get_text(strip=True)
                            else:
                                # If no h3 tag, use any text in the anchor
                                title = a_tag.get_text(strip=True)
                            
                            links.append({
                                'url': href,
                                'title': title
                            })
                except Exception as e:
                    print(f"Error processing div: {e}")
                    continue
        else:
            print("No divs with class 'MjjYud' found, trying alternative selectors...")
            # Try alternative selectors that might be used by Google
            for selector in ['div.g', 'div.yuRUbf', 'div[data-hveid]']:
                try:
                    alternative_divs = soup.select(selector)
                    if alternative_divs:
                        print(f"Found {len(alternative_divs)} elements using alternative selector: {selector}")
                        for div in alternative_divs:
                            a_tags = div.select('a')
                            for a_tag in a_tags:
                                href = a_tag.get('href')
                                if href and 'scribd.com' in href:
                                    title = ""
                                    # Try to find title in h3 tags
                                    h3_elements = a_tag.select('h3')
                                    if h3_elements:
                                        title = h3_elements[0].get_text(strip=True)
                                    else:
                                        title = a_tag.get_text(strip=True)
                                    
                                    links.append({
                                        'url': href,
                                        'title': title
                                    })
                except Exception as e:
                    print(f"Error using alternative selector {selector}: {e}")
    except Exception as e:
        print(f"Error finding MjjYud divs: {e}")
    
    # Method 2: Fallback to searching all links if we don't find any using method 1
    if not links:
        print("Falling back to general link search")
        try:
            for a in soup.select('a[href]'):
                href = a.get('href')
                if href and 'scribd.com' in href:
                    title = a.get_text(strip=True)
                    links.append({
                        'url': href,
                        'title': title
                    })
        except Exception as e:
            print(f"Error in fallback link search: {e}")
    
    return links


def get_google_search_html(driver, query, start_index):
    """
    Use Selenium with undetected_chromedriver to get Google search results HTML.
    """
    url = f"https://www.google.com/search?q={query}&start={start_index}"
    print(f"Accessing URL: {url}")
    
    try:
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)  # Increased wait time
        
        # Check if the page looks like a Google search results page
        page_source = driver.page_source
        
        # Save the HTML for debugging (always save on first page)
        debug_filename = f"debug_page_{start_index}.html"
        with open(debug_filename, "w", encoding="utf-8") as f:
            f.write(page_source)
        
        search_indicators = ["MjjYud", "search results", "results", "scribd.com"]
        captcha_indicators = ["captcha", "unusual traffic", "robot", "not a robot", "verify"]
        
        # Check if the page appears to be search results
        is_search_results = any(indicator in page_source.lower() for indicator in search_indicators)
        is_captcha = any(indicator in page_source.lower() for indicator in captcha_indicators)
        
        if is_captcha or not is_search_results:
            print(f"WARNING: Search results structure not detected. Google may have shown a captcha.")
            print(f"Saved HTML to {debug_filename} for inspection")
            
            # Allow time to manually solve captcha if in visible mode
            is_headless = any("--headless" in arg for arg in driver.options.arguments if isinstance(arg, str))
            if not is_headless:
                print("You may need to solve a CAPTCHA in the browser.")
                print("Please solve the CAPTCHA manually in the browser window if present.")
                input_time = 30
                print(f"Waiting up to {input_time} seconds. Press Enter when ready or wait for timeout...")
                
                try:
                    # Wait for user input or timeout
                    import msvcrt
                    start_time = time.time()
                    while time.time() - start_time < input_time:
                        if msvcrt.kbhit():
                            msvcrt.getch()  # Clear the input buffer
                            print("Continuing...")
                            break
                        time.sleep(0.1)
                except ImportError:
                    # For non-Windows platforms
                    print(f"Waiting {input_time} seconds to give you time to solve the captcha...")
                    time.sleep(input_time)
                
                # Refresh the page source after captcha might have been solved
                page_source = driver.page_source
        
        return page_source
        
    except Exception as e:
        print(f"Error accessing URL: {e}")
        # Return empty string on failure
        return ""


def main():
    parser = argparse.ArgumentParser(description='Extract Scribd links from Google search results using Selenium')
    parser.add_argument('query', help='Google search query')
    parser.add_argument('--pages', '-p', type=int, default=1, help='Number of search result pages to process')
    parser.add_argument('--start', '-s', type=int, default=0, help='Starting index for search results')
    parser.add_argument('--results-per-page', '-r', type=int, default=10, help='Number of results per page')
    parser.add_argument('--output', '-o', help='Output file to save the links (CSV format)')
    parser.add_argument('--delay-min', type=float, default=3.0, help='Minimum delay between requests in seconds')
    parser.add_argument('--delay-max', type=float, default=7.0, help='Maximum delay between requests in seconds')
    parser.add_argument('--no-headless', action='store_true', help='Run Chrome in visible mode (not headless)')
    parser.add_argument('--chrome-path', help='Path to Chrome executable if it cannot be detected automatically')
    parser.add_argument('--verbose', action='store_true', help='Show detailed debug information including skipped duplicates')
    
    args = parser.parse_args()
    
    # Configure Chrome options
    options = uc.ChromeOptions()
    
    # Set Chrome options properly for undetected_chromedriver
    if not args.no_headless:
        options.add_argument("--headless")  # Use just "--headless" instead of "--headless=new"
        
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Add user agent
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Initialize the driver
    print("Initializing Chrome driver...")
    try:
        driver = uc.Chrome(use_subprocess=True, options=options)
    except TypeError as e:
        print(f"Error initializing Chrome driver: {e}")
        print("Trying alternative method...")
        driver = uc.Chrome(use_subprocess=True)
    
    all_links = []
    seen_urls = set()  # Track unique URLs to prevent duplicates
    duplicate_count = 0  # Counter for duplicates
    
    print(f"Searching for: {args.query}")
    print(f"Processing {args.pages} pages of search results...")
    
    try:
        for page in range(args.pages):
            start_index = args.start + (page * args.results_per_page)
            
            print(f"\nProcessing page {page + 1}/{args.pages} (results {start_index}-{start_index + args.results_per_page - 1})...")
            
            if page > 0:
                # Add a random delay between requests
                delay = random.uniform(args.delay_min, args.delay_max)
                print(f"Waiting {delay:.1f} seconds before next request...")
                time.sleep(delay)
            
            # Get search results HTML
            html_content = get_google_search_html(driver, args.query, start_index)
            
            # Extract links from the current page
            page_links = extract_scribd_links_from_html(html_content)
            
            # Process links and remove duplicates
            new_links = 0
            for link in page_links:
                if link['url'] not in seen_urls:
                    seen_urls.add(link['url'])
                    all_links.append(link)
                    new_links += 1
                else:
                    duplicate_count += 1
                    if args.verbose:
                        print(f"Skipped duplicate URL: {link['url']}")
            
            print(f"Found {len(page_links)} Scribd links on this page, added {new_links} new links, skipped {len(page_links) - new_links} duplicates.")
    finally:
        # Always close the browser
        print("Closing Chrome browser...")
        driver.quit()
    
    # Print summary of all links found
    if not all_links:
        print("\nNo Scribd links found across all pages.")
        return
    
    print(f"\nFound a total of {len(all_links)} unique Scribd links (skipped {duplicate_count} duplicates):")
    for i, link in enumerate(all_links, 1):
        print(f"{i}. {link['title']}")
        print(f"   {link['url']}")
        print()
    
    # Save to file if specified
    if args.output:
        output_format = args.output.lower().split('.')[-1]
        
        if output_format == 'csv':
            with open(args.output, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Title', 'URL'])
                for link in all_links:
                    writer.writerow([link['title'], link['url']])
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                for link in all_links:
                    f.write(f"{link['url']},{link['title']}\n")
                    
        print(f"Links saved to {args.output}")


if __name__ == "__main__":
    main()
    
