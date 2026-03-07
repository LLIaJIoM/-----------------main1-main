#!/usr/bin/env python3
"""
Скрипт для парсинга отзывов с Avito и обновления reviews.json.
Запускается раз в день через GitHub Actions.

Подход 1: Avito internal API (быстро, без браузера)
Подход 2: Playwright headless browser (если API не работает)

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

# ID продавца на Avito
SELLER_ID = "c2b40ad72d9d2d39d8de28e340fff1f0"

# URL страницы с отзывами (для Playwright fallback)
AVITO_PAGE_URL = (
    "https://www.avito.ru/brands/i160621003/all"
    "?src=search_seller_info"
    "&iid=7528209497"
    f"&sellerId={SELLER_ID}"
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

    # Несколько версий API для пробы
    api_urls = [
        f"https://www.avito.ru/web/6/user/{SELLER_ID}/ratings?page=1&limit=20",
        f"https://www.avito.ru/web/5/user/{SELLER_ID}/ratings?page=1&limit=20",
        f"https://www.avito.ru/web/4/user/{SELLER_ID}/ratings?page=1&limit=20",
        f"https://m.avito.ru/api/18/user/{SELLER_ID}/ratings?page=1&limit=20",
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
# Подход 2: Playwright (headless browser)
# ═══════════════════════════════════════════════════════════

def try_playwright():
    """
    Попробовать получить отзывы через headless browser.
    Возвращает список отзывов или пустой список при ошибке.
    """
    print("\n[ПОДХОД 2] Playwright headless browser")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [SKIP] Playwright не установлен")
        return []

    reviews = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            locale="ru-RU",
        )

        # Скрываем признаки автоматизации
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()

        try:
            print(f"  [*] Загрузка: {AVITO_PAGE_URL[:60]}...")
            page.goto(AVITO_PAGE_URL, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            # Скриншот для дебага
            screenshot_path = os.path.join(SCRIPT_DIR, "avito_debug.png")
            page.screenshot(path=screenshot_path, full_page=False)
            print(f"  [*] Скриншот: {screenshot_path}")

            # Ищем вкладку "Отзывы"
            try:
                tabs = page.query_selector_all('[data-marker*="tab"], [role="tab"]')
                for tab in tabs:
                    tab_text = tab.inner_text().strip().lower()
                    if "отзыв" in tab_text:
                        tab.click()
                        page.wait_for_timeout(3000)
                        print("  [*] Перешли на вкладку Отзывы")
                        break
            except Exception:
                pass

            # Перехватываем XHR-запросы к API отзывов
            print("  [*] Ищем отзывы через JS...")
            js_reviews = page.evaluate("""
                () => {
                    const results = [];
                    // Ищем все текстовые блоки, которые похожи на отзывы
                    const allElements = document.querySelectorAll('div, article, section, li');
                    const seen = new Set();

                    for (const el of allElements) {
                        // Проверяем маркеры отзывов
                        const marker = el.getAttribute('data-marker') || '';
                        const cls = el.className || '';

                        const isReview = (
                            marker.includes('review') ||
                            marker.includes('rating') ||
                            cls.includes('Review') ||
                            cls.includes('review') ||
                            cls.includes('feedback') ||
                            cls.includes('Feedback')
                        );

                        if (!isReview) continue;

                        const text = el.innerText || '';
                        if (text.length < 10 || text.length > 2000) continue;

                        // Дедупликация
                        const key = text.substring(0, 50);
                        if (seen.has(key)) continue;
                        seen.add(key);

                        // Подсчёт звёзд
                        const stars = el.querySelectorAll(
                            '[class*="filled"], [class*="active"], [class*="Full"]'
                        );

                        results.push({
                            text: text.substring(0, 1000),
                            rating: stars.length || 5,
                            marker: marker,
                            cls: cls.substring(0, 100)
                        });
                    }
                    return results;
                }
            """)

            if js_reviews:
                print(f"  [*] Найдено {len(js_reviews)} блоков")
                for jr in js_reviews:
                    review = parse_text_block(jr.get("text", ""), jr.get("rating", 5))
                    if review:
                        reviews.append(review)
            else:
                # Логируем текст страницы для дебага
                body = page.inner_text("body")[:500]
                print(f"  [WARN] Отзывы не найдены. Текст:\n  {body[:300]}...")

        except Exception as e:
            print(f"  [ОШИБКА] {e}")
        finally:
            browser.close()

    if reviews:
        print(f"  [OK] Извлечено {len(reviews)} отзывов через Playwright")
    else:
        print("  [FAIL] Playwright подход не удался")

    return reviews


def parse_text_block(text, rating=5):
    """Разбор текстового блока отзыва."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) < 2:
        return None

    name = lines[0] if len(lines[0]) < 30 else "Клиент"
    review_text = ""
    date = ""

    skip_words = ["оценка", "отзыв", "ответ", "полезн", "пожалов", "подробнее", "показать"]

    for line in lines[1:]:
        line_lower = line.lower()
        # Ищем дату
        date_match = re.search(
            r'\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',
            line_lower
        )
        if date_match:
            date = line.strip()
            continue
        # Пропускаем служебные строки
        if any(w in line_lower for w in skip_words):
            continue
        if len(line) > 3:
            if review_text:
                review_text += " "
            review_text += line

    if not review_text or len(review_text) < 3:
        return None

    return {
        "name": name,
        "rating": min(max(rating, 1), 5),
        "text": review_text[:500],
        "date": clean_date(date),
        "source": "Avito"
    }


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print(f"  Парсинг отзывов с Avito — {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 60)
    print(f"[*] Файл отзывов: {REVIEWS_FILE}")

    current_reviews = load_current_reviews()
    print(f"[*] Текущих отзывов: {len(current_reviews)}")

    # Подход 1: API
    new_reviews = try_avito_api()

    # Подход 2: Playwright (если API не дал результатов)
    if not new_reviews:
        new_reviews = try_playwright()

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
