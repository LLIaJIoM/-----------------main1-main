#!/usr/bin/env python3
"""
Скрипт для парсинга отзывов с Avito и обновления reviews.json.
Запускается раз в день через cron на сервере или GitHub Actions.

Использует Avito internal API (без Playwright, без браузера).
Если парсинг не удался — текущий reviews.json НЕ трогается.
"""

import json
import os
import sys
import re
import time
import random
import urllib.request
import urllib.error
import ssl
from datetime import datetime

# Путь к файлу отзывов
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEWS_FILE = os.path.join(SCRIPT_DIR, "assets", "reviews.json")

# ID продавца на Avito (числовой из URL /brands/i160621003)
SELLER_NUMERIC_ID = "160621003"
# Hash продавца (из параметра sellerId в URL)
SELLER_HASH = "c2b40ad72d9d2d39d8de28e340fff1f0"

# URL страницы с отзывами (для справки)
AVITO_PAGE_URL = (
    f"https://www.avito.ru/brands/i{SELLER_NUMERIC_ID}/all"
    "?src=search_seller_info"
    "&iid=7528209497"
    f"&sellerId={SELLER_HASH}"
)

# Сколько отзывов показывать на сайте
MAX_REVIEWS = 6

# User-Agent для запросов
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def load_current_reviews():
    """Загрузить текущие отзывы из файла."""
    try:
        with open(REVIEWS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_reviews(reviews):
    """Сохранить отзывы в файл."""
    with open(REVIEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)
    print(f"[OK] Сохранено {len(reviews)} отзывов в {REVIEWS_FILE}")


def parse_date_to_sort_key(date_str):
    """Конвертировать русскую дату в ключ сортировки (новые первые)."""
    months = {
        "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
        "мая": 5, "июня": 6, "июля": 7, "августа": 8,
        "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
    }
    try:
        parts = date_str.strip().lower().split()
        if len(parts) >= 2:
            day = int(parts[0])
            month = months.get(parts[1], 0)
            year = int(parts[2]) if len(parts) >= 3 else datetime.now().year
            return year * 10000 + month * 100 + day
    except Exception:
        pass
    return 0


def clean_date(raw):
    """Очистить и нормализовать строку даты."""
    if not raw:
        return ""
    s = re.sub(r'\s+', ' ', str(raw)).strip()
    m = re.search(
        r'(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',
        s.lower()
    )
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return s[:30] if s else ""


def timestamp_to_russian_date(ts):
    """Конвертировать Unix timestamp в русскую дату."""
    months_gen = [
        "", "января", "февраля", "марта", "апреля", "мая", "июня",
        "июля", "августа", "сентября", "октября", "ноября", "декабря"
    ]
    try:
        dt = datetime.fromtimestamp(int(ts))
        return f"{dt.day} {months_gen[dt.month]}"
    except Exception:
        return ""


def reviews_changed(old_reviews, new_reviews):
    """Проверить, изменились ли отзывы."""
    if len(old_reviews) != len(new_reviews):
        return True
    for old, new in zip(old_reviews, new_reviews):
        if old.get("name") != new.get("name") or old.get("text") != new.get("text"):
            return True
    return False


# ═══════════════════════════════════════════════════════════
# Подход 1: Avito Internal API
# ═══════════════════════════════════════════════════════════

def try_avito_api():
    """
    Попробовать получить отзывы через внутренний API Avito.
    Возвращает список отзывов или пустой список при ошибке.
    """
    print("\n[ПОДХОД 1] Avito Internal API")

    # Все возможные эндпоинты API (разные пути, версии, ID)
    api_urls = [
        # reviews (не ratings!)
        f"https://www.avito.ru/web/6/user/{SELLER_NUMERIC_ID}/reviews?page=1&limit=20",
        f"https://www.avito.ru/web/6/user/{SELLER_HASH}/reviews?page=1&limit=20",
        # ratings с разными параметрами
        f"https://www.avito.ru/web/6/user/{SELLER_NUMERIC_ID}/ratings?page=1&limit=20",
        f"https://www.avito.ru/web/6/user/{SELLER_HASH}/ratings?page=1&limit=20",
        # feedbacks
        f"https://www.avito.ru/web/6/user/{SELLER_NUMERIC_ID}/feedbacks?page=1&limit=20",
        # brands endpoint
        f"https://www.avito.ru/web/6/brands/{SELLER_NUMERIC_ID}/reviews?page=1&limit=20",
        f"https://www.avito.ru/web/6/brands/{SELLER_NUMERIC_ID}/ratings?page=1&limit=20",
        # profiles
        f"https://www.avito.ru/web/6/profiles/{SELLER_NUMERIC_ID}/reviews?page=1&limit=20",
        f"https://www.avito.ru/web/6/profiles/{SELLER_HASH}/reviews?page=1&limit=20",
        # mobile API
        f"https://m.avito.ru/api/18/user/{SELLER_NUMERIC_ID}/reviews?page=1&limit=20",
        f"https://m.avito.ru/api/22/user/{SELLER_NUMERIC_ID}/reviews?page=1&limit=20",
    ]

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.avito.ru/",
        "Origin": "https://www.avito.ru",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    ctx = ssl.create_default_context()

    for url in api_urls:
        print(f"  [*] Пробуем: {url[:80]}...")
        try:
            # Небольшая задержка для имитации человека
            time.sleep(random.uniform(1, 3))

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)

            # Проверяем, не rate-limit ли это
            if isinstance(data, dict) and ("too-many-requests" in data or "error" in data):
                print(f"  [!] Rate limit / ошибка: {data}")
                continue

            # Подробный дебаг структуры ответа
            debug_structure(data, url)

            reviews = parse_api_response(data)
            if reviews:
                print(f"  [OK] Получено {len(reviews)} отзывов через API")
                return reviews
            else:
                print(f"  [!] API ответил, но парсер не извлёк отзывы")

        except urllib.error.HTTPError as e:
            print(f"  [!] HTTP {e.code}: {e.reason}")
            if e.code == 429:
                print("  [!] Rate limit, ждём...")
                time.sleep(5)
        except urllib.error.URLError as e:
            print(f"  [!] URL ошибка: {e.reason}")
        except json.JSONDecodeError:
            print(f"  [!] Ответ не JSON")
        except Exception as e:
            print(f"  [!] Ошибка: {e}")

    print("  [FAIL] API подход не удался")
    return []


