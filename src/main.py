import logging
import re
import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        name='li',
        attrs={'class': 'toctree-l1'}
    )
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        h1_text = h1.text.replace(chr(182), '')  # Убирает ¶
        dl_text = dl.text.replace('\n', ' ')
        result.append(
            (version_link, h1_text, dl_text)
        )
    return result


def latest_versions(session):
    result = [('Ссылка на документацию', 'Версия', 'Статус')]
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All version' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось.')
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        link = a_tag['href']
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        result.append(
            (link, version, status)
        )
    return result


def pep(session):
    result = [('Статус', 'Количество')]
    response = get_response(session, PEP_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    step_two = find_tag(soup, 'section', attrs={'id': 'index-by-category'})
    step_three = step_two.find_all('tr')
    for step in tqdm(step_three):
        version_a_tag = step.find('a')
        if version_a_tag is None:
            continue
        status1 = find_tag(step, 'abbr')
        status_fin = status1['title'].split(', ')
        href = version_a_tag['href']
        version_link = urljoin(PEP_URL, href)
        response = get_response(session, version_link)
        soup = BeautifulSoup(response.text, 'lxml')
        status_fin2 = find_tag(soup, 'abbr').text
        EXPECTED_STATUS[status_fin[1]] = EXPECTED_STATUS.get(status_fin[1], 0) + 1
        if status_fin[1] != status_fin2:
            logging.info(
                f'Несовпадающие статусы: {version_link} '
                f'статус в карторчке: {status_fin2} '
                f'Ожидаемый статус: {status_fin[1]} '
            )
    for key, value in EXPECTED_STATUS.items():
        result.append([key, EXPECTED_STATUS[key]])
        if key == 'Draft':
            result.append(['Total', sum(EXPECTED_STATUS.values())])
    return result


def download(session):
    """Функция загрузки документации в zip файл."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', attrs={'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a', attrs={'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
