from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from config import insert_values
from data_cleaner import clean_job_data

def getJobsByCategory(url: str):
    """
    Scrapes job categories from Merojob.
    """
    lst = []
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    job_link_container = soup.find('div', id='categories')
    if job_link_container:
        list_item = job_link_container.find_all('li', class_='list-item')
        for each_item in tqdm(list_item, desc="Fetching job categories"):
            links = each_item.find('a', href=True)
            if links:
                lst.append(links["href"])
    return lst



def getTotalPages(page_container):
    """
    Finds the total number of pages in a job category.
    """
    total_pages = page_container.find_all('li') if page_container else []
    return max(sum(1 for i in total_pages if i.find('a', class_='page-link')), 1)




def scrape_each_jobs(url: str, page_num: str, page_container, insert_function):
    pagination = getTotalPages(page_container)
    
    for i in range(1, pagination + 1):
        page = requests.get(f'{url}{page_num}{i}')
        soup = BeautifulSoup(page.text, "html.parser")
        job_links = soup.find_all('div', class_='card-body')
        
        for all_card in job_links:
            card = all_card.find('h1', class_='text-primary font-weight-bold media-heading h4')
            if card:
                anchor = card.find('a', href=True)
                if anchor:
                    job_url = "https://merojob.com" + anchor['href']
                    job_data = scrape_job_details(job_url)
                    if job_data:
                        insert_function(job_data)
                        print(f"Stored: {job_data.get('job_title', 'Unknown')}")


def scrape_job_details(job_url):
    """
    Extracts job details from an individual job posting.
    """
    page = requests.get(job_url)
    soup = BeautifulSoup(page.text, "html.parser")

    job_data = {"job_url": job_url}

    # Scrape company information
    card_body = soup.find('div', class_='media-body mt-4')
    if card_body:
        company_name = card_body.find('h2', class_='h5 my-0')
        if company_name:
            name_text = company_name.find('a')
            if name_text:
                job_data["company_name"] = name_text.text.strip()
            else:
                job_data["company_name"] = "Unknown" 

    # Scrape job title
    title_div = soup.find('h1', class_='h4 mb-0 text-primary')
    if title_div:
        job_data["job_title"] = title_div.text.strip()
    else:
        job_data["job_title"] = "Unknown"  

    # Scrape additional job details from tables
    table = soup.find_all('table', class_="table table-hover m-0")
    for rows in table:
        for row in rows.find_all('tr'):
            td = row.find_all('td')
            if len(td) >= 3:
                job_data[td[0].text.strip()] = td[2].text.strip()

    # Clean the scraped data before returning
    cleaned_data = clean_job_data(job_data)
    return cleaned_data if "job_title" in cleaned_data else None


def main_scraper(insert_function):
    """
    Main function to scrape job categories and store job details in PostgreSQL.
    """
    root = "https://merojob.com"
    page_num = "?page="
    
    job_categories = getJobsByCategory(root)
    for each_job in job_categories:
        url = f'{root}{each_job}'
        print(f"Scraping category: {url}")
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        page_container = soup.find('ul', class_='pagination pagination-sm')
        scrape_each_jobs(url, page_num, page_container, insert_function)
