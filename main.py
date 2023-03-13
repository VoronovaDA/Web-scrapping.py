import requests
import json
from bs4 import BeautifulSoup
from fake_headers import Headers




url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'


company_list = []
salary_list = []
sorted_list = []
local_list = []
info_list = []


def get_headers():
    return Headers(browser="firefox", os="win").generate()


def get_search_links():
    character_list = []
    links_list = []
    response = requests.get(url, headers=get_headers())
    search_soup = BeautifulSoup(response.text, 'html.parser')
    vacancies = search_soup.find_all('a', class_='serp-item__title')
    for vacancy in vacancies:
        links = vacancy['href']
        links_list.append(links)
        response_links = requests.get(links, headers=get_headers())
        links_soup = BeautifulSoup(response_links.text, 'html.parser')
        desc = links_soup.find('div', {'data-qa': 'vacancy-description'})
        if not desc:
            continue
        if ('Django' or 'django' or 'Flask' or 'flask') in desc.text:
            character_list.append('+')
        else:
            character_list.append('-')
    for x, y in zip(links_list, character_list):
        if y == "+":
            sorted_list.append(x)
    return sorted_list


def get_salary():
    for link in sorted_list:
        salary_link = requests.get(link, headers=get_headers())
        salary_soup = BeautifulSoup(salary_link.text, 'html.parser')
        salary = salary_soup.find('span', class_="bloko-header-section-2 bloko-header-section-2_lite")
        if not salary:
            continue
        salary_text = salary.text
        salary_list.append(salary_text)
    return salary_list


def get_company():
    for link in sorted_list:
        company_link = requests.get(link, headers=get_headers())
        company_soup = BeautifulSoup(company_link.text, 'html.parser')
        company_name_ = company_soup.find('a', class_="bloko-link bloko-link_kind-tertiary")
        if not company_name_:
            continue
        company_name = company_name_['href']
        company_href = f'https://spb.hh.ru{company_name}'
        company_link2 = requests.get(company_href, headers=get_headers())
        company_soup2 = BeautifulSoup(company_link2.text, 'html.parser')
        company_name2 = company_soup2.find('span', class_="company-header-title-name")
        if not company_name2:
            continue
        company_text = company_name2.text
        company_list.append(company_text)
    return company_list


def get_local():
    for link in sorted_list:
        local_link = requests.get(link, headers=get_headers())
        local_soup = BeautifulSoup(local_link.text, 'html.parser')
        local_ = local_soup.find('div', {'data-qa': 'vacancy-serp__vacancy-address'})
        if not local_:
            continue
        local_text = local_.text
        local_list.append(local_text)
    return local_list


def get_info_json(links_, salary, company, locals):
    total_info = zip(links_, salary, company, locals)
    for link, salary, company_name, location in total_info:
        info_dict = {'link': link,
                     'salary': salary,
                     'company_name': company_name,
                     'location': location}
        info_list.append(info_dict)
    return info_list


if __name__ == '__main__':

    get_search_links()
    get_salary()
    get_company()
    get_local()
    get_info_json(sorted_list, salary_list, company_list, local_list)

    with open('vacancy_info_hh.json', 'w', encoding='utf-8') as f:
        json.dump(info_list, f, indent=2, ensure_ascii=False)
