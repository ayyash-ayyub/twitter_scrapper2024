import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to scrape full article content from detail page
def scrape_full_article(url, content_tag_selector):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    content_tag = soup.select_one(content_tag_selector)
    if content_tag:
        paragraphs = content_tag.find_all('p')
        full_content = ' '.join([para.get_text(separator=' ').strip() for para in paragraphs])
    else:
        full_content = 'No content'

    return full_content

# Function to dynamically detect title, link, and date from a page
def scrape_page(url, site_config):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []

    # Dynamically detect articles based on the site's configuration
    for article in soup.select(site_config['article_selector']):
        # Scrape title
        title_tag = article.select_one(site_config['title_selector'])
        title = title_tag.text.strip() if title_tag else 'No title'

        if title_tag and title_tag.name != 'a':            
            detail_link_tag = title_tag.find('a')
        else:            
            detail_link_tag = title_tag

        # Scrape article detail page link
        detail_link = detail_link_tag['href'] if detail_link_tag else None

        if detail_link and not detail_link.startswith('http'):
            detail_link = f"{site_config['base_url']}{detail_link}"

        # Scrape date if date_selector is provided
        date_tag = article.select_one(site_config['date_selector'])
        date = date_tag.text.strip() if date_tag else 'No date'

        # print("Date Tag: ", date_tag, "date: ", date)

        if detail_link:
            full_content = scrape_full_article(detail_link, site_config['content_selector'])
        else:
            full_content = 'No content'

        articles.append({
            'title': title,
            'content': full_content,
            'date': date
        })

    return articles


# Function to handle pagination and scrape all pages
def scrape_website(pagination_url, site_config, max_articles=3):
    page = 1
    all_articles = []
    
    while len(all_articles) < max_articles:
        url = pagination_url.format(page=page)
        print(f"Scraping page {page}: {url}")
    
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Page {page} not found (status code {response.status_code}). Stopping pagination.")
            break 

        articles = scrape_page(url, site_config)
        
        if not articles:
            break
        
        all_articles.extend(articles)
        
        if len(all_articles) > max_articles:
            all_articles = all_articles[:max_articles]
            break
        
        page += 1

    return all_articles


# Define configurations for different websites
site_configs = {
    'darkreading': {
        'base_url': 'https://www.darkreading.com',
        'pagination_url': 'https://www.darkreading.com/latest-news?page={page}',
        'article_selector': 'div.ListPreview-ContentWrapper', 
        'title_selector': 'a.ListPreview-Title', 
        'date_selector': 'span.ListPreview-Date', 
        'content_selector': 'div.ContentModule-Wrapper' 
    },

    'darkreading_threat_intelligence': {
        'base_url': 'https://www.darkreading.com',
        'pagination_url': 'https://www.darkreading.com/threat-intelligence?page={page}',
        'article_selector': 'div.ListPreview-ContentWrapper', 
        'title_selector': 'a.ListPreview-Title', 
        'date_selector': 'span.ListPreview-Date', 
        'content_selector': 'div.ContentModule-Wrapper' 
    },
    'darkreading_cyberattacks_data_breaches': {
        'base_url': 'https://www.darkreading.com',
        'pagination_url': 'https://www.darkreading.com/cyberattacks-data-breaches?page={page}',
        'article_selector': 'div.ListPreview-ContentWrapper', 
        'title_selector': 'a.ListPreview-Title', 
        'date_selector': 'span.ListPreview-Date', 
        'content_selector': 'div.ContentModule-Wrapper' 
    },



    
    'krebsonsecurity': {
        'base_url': 'https://krebsonsecurity.com',
        'pagination_url': 'https://krebsonsecurity.com/page/{page}/?s=security',
        'article_selector': 'article', 
        'title_selector': 'h2.entry-title', 
        'date_selector': 'div.adt', 
        'content_selector': 'div.entry-content' 
    },



}

selected_site = 'krebsonsecurity'

site_config = site_configs[selected_site]
articles = scrape_website(site_config['pagination_url'], site_config, max_articles=5)

df = pd.DataFrame(articles)
df.to_excel(f'{selected_site}_scraped_data_full_content.xlsx', index=False)


print(f"Data successfully scraped and exported to {selected_site}_scraped_data_full_content.xlsx")