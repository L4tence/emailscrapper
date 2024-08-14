import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from colorama import Fore, Style, init
from collections import deque

init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_logs_directory():
    if not os.path.exists('logs'):
        os.makedirs('logs')

def get_filename_for_domain(domain):
    domain_filename = domain.replace('https://', '').replace('http://', '').replace('/', '_')
    return os.path.join('logs', f"{domain_filename}.txt")

def count_emails_in_file(filename):
    try:
        with open(filename, 'r') as file:
            emails = file.readlines()
            return len(emails)
    except FileNotFoundError:
        return 0

def update_domains_file(domains):
    with open('domains_to_scrape.txt', 'w') as f:
        for domain in domains:
            f.write(f"{domain}\n")

def load_domains_from_file():
    if os.path.exists('domains_to_scrape.txt'):
        with open('domains_to_scrape.txt', 'r') as f:
            domains = [line.strip() for line in f.readlines()]
            return deque(domains)
    return deque()

def is_government_url(url):
    return '.gouv' in url

def scrape_page(session, url, found_emails_list, email_suffix, existing_emails_list, visited_urls, domains_to_explore):
    found_emails = set(found_emails_list)
    existing_emails = set(existing_emails_list)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = session.get(url, headers=headers)
        response.raise_for_status()

        if 'text/html' not in response.headers['Content-Type']:
            raise ValueError("Le site n'est pas en HTML")

        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text()

        targeted_emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:com|fr)\b', page_text))

        if email_suffix:
            targeted_emails = {email for email in targeted_emails if email_suffix in email}

        new_emails = targeted_emails - existing_emails
        found_emails.update(new_emails)

        domain = urlparse(url).netloc
        filename = get_filename_for_domain(domain)
        with open(filename, 'a') as file:
            for email in new_emails:
                file.write(f"{email}\n")

        existing_emails.update(targeted_emails)
        visited_urls.add(url)

        links = [urljoin(url, link['href']) for link in soup.find_all('a', href=True)]
        for link in links:
            parsed_link = urlparse(link)
            if parsed_link.netloc and parsed_link.netloc != domain and not is_government_url(parsed_link.netloc):
                if parsed_link.netloc not in visited_urls and parsed_link.netloc not in domains_to_explore:
                    domains_to_explore.append(parsed_link.netloc)
                    update_domains_file(domains_to_explore)

        found_emails_list[:] = list(found_emails)
        existing_emails_list[:] = list(existing_emails)

        return len(new_emails), url

    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête: {e}")
        return 0, url
    except ValueError as ve:
        print(f"Erreur : {ve}")
        return 0, url
    except Exception as ex:
        print(f"Une erreur inattendue s'est produite: {ex}")
        return 0, url

def get_all_links(session, url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = session.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [
            urljoin(url, link['href'])
            for link in soup.find_all('a', href=True) if urlparse(
                urljoin(url, link['href'])).netloc == urlparse(url).netloc
        ]
        return links
    except requests.exceptions.RequestException as e:
        print(f"Erreur de requête: {e}")
        return []

def explore_all_pages(session, base_url, found_emails_list, email_suffix, existing_emails_list, visited_urls, domains_to_explore):
    try:
        page_count = 0
        links_to_explore = deque(get_all_links(session, base_url))

        while links_to_explore:
            link = links_to_explore.popleft()
            if link not in visited_urls:
                page_count += 1
                count, url = scrape_page(session, link, found_emails_list, email_suffix, existing_emails_list, visited_urls, domains_to_explore)
                domain = urlparse(link).netloc
                total_emails = count_emails_in_file(get_filename_for_domain(domain))
                print(f"Page [{page_count}] ({Fore.MAGENTA}{link}{Style.RESET_ALL}): [{count}] emails trouvés, Total: [{total_emails}] emails")

                links_to_explore.extend(get_all_links(session, link))

    except Exception as ex:
        print(f"Une erreur est survenue lors de l'exploration de la page: {ex}")

def scrape_emails(start_url, email_suffix):
    create_logs_directory()
    found_emails_list = []
    existing_emails_list = []
    visited_urls = set()
    domains_to_explore = load_domains_from_file()
    start_domain = urlparse(start_url).netloc

    if start_domain not in domains_to_explore and not is_government_url(start_domain):
        domains_to_explore.append(start_domain)
        update_domains_file(domains_to_explore)

    with requests.Session() as session:
        while domains_to_explore:
            current_domain = domains_to_explore.popleft()
            update_domains_file(domains_to_explore)
            base_url = f"https://{current_domain}"

            try:
                explore_all_pages(session, base_url, found_emails_list, email_suffix, existing_emails_list, visited_urls, domains_to_explore)
            except Exception as e:
                print(f"Erreur lors de l'exploration du domaine {current_domain}: {e}")
            finally:
                if current_domain in domains_to_explore:
                    domains_to_explore.remove(current_domain)
                update_domains_file(domains_to_explore)

    if found_emails_list:
        print("Les emails ont été sauvegardés en temps réel dans les fichiers logs.")
    else:
        print("Aucune adresse email n'a été trouvée.")

def main():
    clear_screen()
    print(rf"""
    {Fore.MAGENTA}

  _____                 _ _ ____                                       
 | ____|_ __ ___   __ _(_) / ___|  ___ _ __ __ _ _ __  _ __   ___ _ __ 
 |  _| | '_ ` _ \ / _` | | \___ \ / __| '__/ _` | '_ \| '_ \ / _ \ '__|
 | |___| | | | | | (_| | | |___) | (__| | | (_| | |_) | |_) |  __/ |   
 |_____|_| |_| |_|\__,_|_|_|____/ \___|_|  \__,_| .__/| .__/ \___|_|   
                                                |_|   |_|                      
                        -by l4tence-           

    """)

    while True:
        base_url = input("Entrez le nom de domaine du site à scraper (ex: https://www.example.com): ").rstrip('/')
        email_suffix_input = input("Entrez le suffixe des emails recherchés (ex: @gmail.com) ou 'all' pour tous les suffixes: ")

        if email_suffix_input.lower() == 'all':
            email_suffix = ''
        else:
            email_suffix = email_suffix_input

        scrape_emails(base_url, email_suffix)

        action = input(f"Appuyez sur Entrée pour effectuer une autre recherche, ou tapez 'quitter' pour quitter.")
        if action.lower() == 'quitter':
            break

        clear_screen()
        print(rf"""
        {Fore.MAGENTA}
  _____                 _ _ ____                                       
 | ____|_ __ ___   __ _(_) / ___|  ___ _ __ __ _ _ __  _ __   ___ _ __ 
 |  _| | '_ ` _ \ / _` | | \___ \ / __| '__/ _` | '_ \| '_ \ / _ \ '__|
 | |___| | | | | | (_| | | |___) | (__| | | (_| | |_) | |_) |  __/ |   
 |_____|_| |_| |_|\__,_|_|_|____/ \___|_|  \__,_| .__/| .__/ \___|_|   
                                                |_|   |_|                      
                        -by l4tence-            

    """)

if __name__ == "__main__":
    main()
