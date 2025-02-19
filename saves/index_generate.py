import os
import json

SITE_DIR = "site/Blizarus.github.io"
NOVELS_DIR = os.path.join(SITE_DIR, "novels")
INDEX_FILE = os.path.join(SITE_DIR, "index.html")

def generate_index():
    """
    Генерация главной страницы index.html с перечнем всех новелл.
    """
    novels = []

    # Обходим папку novels
    for novel_folder in os.listdir(NOVELS_DIR):
        novel_path = os.path.join(NOVELS_DIR, novel_folder)
        if os.path.isdir(novel_path):
            novel_json_path = os.path.join(novel_path, "novel.json")
            if os.path.exists(novel_json_path):
                with open(novel_json_path, "r", encoding="utf-8") as novel_file:
                    novel_info = json.load(novel_file)
                    novels.append({
                        "title": novel_info["title"],
                        "author": novel_info.get("author", "Unknown"),
                        "link": f"novel_template.html?novel={novel_folder}"  # ссылка на шаблон страницы новеллы
                    })

    # Создаём HTML для главной страницы
    with open(INDEX_FILE, "w", encoding="utf-8") as index_file:
        index_file.write("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>My Novels</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="style.css" rel="stylesheet" />
        </head>
        <body class="container my-5">
            <h1 class="mb-4">My Novels</h1>
            <div class="list-group">
        """)

        for novel in novels:
            index_file.write(f"""
            <a href="{novel['link']}" class="list-group-item list-group-item-action">
                <h5 class="mb-1">{novel['title']}</h5>
                <small>Author: {novel['author']}</small>
            </a>
            """)

        index_file.write("""
            </div>
        </body>
        </html>
        """)

    print(f"Главная страница создана: {INDEX_FILE}")

# Генерация главной страницы
generate_index()