def debug_structure(data, url=""):
    """Подробный лог структуры API-ответа для дебага."""
    print(f"  [DEBUG] === Структура ответа ===")
    if isinstance(data, dict):
        print(f"  [DEBUG] Тип: dict, ключи: {list(data.keys())}")
        for key in data:
            val = data[key]
            if isinstance(val, list):
                print(f"  [DEBUG]   '{key}': list[{len(val)}]")
                if val:
                    first = val[0]
                    if isinstance(first, dict):
                        print(f"  [DEBUG]     [0] keys: {list(first.keys())}")
                        # Показываем значения первого элемента (обрезая длинные)
                        for k, v in first.items():
                            sv = str(v)[:100]
                            print(f"  [DEBUG]     [0].{k} = {sv}")
                    else:
                        print(f"  [DEBUG]     [0] = {str(first)[:200]}")
            elif isinstance(val, dict):
                print(f"  [DEBUG]   '{key}': dict, keys: {list(val.keys())}")
                for k2 in val:
                    v2 = val[k2]
                    if isinstance(v2, list):
                        print(f"  [DEBUG]     '{k2}': list[{len(v2)}]")
                        if v2 and isinstance(v2[0], dict):
                            print(f"  [DEBUG]       [0] keys: {list(v2[0].keys())}")
                            for k3, v3 in v2[0].items():
                                print(f"  [DEBUG]       [0].{k3} = {str(v3)[:100]}")
                    else:
                        print(f"  [DEBUG]     '{k2}' = {str(v2)[:100]}")
            else:
                print(f"  [DEBUG]   '{key}': {str(val)[:100]}")
    elif isinstance(data, list):
        print(f"  [DEBUG] Тип: list[{len(data)}]")
        if data and isinstance(data[0], dict):
            print(f"  [DEBUG]   [0] keys: {list(data[0].keys())}")
    print(f"  [DEBUG] === конец ===")
    return


def find_review_list(data, depth=0):
    """
    Рекурсивно ищет список отзывов в структуре данных.
    Возвращает первый найденный список словарей.
    """
    if depth > 5:
        return None

    if isinstance(data, list) and len(data) > 0:
        # Проверяем, похож ли этот список на отзывы
        if isinstance(data[0], dict):
            # Ищем характерные поля отзыва
            keys = set(data[0].keys())
            review_fields = {"text", "body", "comment", "message", "rating", "score", "value"}
            if keys & review_fields:
                return data
        return data if isinstance(data[0], dict) else None

    if isinstance(data, dict):
        # Приоритетные ключи для поиска
        priority_keys = [
            "entries", "ratings", "reviews", "items", "result",
            "data", "list", "comments", "feedbacks"
        ]
        # Сначала проверяем приоритетные ключи
        for key in priority_keys:
            if key in data:
                found = find_review_list(data[key], depth + 1)
                if found:
                    return found
        # Потом все остальные
        for key in data:
            if key not in priority_keys:
                found = find_review_list(data[key], depth + 1)
                if found:
                    return found
    return None


