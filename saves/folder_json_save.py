import os
import re
import json
from collections import defaultdict, Counter
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from index_generate import generate_index

# Ссылки
# Исходный BASE_URL
BASE_URL = "https://chrysanthemumgarden.com/novel-tl/tire/"

# Извлекаем последнюю часть BASE_URL (после последнего '/')
last_part = BASE_URL.rstrip('/').split('/')[-1]  # Результат: "tire"

# Формируем FIRST_CHAPTER_URL
FIRST_CHAPTER_URL = f"{BASE_URL}{last_part}-1/"

# Формируем SITE_DIR
SITE_DIR = f"site/Blizarus.github.io/novels/{last_part}"

os.makedirs(os.path.join(SITE_DIR, "chapters"), exist_ok=True)

# Функция для извлечения данных о новелле с главной страницы
def fetch_novel_info(url):
    req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')

    novel_info_block = soup.find('div', class_='novel-info')
    novel_title = novel_info_block.find('h1', class_='novel-title').text.strip()
    novel_raw_title = novel_info_block.find('span', class_='novel-raw-title').text.strip()
    author = novel_info_block.find(string=re.compile(r'Author:')).strip().replace('Author: ', '')
    total_chapters = novel_info_block.find(string=re.compile(r'Total Chapters:')).strip().replace('Total Chapters: ', '')

    synopsis_block = soup.find('div', class_='entry-content')
    synopsis = '\n'.join([p.text.strip() for p in synopsis_block.find_all('p')])

    return {
        "title": novel_title,
        "raw_title": novel_raw_title,
        "author": author,
        "total_chapters": total_chapters,
        "description": synopsis,
        "chapters": []
    }

# Функция для извлечения данных о главах с первой главы
def fetch_chapters(url):
    req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')

    chapter_select = soup.find("select", class_="toc browser-default")
    chapters = [
        (option.text.strip(), option["value"])
        for option in chapter_select.find_all("option")
    ]

    return chapters

# Извлечение данных о новелле
novel_info = fetch_novel_info(BASE_URL)

# Извлечение данных о главах
chapters = fetch_chapters(FIRST_CHAPTER_URL)
chapter_titles = [chapter[0] for chapter in chapters]

# Функция для очистки имени файла
def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# Функция для расшифровки текста
def decrypt_text(text, mapping):
    return ''.join(mapping.get(char, char) for char in text)

# Cipher and original texts for mapping
cipher_texts = [
    "Vtfc Bbcu fsfygbkr oeggbkfv: Qtja?",
    "Vtfc Bbcu lcafggeqafv: Rb ibcufg qgbnlvf afwqbgjgs lvfcalalfr?",
    "Ktf rsrafw gfqilfv: Ktf gfmalolfg&r wfcaji ybvs klii ibrf lar reqqbga. Cr atf ibk-vlwfcrlbcji kbgivr mjii la, sbe klii vlf.",
    "Vtfc Bbcu jrxfv mjiwis:",
    "Ktfc ktja gfkjgv klii P ufa?"
]
original_texts = [
    "Shen Kong eyebrows furrowed: What?",
    "Shen Kong interrupted: No longer provide temporary identities?",
    "The system replied: The rectifier's mental body will lose its support. As the low-dimensional worlds call it, you will die.",
    "Shen Kong asked calmly:",
    "Then what reward will I get?"
]

mapping = defaultdict(Counter)
for cipher, original in zip(cipher_texts, original_texts):
    for c_char, o_char in zip(cipher, original):
        mapping[c_char][o_char] += 1
final_mapping = {char: count.most_common(1)[0][0] for char, count in mapping.items()}

unwanted_sentence_pattern = r"([^.]*chrysanthemumgarden \(dot\) com[^.]*\.)|([^.]*Chrysanthemum Garden[^.]*\.)"

# Обработка глав
for i, (chapter_title, chapter_url) in enumerate(chapters):
    print(f"Fetching: {chapter_title}")
    chapter_req = Request(url=chapter_url, headers={'User-Agent': 'Mozilla/5.0'})
    chapter_webpage = urlopen(chapter_req).read()
    chapter_soup = BeautifulSoup(chapter_webpage, 'html.parser')
    content = chapter_soup.find("div", class_="entry-content")

    for span in content.find_all('span', style=lambda x: x and 'height:1px;width:0' in x):
        span.decompose()

    sanitized_chapter_title = sanitize_filename(chapter_title)
    prev_chapter = sanitize_filename(chapter_titles[i-1]) if i > 0 else None
    next_chapter = sanitize_filename(chapter_titles[i+1]) if i < len(chapters) - 1 else None

    paragraphs = content.find_all('p')
    chapter_content = []

    for para in paragraphs:
        para_text = para.get_text()

        para_text = re.sub(unwanted_sentence_pattern, '', para_text)

        jum_elements = para.find_all('span', class_='jum')
        for jum in jum_elements:
            encrypted_text = jum.get_text()
            decrypted_text = decrypt_text(encrypted_text, final_mapping)
            para_text = para_text.replace(encrypted_text, decrypted_text)

        chapter_content.append(para_text)

    chapter_data = {
        "title": chapter_title,
        "content": chapter_content,
        "previous": prev_chapter,
        "next": next_chapter
    }

    with open(os.path.join(SITE_DIR, "chapters", f"{sanitized_chapter_title}.json"), "w", encoding="utf-8") as json_file:
        json.dump(chapter_data, json_file, ensure_ascii=False, indent=4)

    novel_info["chapters"].append({
        "title": chapter_title,
        "filename": f"{sanitized_chapter_title}.json"
    })

# Сохранение данных о новелле
with open(os.path.join(SITE_DIR, "novel.json"), "w", encoding="utf-8") as novel_file:
    json.dump(novel_info, novel_file, ensure_ascii=False, indent=4)

print(f"Data saved to '{SITE_DIR}'")
generate_index()