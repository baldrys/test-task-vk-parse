import requests
from bs4 import BeautifulSoup
import json
import csv

HOST = "https://vk.com"
URL = "https://vk.com/@yvkurse"
HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
}

CSV = "../vkArticles.csv"


def getHtml(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def getArticlesLinks(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    mainArticle = soup.find_all(
        'div', class_='_author_page_block_main_article')
    articles = mainArticle + \
        soup.find_all('div', class_='_author_page_published_item')
    articlesLinks = []
    for article in articles:
        a = article.find('a', href=True)
        articlesLinks.append(HOST + a['href'])
    return articlesLinks


def getArticleContent(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    title = soup.find('h1').get_text(strip=True)
    content = soup.find(
        'div', class_='article article_view').get_text(strip=True)
    imagesList = [getHighestImgResolution(img.attrs.get("data-sizes", None))
                  for img in soup.find_all('div', class_='article_object_sizer_wrap')]
    images = ', '.join([str(image) for image in imagesList])
    return {
        "title": title,
        "content": content,
        "images": images
    }


def getArticlesContent(articlesLinks):
    articlesContent = []
    for articleLink in articlesLinks:
        print("Парсим статью {}".format(articleLink))
        articleHtml = getHtml(articleLink)
        if articleHtml.status_code == 200:
            articleContent = getArticleContent(articleHtml)
            articlesContent.append(
                articleContent
            )
    print("Все спаршено!")
    return articlesContent


def getHighestImgResolution(img):
    parsedJson = json.loads(img)
    key = [*parsedJson[0].keys()][-1]
    return parsedJson[0][key][0]


def parse():
    html = getHtml(URL)
    if html.status_code == 200:
        articlesLinks = getArticlesLinks(html)
        print("Всего статей: {}".format(len(articlesLinks)))
        articles = getArticlesContent(articlesLinks)
        saveContent(articles, CSV)
    return None


def saveContent(articles, path):
    with open(path, 'w', newline='', encoding="utf8") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(['Название', 'Текст', 'Картинки'])
        for article in articles:
            writer.writerow(
                [article['title'], article['content'], article['images']])


parse()