def parse_api_response(data):
    """Разобрать JSON-ответ API Avito и извлечь отзывы."""
    reviews = []

    # Рекурсивно ищем список отзывов в любой структуре
    items = find_review_list(data)

    if not items or not isinstance(items, list):
        print(f"  [DEBUG] find_review_list не нашёл список")
        return []

    print(f"  [DEBUG] Найден список из {len(items)} элементов")

    for item in items:
        if not isinstance(item, dict):
            continue

        # Извлекаем поля с максимальной гибкостью
        name = extract_field(item, [
            "userName", "user_name", "authorName", "author_name",
            "senderName", "sender_name", "name", "title"
        ])
        # Также проверяем вложенные объекты
        if not name:
            for sub_key in ["author", "user", "sender", "owner"]:
                sub = item.get(sub_key)
                if isinstance(sub, dict):
                    name = sub.get("name") or sub.get("title") or sub.get("userName") or ""
                    if name:
                        break
        name = str(name).strip() if name else "Клиент"

        text = extract_field(item, [
            "text", "body", "comment", "message", "content", "description", "review"
        ])
        if not text or len(str(text).strip()) < 2:
            continue
        text = str(text).strip()

        rating = extract_field(item, ["rating", "score", "value", "stars", "mark"])
        try:
            rating = int(rating) if rating else 5
        except (ValueError, TypeError):
            rating = 5

        # Дата — может быть timestamp или строка
        raw_date = extract_field(item, [
            "date", "created", "createdAt", "created_at",
            "updatedAt", "updated_at", "time", "timestamp"
        ])
        if isinstance(raw_date, (int, float)):
            # Если timestamp < 100000, возможно это относительное время
            if raw_date > 1000000000:
                date = timestamp_to_russian_date(raw_date)
            else:
                date = ""
        else:
            date = clean_date(str(raw_date)) if raw_date else ""

        reviews.append({
            "name": name or "Клиент",
            "rating": min(max(rating, 1), 5),
            "text": text[:500],
            "date": date,
            "source": "Avito"
        })

    return reviews


def extract_field(obj, field_names):
    """Извлечь значение из словаря, пробуя несколько имён полей."""
    for name in field_names:
        val = obj.get(name)
        if val is not None and val != "" and val != 0:
            return val
    return None


# ═══════════════════════════════════════════════════════════
# Подход 2: HTML-парсинг страницы Avito
# ═══════════════════════════════════════════════════════════

def try_html_scrape():
    """
    Загрузить HTML страницы Avito и извлечь отзывы из SSR-контента.
    На российском IP Avito может отдать HTML с данными без капчи.
    """
    print("\n[ПОДХОД 2] HTML-парсинг страницы Avito")

    urls_to_try = [
        AVITO_PAGE_URL,
        f"https://www.avito.ru/user/{SELLER_HASH}/reviews",
        f"https://www.avito.ru/brands/i{SELLER_NUMERIC_ID}/all/otzyvy",
    ]

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Accept-Encoding": "identity",
        "Cache-Control": "no-cache",
    }

    ctx = ssl.create_default_context()

    for url in urls_to_try:
        print(f"  [*] Загружаем: {url[:80]}...")
        try:
            time.sleep(random.uniform(2, 4))
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            # Проверяем, не капча ли это
            if "captcha" in html.lower() or "проблема с IP" in html:
                print(f"  [!] Капча/блокировка IP")
                continue

            print(f"  [*] Получено {len(html)} символов HTML")

            # Подход A: Ищем JSON в __NEXT_DATA__ или window.__initialData__
            reviews = extract_reviews_from_ssr_json(html)
            if reviews:
                print(f"  [OK] Найдено {len(reviews)} отзывов в SSR JSON")
                return reviews

            # Подход B: Парсим HTML напрямую (regex)
            reviews = extract_reviews_from_html(html)
            if reviews:
                print(f"  [OK] Найдено {len(reviews)} отзывов в HTML")
                return reviews

            # Дебаг: показываем фрагменты HTML с "отзыв" или "review"
            for pattern in ["отзыв", "review", "rating", "feedback"]:
                idx = html.lower().find(pattern)
                if idx >= 0:
                    snippet = html[max(0, idx-100):idx+200].replace("\n", " ")
                    print(f"  [DEBUG] Найдено '{pattern}' в HTML: ...{snippet[:200]}...")

        except urllib.error.HTTPError as e:
            print(f"  [!] HTTP {e.code}: {e.reason}")
        except Exception as e:
            print(f"  [!] Ошибка: {e}")

    print("  [FAIL] HTML-парсинг не удался")
    return []


