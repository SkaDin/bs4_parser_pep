# Проект парсинг

## Описание проекта:
###  Проект работающий в разных режимах, с подключённым  логированием и обработкой ошибок, помогающий быть в курсе новостей в мире Python. Он выполняет 4 основных функции:

 1. Собирает ссылки на статьи о нововведениях в Python, переходит по ним и забирает информацию об авторах и редакторах статей.
 2. Собирает информацию о статусах версий Python.
 3. Скачивает архив с актуальной документацией.
 4. Парсит данные обо всех документах PEP:
     * Cохраняет результат в табличном виде в csv-файл
     * Выводит таблицу с 3-мя колонками «Статус», «Количество» и «Total»(общим количеством PEP)

## Используемые технологии:
### * Python
### * BeautifulSoup4 - библиотека для парсинга.
### * Prettytable - библиотека для отображения табличных данных.

## Инструкция по развёртыванию проекта:
1. Клонировать репозиторий и перейти в него в командной строке:
```
git@github.com:SkaDin/bs4_parser_pep.git
```
```
cd bs4_parser_pep
```
2.Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
   1.При необходимости обновить pip
    ```
    python3 -m pip install --upgrade pip
    ```

## Примеры команд:
* Вывод ссылок o нововведениях в Python:
```
python main.py whats-new
```
* Создание csv файла с таблицей:
```
python main.py pep -o file
```
* Создание таблицы о статусах версий:
```
python main.py latest-versions -o pretty
```
### Для более детального ознакомления с командами необходимо сделать следующее:
```
python main.py -h
```
## Автор проекта: SkaDin(Сушков Денис)

