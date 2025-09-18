
import requests
from bs4 import BeautifulSoup, NavigableString # Ensure NavigableString is imported
from urllib.parse import urljoin, urlparse
import json
import os

# Global set to keep track of visited URLs during a crawl session
visited_urls = set()

# ✨ Clean and extract visible text, now with link augmentation
def clean_text_with_links(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Remove script, style, and common non-content tags
    tags_to_remove = ["script", "style", "nav", "footer", "header", "aside", 
                      "form", "button", "input", "textarea", "select", "option",
                      "noscript", "iframe", "canvas", "svg", "video", "audio"]
    for tag_name in tags_to_remove:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    
    # 2. Augment specific <a> tags to include their hrefs in the textual content
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "")
        link_type_label = None
        is_contact_link = False

        if not href: # Skip if href is empty or None
            continue

        if "wa.me/" in href or "api.whatsapp.com/send" in href:
            link_type_label = "WhatsApp"
            is_contact_link = True
        elif href.startswith("skype:"):
            link_type_label = "Skype"
            is_contact_link = True
        elif href.startswith("mailto:"):
            link_type_label = "Email"
            is_contact_link = True
        elif href.startswith("tel:"):
            link_type_label = "Phone"
            is_contact_link = True
        # Add other types if needed (e.g., Telegram, LinkedIn)

        if is_contact_link:
            link_info_str = f" ({link_type_label} Link: {href})"

            # Avoid adding if link info is already part of the text (basic check)
            if href in a_tag.get_text(separator=" ", strip=True): 
                continue

            # Attempt to modify specific known structures (e.g., Elementor's text span)
            text_span = a_tag.find("span", class_="elementor-icon-list-text")
            if text_span and text_span.string: 
                current_text = text_span.string.strip()
                text_span.string.replace_with(f"{current_text}{link_info_str}")
            elif a_tag.string and a_tag.string.strip() and not a_tag.find_all(True, recursive=False):
                # Case: <a>Direct text here</a> (no child tags)
                current_text = a_tag.string.strip()
                a_tag.string.replace_with(f"{current_text}{link_info_str}")
            else:
                # Case: <a><span>Text</span><i class="icon"></i></a> or image links etc.
                # Append the link information as a new NavigableString child.
                a_tag.append(NavigableString(link_info_str))

    # 3. Extract all text content from the (potentially modified) soup
    text_parts = [text for text in soup.stripped_strings]
    cleaned_text = " ".join(text_parts)
    
    return cleaned_text

def is_valid_url(url, base_domain):
    parsed_url = urlparse(url)
    
    if parsed_url.scheme not in ['http', 'https']:
        return False
    
    common_file_extensions = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', 
        '.zip', '.tar', '.gz', '.rar',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv',
        '.xml', '.rss', '.css', '.js', '.json', '.txt'
    ]
    if any(parsed_url.path.lower().endswith(ext) for ext in common_file_extensions):
        return False
        
    if base_domain not in parsed_url.netloc: # Allows subdomains of base_domain
        return False
        
    url_without_fragment = urljoin(url, parsed_url.path + (';' + parsed_url.params if parsed_url.params else '') + ('?' + parsed_url.query if parsed_url.query else ''))
    if url_without_fragment in visited_urls:
        return False
        
    return True


def scrape_website(start_url, max_depth=2):
    global visited_urls
    visited_urls.clear() 

    base_domain = urlparse(start_url).netloc
    to_visit_queue = [(start_url, 0)] 
    scraped_data_list = []
    
    # Keep track of URLs added to queue to avoid redundant processing, normalized without fragment
    processed_urls_in_queue = set()
    start_url_parsed = urlparse(start_url)
    start_url_normalized = urljoin(start_url, start_url_parsed.path + (';' + start_url_parsed.params if start_url_parsed.params else '') + ('?' + start_url_parsed.query if start_url_parsed.query else ''))
    processed_urls_in_queue.add(start_url_normalized)


    while to_visit_queue:
        current_url, current_depth = to_visit_queue.pop() # DFS

        parsed_current_url = urlparse(current_url)
        current_url_normalized_for_visited = urljoin(current_url, parsed_current_url.path + (';' + parsed_current_url.params if parsed_current_url.params else '') + ('?' + parsed_current_url.query if parsed_current_url.query else ''))

        if current_url_normalized_for_visited in visited_urls:
             continue
        
        if current_depth > max_depth:
            continue

        print(f"Scraping: {current_url} (Depth: {current_depth})")
        visited_urls.add(current_url_normalized_for_visited)

        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(current_url, timeout=15, headers=headers)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                print(f"Skipping non-HTML content at {current_url} (Content-Type: {content_type})")
                continue
            
            html_to_parse = response.text

        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch or access {current_url}: {e}")
            continue
        
        cleaned_page_content = clean_text_with_links(html_to_parse)

        if cleaned_page_content:
            scraped_data_list.append({
                "url": current_url,
                "content": cleaned_page_content
            })

        if current_depth < max_depth:
            soup_for_links = BeautifulSoup(html_to_parse, "html.parser")
            for link_tag in soup_for_links.find_all("a", href=True):
                raw_href = link_tag.get("href")
                if not raw_href: continue

                absolute_href = urljoin(current_url, raw_href)
                
                # Check validity (includes domain, scheme, not file, not visited)
                # is_valid_url itself checks visited_urls, so redundant check for `current_url_normalized_for_visited in visited_urls` above might be removed if strictly relying on is_valid_url
                if is_valid_url(absolute_href, base_domain):
                    parsed_abs_href = urlparse(absolute_href)
                    normalized_abs_href_for_queue = urljoin(absolute_href, parsed_abs_href.path + (';' + parsed_abs_href.params if parsed_abs_href.params else '') + ('?' + parsed_abs_href.query if parsed_abs_href.query else ''))

                    if normalized_abs_href_for_queue not in processed_urls_in_queue:
                        to_visit_queue.append((absolute_href, current_depth + 1))
                        processed_urls_in_queue.add(normalized_abs_href_for_queue)
    
    output_dir = "backend/data"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "scraped_data.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scraped_data_list, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(scraped_data_list)} pages. Data saved to {output_path}")
    return scraped_data_list


if __name__ == "__main__":
    # To test with the specific "About Us" page:
    # target_url = "https://assorttech.com/about-us/"
    # print(f"Starting scrape for: {target_url}")
    # scrape_website(target_url, max_depth=0) # max_depth=0 will only scrape the start_url

    # To scrape the entire site (or up to a certain depth):
    # main_site_url = "https://assorttech.com/"
    main_site_url = "https://madigitalhub.com/"
    print(f"Starting scrape for: {main_site_url}")
    scrape_website(main_site_url, max_depth=1) # Adjust max_depth as needed, e.g., 1 or 
    


    