def extract_reviews_from_ssr_json(html):
    """Извлечь отзывы из JSON, встроенного в HTML (SSR/Next.js)."""
    reviews = []

    # Ищем JSON в script-тегах
    patterns = [
        r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        r'window\.__initialData__\s*=\s*(\{.*?\});?\s*</script>',
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\});?\s*</script>',
        r'"reviews?":\s*(\[.*?\])',
        r'"ratings?":\s*(\[.*?\])',
        r'"feedbacks?":\s*(\[.*?\])',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match)
                found = find_review_list(data)
                if found:
                    parsed = parse_api_response({"items": found})
                    if parsed:
                        return parsed
            except (json.JSONDecodeError, TypeError):
                continue

    return reviews


def extract_reviews_from_html(html):
    """Извлечь отзывы из HTML-разметки (regex-подход)."""
    reviews = []

    # Ищем типичные паттерны Avito: блоки с рейтингом + текстом + датой + именем
    # Avito использует data-marker атрибуты
    review_blocks = re.findall(
        r'data-marker="review[^"]*"[^>]*>(.*?)</(?:div|article|section)',
        html, re.DOTALL | re.IGNORECASE
    )

    if not review_blocks:
        # Пробуем другие паттерны
        review_blocks = re.findall(
            r'class="[^"]*[Rr]eview[^"]*"[^>]*>(.*?)</(?:div|article)',
            html, re.DOTALL
        )

    for block in review_blocks[:20]:
        # Извлекаем текст (убираем HTML-теги)
        text = re.sub(r'<[^>]+>', ' ', block)
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) < 10:
            continue

        # Пробуем извлечь имя, дату
        name_match = re.search(r'([А-Яа-яA-Za-z]+(?:\s+[А-Яа-яA-Za-z]+)?)', text)
        date_match = re.search(
            r'(\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря))',
            text.lower()
        )

        name = name_match.group(1) if name_match else "Клиент"
        date = date_match.group(1) if date_match else ""

        # Убираем имя и дату из текста отзыва
        review_text = text
        if name and len(name) < 30:
            review_text = review_text.replace(name, "", 1).strip()
        if date:
            review_text = re.sub(re.escape(date), "", review_text, count=1).strip()

        if len(review_text) < 5:
            continue

        reviews.append({
            "name": name[:30] if name else "Клиент",
            "rating": 5,
            "text": review_text[:500],
            "date": clean_date(date),
            "source": "Avito"
        })

    return reviews


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print(f"  Парсинг отзывов с Avito — {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 60)
    print(f"[*] Файл отзывов: {REVIEWS_FILE}")
    print(f"[*] Числовой ID: {SELLER_NUMERIC_ID}")
    print(f"[*] Hash ID: {SELLER_HASH}")

    current_reviews = load_current_reviews()
    print(f"[*] Текущих отзывов: {len(current_reviews)}")

    # Подход 1: Avito API
    new_reviews = try_avito_api()

    # Подход 2: HTML-парсинг (если API не дал результатов)
    if not new_reviews:
        new_reviews = try_html_scrape()

    # Если ничего не нашли — не трогаем файл
    if not new_reviews:
        print("\n" + "=" * 60)
        print("[!] Отзывы не найдены ни одним способом.")
        print("[!] Текущий reviews.json НЕ изменён.")
        print("=" * 60)
        sys.exit(0)

    # Сортируем по дате (новые первые) и берём последние MAX_REVIEWS
    new_reviews.sort(key=lambda r: parse_date_to_sort_key(r.get("date", "")), reverse=True)
    new_reviews = new_reviews[:MAX_REVIEWS]

    # Проверяем, изменились ли отзывы
    if not reviews_changed(current_reviews, new_reviews):
        print("\n[*] Отзывы не изменились. Обновление не требуется.")
        sys.exit(0)

    # Сохраняем
    save_reviews(new_reviews)

    print("\n[*] Обновлённые отзывы:")
    for i, r in enumerate(new_reviews, 1):
        stars = "★" * r["rating"] + "☆" * (5 - r["rating"])
        print(f"  {i}. {r['name']} [{stars}]: {r['text'][:60]}... ({r['date']})")

    print("\n" + "=" * 60)
    print("[OK] reviews.json обновлён!")
    print("=" * 60)


if __name__ == "__main__":
    main()
