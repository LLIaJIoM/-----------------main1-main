# -*- coding: utf-8 -*-
"""Multi-page site renderer for Тёплый Дом."""

BASE_URL = "https://tepliy-dom.online"
PHONE = "+7 (929) 678-36-56"
PHONE_RAW = "+79296783656"

# ─── Navigation structure ───────────────────────────────────────────────
NAV = [
    {"label": "Главная", "href": "/"},
    {"label": "Услуги", "href": "/uslugi", "children": [
        {"label": "Ремонт котлов", "href": "/uslugi/remont-kotlov"},
        {"label": "Монтаж отопления", "href": "/uslugi/montazh-otopleniya"},
        {"label": "Химическая промывка", "href": "/uslugi/himicheskaya-promyvka"},
        {"label": "Монтаж тёплого пола", "href": "/uslugi/montazh-teplogo-pola"},
        {"label": "Подключение ZONT", "href": "/uslugi/podklyuchenie-zont"},
        {"label": "Консалтинг", "href": "/uslugi/konsalting"},
        {"label": "Техобслуживание", "href": "/uslugi/obsluzhivanie"},
    ]},
    {"label": "Бренды", "href": "/brendy", "children": [
        {"label": "Baxi", "href": "/brendy/baxi"},
        {"label": "Vaillant", "href": "/brendy/vaillant"},
        {"label": "Bosch", "href": "/brendy/bosch"},
        {"label": "Buderus", "href": "/brendy/buderus"},
        {"label": "Viessmann", "href": "/brendy/viessmann"},
        {"label": "Protherm", "href": "/brendy/protherm"},
        {"label": "Navien", "href": "/brendy/navien"},
        {"label": "Ariston", "href": "/brendy/ariston"},
    ]},
    {"label": "Цены", "href": "/price"},
    {"label": "Портфолио", "href": "/portfolio"},
    {"label": "Отзывы", "href": "/otzyvy"},
    {"label": "География", "href": "/geo", "children": [
        {"label": "Москва", "href": "/geo/moskva"},
        {"label": "Балашиха", "href": "/geo/balashikha"},
        {"label": "Истра", "href": "/geo/istra"},
        {"label": "Королёв", "href": "/geo/korolev"},
        {"label": "Красногорск", "href": "/geo/krasnogorsk"},
        {"label": "Лобня", "href": "/geo/lobnya"},
        {"label": "Мытищи", "href": "/geo/mytishchi"},
        {"label": "Одинцово", "href": "/geo/odintsovo"},
        {"label": "Орехово-Зуево", "href": "/geo/orekhovo-zuevo"},
        {"label": "Первомайский", "href": "/geo/pervomayskiy"},
        {"label": "Пушкино", "href": "/geo/pushkino"},
        {"label": "Химки", "href": "/geo/khimki"},
        {"label": "Щёлково", "href": "/geo/shchyolkovo"},
    ]},
    {"label": "О компании", "href": "/about"},
    {"label": "Контакты", "href": "/contacts"},
]


def render_nav(active_path="/"):
    """Render navigation HTML with dropdown support."""
    lines = []
    for item in NAV:
        is_active = active_path == item["href"] or (
            item.get("children") and active_path.startswith(item["href"] + "/")
        )
        if item.get("children"):
            parent_cls = "nav-parent active" if is_active else "nav-parent"
            lines.append(f'<div class="nav-dropdown">')
            lines.append(f'  <a href="{item["href"]}" class="{parent_cls}">{item["label"]} <span class="nav-arrow">▾</span></a>')
            lines.append(f'  <div class="nav-dropdown-menu">')
            for child in item["children"]:
                c_cls = ' class="active"' if active_path == child["href"] else ""
                lines.append(f'    <a href="{child["href"]}"{c_cls}>{child["label"]}</a>')
            lines.append(f'  </div>')
            lines.append(f'</div>')
        else:
            cls = ' class="active"' if is_active else ""
            lines.append(f'<a href="{item["href"]}"{cls}>{item["label"]}</a>')
    return "\n        ".join(lines)


def render_breadcrumbs(crumbs):
    """Render breadcrumb navigation. crumbs = [(label, href), ...]"""
    parts = []
    for i, (label, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            parts.append(f'<span class="breadcrumb-current">{label}</span>')
        else:
            parts.append(f'<a href="{href}">{label}</a>')
    return '<nav class="breadcrumbs" aria-label="Навигация"><div class="container">' + ' → '.join(parts) + '</div></nav>'


def render_cta_block(title="Получить бесплатную диагностику", subtitle="Оставьте заявку — мастер перезвонит в течение 15 минут"):
    return f'''
    <section class="section section-blue cta-section">
      <div class="container center">
        <h2>{title}</h2>
        <p class="lead">{subtitle}</p>
        <form id="cta-form" class="cta-inline-form">
          <div class="cta-form-row">
            <input type="text" name="name" placeholder="Ваше имя" required maxlength="50" pattern="[A-Za-zА-Яа-яЁё\\s\\-]+" autocomplete="name">
            <input type="tel" name="phone" placeholder="Телефон" required autocomplete="tel" inputmode="tel">
            <button type="submit" class="btn btn-cta btn-lg">Вызвать мастера</button>
          </div>
          <div id="cta-form-msg" class="form-msg" role="status" aria-live="polite"></div>
        </form>
        <div class="cta-phone-alt">
          <span>или позвоните:</span>
          <a href="tel:{PHONE_RAW}" class="cta-phone-link">📞 {PHONE}</a>
        </div>
      </div>
    </section>'''


def render_price_table(rows, caption=""):
    """rows = [(service, price), ...]"""
    lines = [f'<div class="price-table-wrap">{f"<h3>{caption}</h3>" if caption else ""}',
             '<table class="price-table"><thead><tr><th>Услуга / Неисправность</th><th>Стоимость</th></tr></thead><tbody>']
    for svc, price in rows:
        lines.append(f'<tr><td>{svc}</td><td class="price-cell">{price}</td></tr>')
    lines.append('</tbody></table></div>')
    return "\n".join(lines)


def render_faq(items):
    """items = [(question, answer), ...]"""
    lines = ['<div class="accordion">']
    for q, a in items:
        lines.append(f'''  <div class="accordion-item">
    <button class="accordion-btn">{q}</button>
    <div class="accordion-content"><p>{a}</p></div>
  </div>''')
    lines.append('</div>')
    return "\n".join(lines)


def render_brands_logos():
    brands = ["Baxi", "Vaillant", "Bosch", "Buderus", "Viessmann", "Protherm", "Navien", "Ariston"]
    items = []
    for b in brands:
        slug = b.lower()
        items.append(f'<a href="/brendy/{slug}" class="brand-logo-item">{b}</a>')
    return '<div class="brands-grid">' + "".join(items) + '</div>'


def render_work_steps():
    steps = [
        ("📞", "Заявка", "Позвоните или оставьте заявку на сайте"),
        ("🔍", "Диагностика", "Мастер проведёт бесплатную диагностику"),
        ("🔧", "Ремонт", "Выполним ремонт с оригинальными запчастями"),
        ("✅", "Гарантия", "Гарантия на работы — 2 года"),
    ]
    items = []
    for icon, title, desc in steps:
        items.append(f'<div class="step-card"><div class="step-icon">{icon}</div><h4>{title}</h4><p>{desc}</p></div>')
    return '<div class="steps-grid">' + "".join(items) + '</div>'


# ─── Feedback form (shared across pages) ────────────────────────────────
FEEDBACK_FORM = '''
<section id="feedback" class="section">
  <div class="container">
    <h2>Оставить заявку</h2>
    <p class="center">Заполните форму — мастер свяжется с вами в течение 15 минут.</p>
    <form id="feedback-form" class="form">
      <div class="form-row">
        <label for="name">Имя</label>
        <input id="name" name="name" type="text" placeholder="Ваше имя" required maxlength="50" pattern="[A-Za-zА-Яа-яЁё\\s\\-]+" title="Только буквы (макс. 50 символов)" autocomplete="name">
      </div>
      <div class="form-row">
        <label for="phone">Телефон</label>
        <input id="phone" name="phone" type="tel" required style="width: 100%;" autocomplete="tel" inputmode="tel">
      </div>
      <div class="form-row">
        <label for="comment">Комментарий</label>
        <textarea id="comment" name="comment" rows="4" placeholder="Опишите вашу проблему или вопрос" maxlength="1000"></textarea>
      </div>
      <div class="form-actions">
        <button type="submit" name="action" value="telegram" class="btn btn-telegram">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.16.16-.295.293-.605.293l.214-3.054 5.56-5.022c.24-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.942z" fill="white"/></svg>
          Отправить заявку
        </button>
        <button type="submit" name="action" value="whatsapp" class="btn btn-whatsapp">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M17.472 14.382C17.119 14.205 15.385 13.353 15.061 13.235C14.737 13.118 14.501 13.059 14.265 13.412C14.029 13.765 13.352 14.559 13.146 14.795C12.94 15.03 12.733 15.059 12.38 14.882C12.027 14.706 10.891 14.333 9.544 13.132C8.497 12.199 7.79 11.047 7.584 10.694C7.378 10.341 7.562 10.15 7.739 9.974C7.897 9.816 8.09 9.563 8.267 9.357C8.444 9.151 8.503 8.975 8.621 8.739C8.739 8.503 8.68 8.297 8.592 8.12C8.504 7.943 7.79 6.19 7.495 5.484C7.208 4.797 6.916 4.89 6.702 4.881C6.505 4.872 6.279 4.872 6.053 4.872C5.827 4.872 5.463 4.956 5.158 5.289C4.853 5.622 3.99 6.432 3.99 8.08C3.99 9.728 5.188 11.322 5.365 11.558C5.542 11.794 7.755 15.206 11.143 16.669C11.949 17.017 12.578 17.225 13.072 17.382C13.882 17.639 14.623 17.602 15.209 17.514C15.86 17.417 17.214 16.695 17.497 15.899C17.78 15.104 17.78 14.427 17.692 14.279C17.604 14.132 17.368 14.038 17.015 13.861H17.472Z" fill="white"/><path d="M12 0C5.373 0 0 5.373 0 12C0 14.084 0.536 16.108 1.556 17.876L0.556 21.528L4.298 20.548C5.975 21.463 7.915 21.966 9.944 21.996H12.054C18.626 21.996 24 16.623 24 10.998C24 4.373 18.627 0 12 0ZM12.054 20.129H12.052C10.274 20.129 8.525 19.651 6.996 18.744L6.634 18.529L2.91 19.505L3.904 15.875L3.668 15.499C2.658 13.896 2.126 12.05 2.126 10.998C2.126 5.545 6.556 1.871 12 1.871C17.444 1.871 21.874 5.545 21.874 10.998C21.874 16.451 17.444 20.129 12.054 20.129Z" fill="white"/></svg>
          Написать в WhatsApp
        </button>
      </div>
      <div id="form-msg" class="form-msg" role="status" aria-live="polite"></div>
    </form>
  </div>
</section>'''


# ─── Base page template ─────────────────────────────────────────────────
def render_page(title, description, content, active_path="/", canonical=None, keywords="", schema_extra=""):
    canon = canonical or (BASE_URL + active_path)
    nav_html = render_nav(active_path)
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#101316">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="keywords" content="{keywords}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:url" content="{canon}">
  <meta property="og:site_name" content="Тёплый Дом">
  <meta property="og:image" content="{BASE_URL}/assets/hero.jpg">
  <link rel="canonical" href="{canon}">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"LocalBusiness","name":"Тёплый Дом","url":"{BASE_URL}/","telephone":"{PHONE_RAW}","areaServed":"Москва и Московская область","image":"{BASE_URL}/assets/hero.jpg","description":"{description}","priceRange":"от 2700 ₽","address":{{"@type":"PostalAddress","addressLocality":"Москва","addressRegion":"Московская область","addressCountry":"RU"}}}}</script>
  {schema_extra}
  <link rel="icon" href="{BASE_URL}/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="{BASE_URL}/favicon.png" type="image/png" sizes="32x32">
  <link rel="icon" href="{BASE_URL}/favicon.ico" type="image/x-icon" sizes="16x16 32x32">
  <link rel="shortcut icon" href="{BASE_URL}/favicon.ico" type="image/x-icon">
  <link rel="apple-touch-icon" href="{BASE_URL}/icon-192.png">
  <link rel="manifest" href="/manifest.json">
  <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/18.2.1/css/intlTelInput.css">
  <link rel="stylesheet" href="/assets/styles.css?v=7">
  <link rel="stylesheet" href="/assets/emergency.css">
  <script type="text/javascript">
     (function(m,e,t,r,i,k,a){{
         m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
         m[i].l=1*new Date();
         for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
         k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
     }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=106684335', 'ym');
     ym(106684335, 'init', {{ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true}});
  </script>
  <noscript><div><img src="https://mc.yandex.ru/watch/106684335" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
</head>
<body>
  <a class="skip-link" href="#main">Перейти к содержанию</a>
  <header class="site-header">
    <div class="emergency-bar">
      <div class="container emergency-flex">
        <div class="emergency-item urgent">🔥 Котёл сломался? Выезд мастера за 40 минут!</div>
        <div class="emergency-item details">✅ Диагностика бесплатно | Гарантия 2 года | Работаем с 2012 г.</div>
        <div class="emergency-item contact">
          <a href="tel:{PHONE_RAW}" class="phone-link">📞 {PHONE}</a>
          <a href="/contacts#feedback" class="online-link">Заявка онлайн</a>
        </div>
      </div>
    </div>
    <div class="container header-inner">
      <a href="/" class="brand">Тёплый Дом</a>
      <button class="nav-toggle" aria-label="Меню" aria-controls="site-nav" aria-expanded="false" type="button">☰</button>
      <nav class="nav" id="site-nav" aria-label="Основная навигация">
        {nav_html}
      </nav>
    </div>
  </header>

  <main id="main">
    {content}
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-col">
          <div class="footer-brand">Тёплый Дом</div>
          <p>Ремонт, обслуживание и монтаж котлов в Москве и Московской области</p>
        </div>
        <div class="footer-col">
          <h4>Услуги</h4>
          <a href="/uslugi/remont-kotlov">Ремонт котлов</a>
          <a href="/uslugi/montazh-otopleniya">Монтаж отопления</a>
          <a href="/uslugi/himicheskaya-promyvka">Химическая промывка</a>
          <a href="/uslugi/montazh-teplogo-pola">Тёплый пол</a>
          <a href="/uslugi/obsluzhivanie">Техобслуживание</a>
        </div>
        <div class="footer-col">
          <h4>Бренды</h4>
          <a href="/brendy/baxi">Baxi</a>
          <a href="/brendy/vaillant">Vaillant</a>
          <a href="/brendy/bosch">Bosch</a>
          <a href="/brendy/buderus">Buderus</a>
          <a href="/brendy/viessmann">Viessmann</a>
        </div>
        <div class="footer-col">
          <h4>Контакты</h4>
          <a href="tel:{PHONE_RAW}">📞 {PHONE}</a>
          <a href="https://t.me/Vardan39" target="_blank" rel="noopener">Telegram</a>
          <a href="/contacts">Все контакты</a>
        </div>
      </div>
      <div class="footer-bottom">
        <div>© 2012–2026 «Тёплый Дом» | tepliy-dom.online</div>
        <div>ИП Хачатрян В.В. | ИНН: 616615453880 | ОГРНИП: 325508100235555</div>
      </div>
    </div>
  </footer>

  <div class="float-buttons">
    <a href="https://wa.me/79296783656?text=%D0%97%D0%B4%D1%80%D0%B0%D0%B2%D1%81%D1%82%D0%B2%D1%83%D0%B9%D1%82%D0%B5!%20%D0%9D%D1%83%D0%B6%D0%BD%D0%B0%20%D0%BA%D0%BE%D0%BD%D1%81%D1%83%D0%BB%D1%8C%D1%82%D0%B0%D1%86%D0%B8%D1%8F." class="float-btn whatsapp-float" target="_blank" rel="noopener" aria-label="Написать в WhatsApp">
      <svg viewBox="0 0 24 24" width="26" height="26" fill="#fff"><path d="M17.472 14.382c-.353-.177-2.087-1.029-2.411-1.147-.324-.117-.56-.176-.796.177-.236.353-.913 1.147-1.119 1.383-.206.236-.413.265-.766.088-.353-.176-1.489-.549-2.836-1.75-1.047-.933-1.754-2.085-1.96-2.438-.206-.353-.022-.544.155-.72.158-.158.353-.413.53-.619.177-.206.236-.353.353-.589.118-.236.059-.442-.029-.619-.088-.177-.796-1.927-1.091-2.639-.287-.687-.579-.594-.796-.604-.206-.009-.442-.012-.677-.012s-.619.088-.943.442c-.325.353-1.239 1.21-1.239 2.951s1.269 3.422 1.446 3.658c.177.236 2.498 3.812 6.05 5.345.846.364 1.505.581 2.02.744.849.266 1.621.228 2.231.138.68-.1 2.087-.854 2.382-1.679.295-.824.295-1.531.206-1.679-.088-.147-.324-.236-.677-.413zm-5.418 7.403h-.004c-1.77 0-3.513-.476-5.03-1.374l-.361-.214-3.741.981.998-3.648-.235-.374c-.99-1.574-1.513-3.393-1.513-5.26 0-5.45 4.436-9.884 9.889-9.884 2.64 0 5.122 1.03 6.988 2.898 1.866 1.869 2.893 4.352 2.892 6.993-.003 5.45-4.437 9.884-9.885 9.884zM20.52 3.449C18.24 1.226 15.24 0 12.045 0 5.463 0 .104 5.334.101 11.893c-.001 2.096.547 4.142 1.588 5.946L.057 24l6.305-1.654c1.737.947 3.693 1.447 5.683 1.448h.005c6.585 0 11.946-5.336 11.949-11.896.002-3.176-1.234-6.165-3.479-8.449z"/></svg>
    </a>
    <a href="https://t.me/Vardan39" class="float-btn telegram-float" target="_blank" rel="noopener" aria-label="Написать в Telegram">
      <svg viewBox="0 0 24 24" width="26" height="26" fill="#fff"><path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12.056 0h-.112zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.479.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>
    </a>
    <a href="tel:+79296783656" class="float-btn phone-float" aria-label="Позвонить">
      <svg viewBox="0 0 24 24" width="24" height="24" fill="#fff"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
    </a>
  </div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/18.2.1/js/intlTelInput.min.js" defer></script>
  <script src="/assets/script.js?v=15" defer></script>
  <button id="backToTop" class="back-to-top" aria-label="Наверх"><span>↑</span></button>
</body>
</html>'''


# ─── PAGE DEFINITIONS ───────────────────────────────────────────────────

def page_index():
    content = f'''
    <section class="section section-dark hero-section">
      <div class="container">
        <h1 class="page-title">Ремонт и обслуживание газовых котлов в Москве и МО</h1>
        <p class="lead">Профессиональный ремонт, монтаж и техническое обслуживание котлов всех марок. Выезд мастера за 40 минут, бесплатная диагностика, гарантия 2 года.</p>
        <div class="cta-buttons center">
          <a href="/contacts#feedback" class="btn btn-cta btn-lg">Получить бесплатную диагностику</a>
          <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">📞 {PHONE}</a>
        </div>
      </div>
      <div class="wide-image" aria-label="Фото оборудования">
        <img src="/assets/hero.jpg" alt="Профессиональный ремонт и монтаж котлов" loading="eager" fetchpriority="high" decoding="async" width="1120" height="420">
      </div>
    </section>

    <section class="section trust-section">
      <div class="container">
        <div class="trust-grid">
          <div class="trust-item"><div class="trust-number">12+</div><div class="trust-label">лет опыта</div></div>
          <div class="trust-item"><div class="trust-number">2000+</div><div class="trust-label">довольных клиентов</div></div>
          <div class="trust-item"><div class="trust-number">40</div><div class="trust-label">мин — выезд мастера</div></div>
          <div class="trust-item"><div class="trust-number">2</div><div class="trust-label">года гарантии</div></div>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2>Наши услуги</h2>
        <p class="lead">Полный спектр услуг по ремонту, монтажу и обслуживанию отопительного оборудования</p>
        <div class="services">
          <article class="service">
            <div class="service-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 14l4 4 10-10-4-4L3 14zm13-9l4 4"></path></svg></div>
            <h3>Ремонт котлов</h3>
            <p>Диагностика и ремонт газовых котлов всех марок. Выезд в день обращения.</p>
            <div class="service-price">от 2 700 ₽</div>
            <a href="/uslugi/remont-kotlov" class="btn btn-outline">Подробнее</a>
          </article>
          <article class="service">
            <div class="service-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18v12H3V6zm4 3v6m4-6v6m4-6v6"></path></svg></div>
            <h3>Монтаж отопления</h3>
            <p>Проектирование и установка систем отопления любой сложности.</p>
            <div class="service-price">от 9 900 ₽</div>
            <a href="/uslugi/montazh-otopleniya" class="btn btn-outline">Подробнее</a>
          </article>
          <article class="service">
            <div class="service-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3c2.5 3.7 6 6.3 6 9.5A6 6 0 0 1 6 12.5C6 9.3 9.5 6.7 12 3z"></path></svg></div>
            <h3>Химическая промывка</h3>
            <p>Промывка теплообменников и систем отопления для восстановления эффективности.</p>
            <div class="service-price">от 4 500 ₽</div>
            <a href="/uslugi/himicheskaya-promyvka" class="btn btn-outline">Подробнее</a>
          </article>
          <article class="service">
            <div class="service-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8h10v4H4V8zm10 0h6v8h-6V8zM4 12h10v8H4v-8z"></path></svg></div>
            <h3>Монтаж тёплого пола</h3>
            <p>Установка водяного тёплого пола с подключением к системе отопления.</p>
            <div class="service-price">от 5 000 ₽</div>
            <a href="/uslugi/montazh-teplogo-pola" class="btn btn-outline">Подробнее</a>
          </article>
          <article class="service">
            <div class="service-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 8c5-5 13-5 18 0M6 11c3.5-3.5 8.5-3.5 12 0M9 14c2-2 4-2 6 0M12 18a2 2 0 110-4 2 2 0 010 4"></path></svg></div>
            <h3>Подключение ZONT</h3>
            <p>Установка и настройка автоматики ZONT для удалённого управления отоплением.</p>
            <div class="service-price">от 3 500 ₽</div>
            <a href="/uslugi/podklyuchenie-zont" class="btn btn-outline">Подробнее</a>
          </article>
          <article class="service">
            <div class="service-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16v12H4V6zm3 3h10M7 13h6"></path></svg></div>
            <h3>Техобслуживание</h3>
            <p>Плановое техническое обслуживание котлов для продления срока службы.</p>
            <div class="service-price">от 3 000 ₽</div>
            <a href="/uslugi/obsluzhivanie" class="btn btn-outline">Подробнее</a>
          </article>
        </div>
      </div>
    </section>

    <section class="section section-dark">
      <div class="container">
        <h2>Как мы работаем</h2>
        {render_work_steps()}
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2>Работаем с ведущими брендами</h2>
        <p class="lead">Ремонтируем и обслуживаем котлы всех популярных производителей</p>
        {render_brands_logos()}
      </div>
    </section>

    <section class="section section-dark">
      <div class="container">
        <h2>Отзывы клиентов</h2>
        <p class="center">Подборка отзывов с Avito. Полная история доступна по ссылке ниже.</p>
        <div id="reviews-list" class="cards reviews-grid"></div>
        <div class="cta-wrap center">
          <a href="/otzyvy" class="btn btn-outline">Все отзывы</a>
        </div>
      </div>
    </section>

    {render_cta_block()}

    <section class="section section-dark">
      <div class="container">
        <h2>Часто задаваемые вопросы</h2>
        {render_faq([
            ("Сколько стоит ремонт газового котла?", "Стоимость ремонта зависит от неисправности. Диагностика бесплатная, ремонт — от 2 700 ₽. Точную стоимость мастер назовёт после осмотра. Все цены — на странице <a href='/price'>прайс-листа</a>."),
            ("Как быстро приедет мастер?", "Мастер выезжает в течение 40 минут после обращения по Москве и ближайшему Подмосковью. В отдалённые районы МО — в течение 1,5–2 часов."),
            ("Какие марки котлов вы ремонтируете?", "Мы работаем со всеми популярными брендами: Baxi, Vaillant, Bosch, Buderus, Viessmann, Protherm, Navien, Ariston и другими. <a href='/brendy/baxi'>Подробнее о брендах</a>."),
            ("Даёте ли гарантию на работы?", "Да, гарантия на все выполненные работы — 2 года. Гарантия оформляется актом выполненных работ."),
            ("Работаете ли вы с юридическими лицами?", "Да, мы работаем как с частными, так и с юридическими лицами. Оформляем договор, предоставляем полный пакет документов для бухгалтерии."),
        ])}
      </div>
    </section>
    '''
    return render_page(
        title="Тёплый Дом — ремонт и обслуживание газовых котлов в Москве и МО",
        description="Профессиональный ремонт, монтаж и обслуживание газовых котлов в Москве и Московской области. Выезд мастера за 40 минут, бесплатная диагностика, гарантия 2 года.",
        keywords="ремонт котлов, монтаж отопления, обслуживание газовых котлов, Москва, Московская область",
        content=content,
        active_path="/"
    )


# ─── SERVICE PAGES ──────────────────────────────────────────────────────

SERVICES = {
    "remont-kotlov": {
        "title": "Ремонт газовых котлов в Москве и МО",
        "h1": "Ремонт газовых котлов в Москве и МО — выезд за 40 минут",
        "desc": "Профессиональный ремонт газовых, электрических и дизельных котлов. Выезд мастера за 40 минут, бесплатная диагностика, гарантия 2 года.",
        "intro": "Ремонтируем котлы всех типов и марок: газовые, электрические, дизельные. Мастер приезжает с полным набором инструментов и запасных частей. Диагностика бесплатная — вы платите только за ремонт.",
        "prices": [
            ("Диагностика неисправности", "Бесплатно"),
            ("Замена платы управления", "от 3 500 ₽"),
            ("Замена теплообменника", "от 4 000 ₽"),
            ("Замена циркуляционного насоса", "от 2 700 ₽"),
            ("Замена трёхходового клапана", "от 2 500 ₽"),
            ("Замена газового клапана", "от 3 000 ₽"),
            ("Замена вентилятора (турбины)", "от 3 500 ₽"),
            ("Устранение течи теплообменника", "от 4 500 ₽"),
            ("Чистка и настройка горелки", "от 2 700 ₽"),
            ("Замена датчиков (NTC, давления, протока)", "от 1 500 ₽"),
        ],
        "faq": [
            ("Сколько стоит ремонт котла?", "Диагностика — бесплатная. Стоимость ремонта зависит от неисправности: от 1 500 ₽ за замену датчика до 4 500 ₽ за ремонт теплообменника. Точную цену мастер назовёт после диагностики."),
            ("Как быстро приедет мастер?", "По Москве и ближайшему Подмосковью мастер приезжает в течение 40 минут. В отдалённые районы МО — в течение 1,5–2 часов."),
            ("Какие запчасти используете?", "Используем только оригинальные запчасти или качественные аналоги от проверенных производителей. Запчасти есть на складе — ремонт в большинстве случаев за один визит."),
        ],
        "keywords": "ремонт котлов Москва, ремонт газового котла, ремонт котла цена, вызвать мастера по ремонту котла",
    },
    "montazh-otopleniya": {
        "title": "Монтаж отопления в Москве и МО",
        "h1": "Монтаж систем отопления в Москве и Московской области",
        "desc": "Проектирование и монтаж систем отопления любой сложности. Установка котлов, радиаторов, конвекторов. Гарантия 2 года.",
        "intro": "Проектируем и монтируем системы отопления для частных домов и коммерческих объектов. Работаем с газовыми, электрическими и комбинированными системами. Подбираем оптимальное оборудование под ваш бюджет.",
        "prices": [
            ("Проектирование системы отопления", "от 5 000 ₽"),
            ("Монтаж настенного газового котла", "от 9 900 ₽"),
            ("Монтаж напольного газового котла", "от 14 000 ₽"),
            ("Монтаж электрического котла", "от 7 500 ₽"),
            ("Установка радиатора отопления", "от 3 500 ₽"),
            ("Обвязка котельной", "от 25 000 ₽"),
            ("Монтаж коллекторной системы", "от 15 000 ₽"),
            ("Опрессовка системы отопления", "от 4 000 ₽"),
            ("Запуск и настройка системы", "от 3 000 ₽"),
        ],
        "faq": [
            ("Какой котёл лучше для частного дома?", "Выбор зависит от площади, утепления и доступного топлива. Для домов до 200 м² рекомендуем настенные котлы Baxi, Vaillant или Bosch. Для больших домов — напольные котлы Buderus или Viessmann."),
            ("Сколько времени занимает монтаж?", "Монтаж системы отопления «под ключ» для частного дома площадью 100–200 м² занимает 3–5 дней. Установка котла — 1 день."),
            ("Включена ли настройка котла в стоимость?", "Да, в стоимость монтажа входит пуско-наладка и настройка оборудования."),
        ],
        "keywords": "монтаж отопления, установка котла, монтаж котла цена Москва, монтаж системы отопления",
    },
    "himicheskaya-promyvka": {
        "title": "Химическая промывка котлов и систем отопления",
        "h1": "Химическая промывка котлов и систем отопления в Москве",
        "desc": "Профессиональная химическая промывка теплообменников, котлов и систем отопления. Восстановление теплоотдачи, снижение расхода газа.",
        "intro": "Химическая промывка — эффективный способ удалить накипь, ржавчину и отложения из теплообменника котла и системы отопления. Процедура восстанавливает теплоотдачу до 98%, снижает расход газа и продлевает срок службы оборудования.",
        "prices": [
            ("Промывка первичного теплообменника", "от 4 500 ₽"),
            ("Промывка вторичного теплообменника (ГВС)", "от 4 000 ₽"),
            ("Промывка двух теплообменников", "от 7 000 ₽"),
            ("Промывка системы отопления (до 10 радиаторов)", "от 8 000 ₽"),
            ("Промывка системы отопления (10–20 радиаторов)", "от 12 000 ₽"),
            ("Промывка бойлера косвенного нагрева", "от 5 000 ₽"),
        ],
        "faq": [
            ("Как часто нужно промывать котёл?", "Рекомендуем промывать теплообменник котла каждые 2–3 года, а систему отопления — каждые 5–7 лет. При жёсткой воде — чаще."),
            ("Сколько времени занимает промывка?", "Промывка одного теплообменника занимает 2–4 часа. Промывка всей системы — от 4 до 8 часов в зависимости от объёма."),
            ("Безопасна ли химическая промывка?", "Да, мы используем сертифицированные реагенты, которые безопасны для оборудования. После промывки система нейтрализуется и промывается чистой водой."),
        ],
        "keywords": "химическая промывка котла, промывка теплообменника, промывка системы отопления цена",
    },
    "montazh-teplogo-pola": {
        "title": "Монтаж тёплого пола в Москве и МО",
        "h1": "Монтаж водяного тёплого пола в Москве и Подмосковье",
        "desc": "Установка водяного тёплого пола с подключением к системе отопления. Расчёт, проектирование, монтаж. Гарантия 2 года.",
        "intro": "Монтируем водяной тёплый пол для частных домов и квартир. Равномерный прогрев помещения, экономия на отоплении до 30%. Работаем с любыми напольными покрытиями.",
        "prices": [
            ("Расчёт и проектирование тёплого пола", "от 3 000 ₽"),
            ("Монтаж тёплого пола (за м²)", "от 500 ₽/м²"),
            ("Установка коллектора тёплого пола", "от 5 000 ₽"),
            ("Укладка теплоизоляции", "от 200 ₽/м²"),
            ("Заливка стяжки", "от 400 ₽/м²"),
            ("Опрессовка и пуско-наладка", "от 3 000 ₽"),
        ],
        "faq": [
            ("Какой тёплый пол лучше: водяной или электрический?", "Водяной тёплый пол экономичнее в эксплуатации на 40–60% по сравнению с электрическим. Рекомендуем водяной для домов с газовым отоплением."),
            ("Можно ли сделать тёплый пол в квартире?", "Да, но в квартире с центральным отоплением подключение к стояку запрещено. Мы устанавливаем тёплый пол от автономного котла или электрического."),
            ("Какой толщины будет конструкция?", "Общая толщина «пирога» тёплого пола составляет 10–12 см: утеплитель 3–5 см, трубы 1,6–2 см, стяжка 4–5 см."),
        ],
        "keywords": "монтаж тёплого пола, водяной тёплый пол цена, установка тёплого пола Москва",
    },
    "podklyuchenie-zont": {
        "title": "Подключение автоматики ZONT для котлов",
        "h1": "Подключение и настройка автоматики ZONT в Москве",
        "desc": "Установка контроллеров ZONT для удалённого управления отоплением. GSM/Wi-Fi, сценарии, оповещения. Настройка под ключ.",
        "intro": "Система ZONT позволяет управлять котлом дистанционно через приложение на смартфоне. Вы сможете контролировать температуру, получать уведомления об авариях и экономить на отоплении, задавая расписания и сценарии.",
        "prices": [
            ("Установка контроллера ZONT", "от 3 500 ₽"),
            ("Настройка сценариев и расписаний", "от 2 000 ₽"),
            ("Подключение датчиков температуры", "от 1 500 ₽/шт"),
            ("Настройка GSM/Wi-Fi модуля", "от 1 500 ₽"),
            ("Интеграция с термостатами", "от 2 500 ₽"),
            ("Комплексная настройка «под ключ»", "от 7 000 ₽"),
        ],
        "faq": [
            ("Что такое ZONT?", "ZONT — это система автоматики для управления отоплением через интернет. Позволяет удалённо контролировать и настраивать котёл через приложение на телефоне."),
            ("С какими котлами работает ZONT?", "ZONT совместим с большинством газовых и электрических котлов: Baxi, Vaillant, Bosch, Buderus, Viessmann, Protherm, Navien и другими."),
            ("Нужен ли интернет для работы?", "ZONT работает через GSM (SIM-карта) или Wi-Fi. Рекомендуем GSM-версию для загородных домов — она работает независимо от интернета."),
        ],
        "keywords": "ZONT подключение, автоматика котла, удалённое управление отоплением, ZONT настройка",
    },
    "konsalting": {
        "title": "Консалтинг по газовому оборудованию",
        "h1": "Консультации по выбору и обслуживанию газового оборудования",
        "desc": "Профессиональные консультации по выбору котла, проектированию отопления, оптимизации расходов. Помощь с документами для газовых служб.",
        "intro": "Поможем подобрать оптимальное оборудование для вашего дома или объекта. Проконсультируем по вопросам проектирования, эксплуатации и обслуживания отопительных систем. Поможем с документами для газовых служб.",
        "prices": [
            ("Консультация по выбору котла", "Бесплатно"),
            ("Расчёт системы отопления", "от 3 000 ₽"),
            ("Подготовка документов для газовой службы", "от 5 000 ₽"),
            ("Аудит существующей системы отопления", "от 4 000 ₽"),
            ("Консультация по оптимизации расходов", "от 2 000 ₽"),
        ],
        "faq": [
            ("Можно ли получить консультацию бесплатно?", "Да, первичная консультация по выбору котла и оборудования — бесплатная. Звоните или оставляйте заявку."),
            ("Помогаете ли с документами?", "Да, помогаем подготовить документы для газовых служб, включая проект газоснабжения и акты."),
        ],
        "keywords": "консалтинг газовое оборудование, подбор котла, консультация по отоплению",
    },
    "obsluzhivanie": {
        "title": "Техническое обслуживание котлов в Москве",
        "h1": "Техническое обслуживание газовых котлов в Москве и МО",
        "desc": "Плановое ТО газовых котлов всех марок. Чистка, настройка, проверка безопасности. Продление срока службы оборудования.",
        "intro": "Регулярное техническое обслуживание — залог безопасной и экономичной работы котла. Включает чистку горелки, проверку газовых соединений, настройку давления и тяги, диагностику электроники.",
        "prices": [
            ("ТО настенного газового котла", "от 3 000 ₽"),
            ("ТО напольного газового котла", "от 4 500 ₽"),
            ("ТО двухконтурного котла", "от 3 500 ₽"),
            ("Чистка горелки и камеры сгорания", "от 2 500 ₽"),
            ("Проверка и настройка автоматики", "от 1 500 ₽"),
            ("Замена фильтров и уплотнений", "от 1 000 ₽"),
            ("Годовой контракт на обслуживание", "от 8 000 ₽/год"),
        ],
        "faq": [
            ("Как часто нужно обслуживать котёл?", "Рекомендуется проводить ТО газового котла 1 раз в год, перед началом отопительного сезона (август–октябрь)."),
            ("Что входит в ТО котла?", "Чистка горелки и теплообменника, проверка давления газа и воды, проверка герметичности соединений, диагностика электроники, настройка параметров."),
            ("Обязательно ли ТО котла?", "По закону техобслуживание газового оборудования обязательно. Кроме того, многие производители требуют ежегодное ТО для сохранения гарантии."),
        ],
        "keywords": "техобслуживание котла, ТО газового котла, обслуживание котла Москва, ежегодное ТО котла цена",
    },
}


def render_service_page(slug):
    s = SERVICES[slug]
    crumbs = render_breadcrumbs([("Главная", "/"), ("Услуги", "/uslugi"), (s["h1"].split(" в ")[0] if " в " in s["h1"] else s["h1"].split(" — ")[0], f"/uslugi/{slug}")])
    price_table = render_price_table(s["prices"], "Цены на услугу")
    faq_html = render_faq(s["faq"])
    content = f'''
    {crumbs}
    <section class="section">
      <div class="container">
        <h1>{s["h1"]}</h1>
        <p class="lead">{s["intro"]}</p>
        {render_work_steps()}
      </div>
    </section>

    <section class="section section-dark">
      <div class="container">
        <h2>Стоимость</h2>
        {price_table}
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2>Работаем с ведущими брендами</h2>
        {render_brands_logos()}
      </div>
    </section>

    {render_cta_block()}

    <section class="section section-dark">
      <div class="container">
        <h2>Часто задаваемые вопросы</h2>
        {faq_html}
      </div>
    </section>

    {FEEDBACK_FORM}
    '''
    return render_page(
        title=s["title"] + " — Тёплый Дом",
        description=s["desc"],
        keywords=s.get("keywords", ""),
        content=content,
        active_path=f"/uslugi/{slug}"
    )


def page_uslugi_index():
    cards = []
    for slug, s in SERVICES.items():
        cards.append(f'''
        <a href="/uslugi/{slug}" class="service-card-link">
          <article class="service">
            <h3>{s["h1"].split(" в ")[0] if " в " in s["h1"] else s["h1"].split(" — ")[0]}</h3>
            <p>{s["intro"][:120]}...</p>
            <span class="btn btn-outline">Подробнее</span>
          </article>
        </a>''')
    crumbs = render_breadcrumbs([("Главная", "/"), ("Услуги", "/uslugi")])
    content = f'''
    {crumbs}
    <section class="section">
      <div class="container">
        <h1>Наши услуги</h1>
        <p class="lead">Полный спектр услуг по ремонту, монтажу и обслуживанию отопительного оборудования в Москве и Московской области</p>
        <div class="services">
          {"".join(cards)}
        </div>
      </div>
    </section>
    {render_cta_block()}
    '''
    return render_page(
        title="Услуги по ремонту и обслуживанию котлов — Тёплый Дом",
        description="Полный перечень услуг компании Тёплый Дом: ремонт котлов, монтаж отопления, химическая промывка, тёплый пол, подключение ZONT.",
        content=content,
        active_path="/uslugi"
    )


# ─── BRAND PAGES ────────────────────────────────────────────────────────

BRANDS = {
    "baxi": {
        "name": "Baxi",
        "country": "Италия",
        "desc_short": "Итальянские котлы Baxi — одни из самых популярных в России благодаря надёжности и доступной цене.",
        "features": "Электронное управление, модулируемая горелка, встроенная диагностика, компактные размеры.",
        "typical_issues": "Ошибки платы управления, выход из строя теплообменника из-за накипи, проблемы с розжигом, течь трёхходового клапана.",
        "error_codes": [
            ("E01", "Нет розжига — проблема с газовым клапаном, электродом розжига или платой управления"),
            ("E02", "Перегрев — неисправность датчика NTC, засорение теплообменника или насоса"),
            ("E03", "Ошибка дымоудаления — неисправность вентилятора или реле давления дымовых газов"),
            ("E04", "Ложное срабатывание пламени — замена платы управления"),
            ("E05", "Неисправность датчика NTC отопления — замена датчика"),
            ("E06", "Неисправность датчика NTC ГВС — замена датчика"),
            ("E10", "Низкое давление воды — подпитка системы, проверка расширительного бака"),
            ("E25", "Слишком быстрый рост температуры — воздух в системе или неисправность насоса"),
            ("E35", "Паразитное пламя — неисправность платы, газового клапана"),
        ],
    },
    "vaillant": {
        "name": "Vaillant",
        "country": "Германия",
        "desc_short": "Немецкие котлы Vaillant — премиум-класс с высоким КПД и надёжностью. Конденсационные модели экономят до 15% газа.",
        "features": "Конденсационная технология, сенсорное управление, погодозависимая автоматика, низкий уровень шума.",
        "typical_issues": "Ошибки датчиков, проблемы с розжигом в холодное время года, неисправность платы управления, течь в теплообменнике.",
        "error_codes": [
            ("F22", "Низкое давление воды — подпитка системы, проверка расширительного бака"),
            ("F28", "Нет розжига — проблема с газовым клапаном, электродом или платой"),
            ("F29", "Потеря пламени — нестабильная подача газа, засорение дымохода"),
            ("F75", "Неисправность датчика давления — замена датчика или насоса"),
            ("F83", "Ошибка датчика температуры — замена NTC датчика"),
        ],
    },
    "bosch": {
        "name": "Bosch",
        "country": "Германия",
        "desc_short": "Котлы Bosch — надёжная немецкая техника для отопления. Широкий модельный ряд от бюджетных до конденсационных моделей.",
        "features": "Простое управление, модулируемая горелка, встроенная функция антизамерзания, энергоэффективность класса А.",
        "typical_issues": "Засорение теплообменника, ошибки датчиков температуры, проблемы с насосом, неисправность газового клапана.",
        "error_codes": [
            ("EA", "Нет розжига — проверка газового клапана, электрода, газового крана"),
            ("E2", "Перегрев — неисправность датчика NTC или засорение теплообменника"),
            ("E9", "Срабатывание предохранительного термостата — перегрев системы"),
            ("CE", "Низкое давление воды — подпитка системы, проверка утечек"),
            ("C6", "Вентилятор не работает — замена вентилятора или платы"),
        ],
    },
    "buderus": {
        "name": "Buderus",
        "country": "Германия",
        "desc_short": "Buderus — немецкий бренд с 275-летней историей (входит в группу Bosch). Надёжные котлы для объектов любого масштаба.",
        "features": "Высокий КПД, длительный срок службы, совместимость с автоматикой Bosch, широкий выбор мощностей.",
        "typical_issues": "Ошибки датчиков, накипь в теплообменнике, проблемы с насосом, неисправности платы управления.",
        "error_codes": [
            ("6A", "Нет розжига — проверка газового клапана и электрода"),
            ("2E", "Недостаток воды — подпитка системы, проверка утечек"),
            ("3C", "Перегрев — неисправность датчика или засорение теплообменника"),
            ("4C", "Ошибка дымоудаления — проверка вентилятора и дымохода"),
        ],
    },
    "viessmann": {
        "name": "Viessmann",
        "country": "Германия",
        "desc_short": "Viessmann — премиальные немецкие котлы с инновационными технологиями. Конденсационные модели с КПД до 98%.",
        "features": "Нержавеющий теплообменник Inox-Radial, MatriX-горелка, интеграция с солнечными коллекторами, ViCare — управление через приложение.",
        "typical_issues": "Ошибки датчиков температуры, проблемы с горелкой, неисправность платы, засорение конденсатного отвода.",
        "error_codes": [
            ("F2", "Ошибка горелки — неисправность электрода или газового клапана"),
            ("F3", "Ошибка ионизации — нет пламени, проверка электрода и газа"),
            ("F4", "Ошибка дымоудаления — засорение дымохода, неисправность вентилятора"),
            ("F5", "Ошибка подачи воздуха — проверка воздушного канала"),
            ("0C", "Обрыв датчика температуры — замена NTC датчика"),
        ],
    },
    "protherm": {
        "name": "Protherm",
        "country": "Словакия",
        "desc_short": "Protherm — европейские котлы с отличным соотношением цены и качества. Популярные модели: Пантера, Гепард, Медведь.",
        "features": "Простое управление, надёжная конструкция, доступные запчасти, сервис по всей России.",
        "typical_issues": "Ошибки розжига, проблемы с насосом, выход из строя платы управления, течь трёхходового клапана.",
        "error_codes": [
            ("F1", "Потеря пламени — проверка газового клапана и электрода розжига"),
            ("F2", "Неисправность датчика температуры — замена NTC"),
            ("F3", "Перегрев — проверка насоса и теплообменника"),
            ("F4", "Нет тяги — проверка дымохода и вентилятора"),
            ("F5", "Внешняя ошибка — проверка внешних подключений"),
        ],
    },
    "navien": {
        "name": "Navien",
        "country": "Южная Корея",
        "desc_short": "Navien — корейские котлы с передовыми технологиями. Выносливые, экономичные, с удобным управлением.",
        "features": "Турбонаддув, нержавеющий теплообменник, пульт управления с голосовыми подсказками, встроенный Wi-Fi (Navien Smart).",
        "typical_issues": "Ошибки датчиков, засорение теплообменника жёсткой водой, проблемы с вентилятором, ошибки давления.",
        "error_codes": [
            ("02", "Нехватка воды — подпитка системы, проверка датчика протока"),
            ("03", "Нет сигнала пламени — проверка электрода, газового клапана"),
            ("10", "Ошибка дымоудаления — засорение дымохода, неисправность вентилятора"),
            ("12", "Потеря пламени — нестабильная подача газа"),
            ("16", "Перегрев — проверка насоса и теплообменника"),
        ],
    },
    "ariston": {
        "name": "Ariston",
        "country": "Италия",
        "desc_short": "Ariston — итальянские котлы с хорошим соотношением цены и качества. Популярны в сегменте бюджетных решений.",
        "features": "Компактные размеры, автоматическая диагностика, защита от замерзания, модулируемая горелка.",
        "typical_issues": "Засорение теплообменника, ошибки датчиков NTC, проблемы с розжигом, выход из строя насоса.",
        "error_codes": [
            ("101", "Перегрев — неисправность NTC датчика или засорение теплообменника"),
            ("103", "Недостаточная циркуляция — воздух в системе или неисправность насоса"),
            ("104", "Нет тяги — засорение дымохода, неисправность вентилятора"),
            ("501", "Нет розжига — проверка газового клапана, электрода"),
            ("607", "Залипание реле — замена платы управления"),
        ],
    },
}


def render_brand_page(slug):
    b = BRANDS[slug]
    crumbs = render_breadcrumbs([("Главная", "/"), ("Бренды", "/brendy"), (b["name"], f"/brendy/{slug}")])

    error_rows = "\n".join([
        f'<tr><td class="error-code">{code}</td><td>{desc}</td></tr>'
        for code, desc in b["error_codes"]
    ])

    content = f'''
    {crumbs}
    <section class="section">
      <div class="container">
        <h1>Ремонт котлов {b["name"]} в Москве — выезд за 40 минут</h1>
        <p class="lead">{b["desc_short"]}</p>

        <div class="brand-info-grid">
          <div class="brand-info-card">
            <h3>Страна производитель</h3>
            <p>{b["country"]}</p>
          </div>
          <div class="brand-info-card">
            <h3>Особенности</h3>
            <p>{b["features"]}</p>
          </div>
          <div class="brand-info-card">
            <h3>Типичные неисправности</h3>
            <p>{b["typical_issues"]}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-dark">
      <div class="container">
        <h2>Коды ошибок котлов {b["name"]}</h2>
        <p class="center">Расшифровка основных кодов ошибок. Если ваш котёл показывает ошибку — звоните, мастер поможет!</p>
        <div class="price-table-wrap">
          <table class="price-table error-table">
            <thead><tr><th>Код</th><th>Описание и решение</th></tr></thead>
            <tbody>{error_rows}</tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2>Стоимость ремонта котлов {b["name"]}</h2>
        {render_price_table([
            ("Диагностика", "Бесплатно"),
            ("Замена платы управления", "от 3 500 ₽"),
            ("Замена теплообменника", "от 4 000 ₽"),
            ("Замена циркуляционного насоса", "от 2 700 ₽"),
            ("Чистка и настройка горелки", "от 2 700 ₽"),
            ("Химическая промывка теплообменника", "от 4 500 ₽"),
            ("Техническое обслуживание", "от 3 000 ₽"),
        ])}
      </div>
    </section>

    <section class="section section-dark">
      <div class="container">
        <h2>Как мы работаем</h2>
        {render_work_steps()}
      </div>
    </section>

    {render_cta_block(f"Нужен ремонт котла {b['name']}?", "Оставьте заявку — мастер перезвонит в течение 15 минут")}

    {FEEDBACK_FORM}
    '''
    return render_page(
        title=f"Ремонт котлов {b['name']} в Москве — коды ошибок, цены | Тёплый Дом",
        description=f"Ремонт котлов {b['name']} в Москве и МО. Коды ошибок, цены, бесплатная диагностика. Выезд мастера за 40 минут, гарантия 2 года.",
        keywords=f"ремонт котлов {b['name']}, ремонт {b['name']} цена, коды ошибок {b['name']}, {b['name']} сервис Москва",
        content=content,
        active_path=f"/brendy/{slug}"
    )


def page_brendy_index():
    cards = []
    for slug, b in BRANDS.items():
        cards.append(f'''
        <a href="/brendy/{slug}" class="service-card-link">
          <article class="service brand-card">
            <h3>{b["name"]}</h3>
            <div class="brand-country">{b["country"]}</div>
            <p>{b["desc_short"]}</p>
            <span class="btn btn-outline">Подробнее</span>
          </article>
        </a>''')
    crumbs = render_breadcrumbs([("Главная", "/"), ("Бренды", "/brendy")])
    content = f'''
    {crumbs}
    <section class="section">
      <div class="container">
        <h1>Бренды котлов — ремонт и обслуживание</h1>
        <p class="lead">Ремонтируем и обслуживаем котлы всех популярных производителей. Оригинальные запчасти, опытные мастера.</p>
        <div class="services">
          {"".join(cards)}
        </div>
      </div>
    </section>
    {render_cta_block()}
    '''
    return render_page(
        title="Ремонт котлов по брендам — Baxi, Vaillant, Bosch и другие | Тёплый Дом",
        description="Ремонт котлов всех популярных брендов: Baxi, Vaillant, Bosch, Buderus, Viessmann, Protherm, Navien, Ariston. Москва и МО.",
        content=content,
        active_path="/brendy"
    )


# ─── GEO PAGES ──────────────────────────────────────────────────────────

GEO_CITIES = {
    "moskva": {"name": "Москва", "prep": "Москве", "desc_extra": "Выезд мастера в любой район Москвы в течение 40 минут."},
    "balashikha": {"name": "Балашиха", "prep": "Балашихе", "desc_extra": "Обслуживаем Балашиху, Железнодорожный, Салтыковку, Реутов."},
    "istra": {"name": "Истра", "prep": "Истре", "desc_extra": "Обслуживаем Истру, Дедовск, Снегири, Павловскую Слободу и весь Истринский городской округ."},
    "korolev": {"name": "Королёв", "prep": "Королёве", "desc_extra": "Обслуживаем Королёв, Юбилейный, Болшево, Текстильщик."},
    "krasnogorsk": {"name": "Красногорск", "prep": "Красногорске", "desc_extra": "Обслуживаем Красногорск, Нахабино, Опалиху, Павшинскую пойму и весь городской округ."},
    "lobnya": {"name": "Лобня", "prep": "Лобне", "desc_extra": "Обслуживаем Лобню, Катюшки, Луговую, Депо."},
    "mytishchi": {"name": "Мытищи", "prep": "Мытищах", "desc_extra": "Обслуживаем Мытищи, Перловку, Тайнинку, Дружбу и весь городской округ."},
    "odintsovo": {"name": "Одинцово", "prep": "Одинцово", "desc_extra": "Обслуживаем Одинцово, Трёхгорку, Новую Трёхгорку, Лесной Городок и Одинцовский район."},
    "orekhovo-zuevo": {"name": "Орехово-Зуево", "prep": "Орехово-Зуеве", "desc_extra": "Обслуживаем Орехово-Зуево, Ликино-Дулёво, Дрезну и окрестности."},
    "pervomayskiy": {"name": "Первомайский", "prep": "Первомайском", "desc_extra": "Обслуживаем посёлок Первомайский и прилегающие территории."},
    "pushkino": {"name": "Пушкино", "prep": "Пушкино", "desc_extra": "Обслуживаем Пушкино, Ивантеевку, Красноармейск и Пушкинский район."},
    "khimki": {"name": "Химки", "prep": "Химках", "desc_extra": "Обслуживаем Химки, Куркино, Сходню, Планерную."},
    "shchyolkovo": {"name": "Щёлково", "prep": "Щёлково", "desc_extra": "Обслуживаем Щёлково, Фрязино, Загорянский, Монино и Щёлковский район."},
}


def render_geo_page(slug):
    g = GEO_CITIES[slug]
    crumbs = render_breadcrumbs([("Главная", "/"), ("География", "/geo"), (g["name"], f"/geo/{slug}")])
    content = f'''
    {crumbs}
    <section class="section">
      <div class="container">
        <h1>Ремонт и обслуживание котлов в {g["prep"]}</h1>
        <p class="lead">Профессиональный ремонт, монтаж и обслуживание газовых котлов в {g["prep"]} и окрестностях. {g["desc_extra"]} Бесплатная диагностика, гарантия 2 года.</p>
        {render_work_steps()}
      </div>
    </section>

    <section class="section section-dark">
      <div class="container">
        <h2>Цены на ремонт котлов в {g["prep"]}</h2>
        {render_price_table([
            ("Диагностика неисправности", "Бесплатно"),
            ("Ремонт газового котла", "от 2 700 ₽"),
            ("Техническое обслуживание", "от 3 000 ₽"),
            ("Химическая промывка теплообменника", "от 4 500 ₽"),
            ("Монтаж настенного котла", "от 9 900 ₽"),
            ("Монтаж тёплого пола", "от 500 ₽/м²"),
        ])}
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2>Бренды котлов, которые мы ремонтируем</h2>
        {render_brands_logos()}
      </div>
    </section>

    {render_cta_block(f"Ремонт котла в {g['prep']}?", "Вызовите мастера — приедем в течение часа!")}

    {FEEDBACK_FORM}
    '''
    return render_page(
        title=f"Ремонт котлов в {g['prep']} — выезд мастера, цены | Тёплый Дом",
        description=f"Ремонт и обслуживание газовых котлов в {g['prep']}. Выезд мастера за 40 минут, бесплатная диагностика, гарантия 2 года. {g['desc_extra']}",
        keywords=f"ремонт котлов {g['name']}, обслуживание котлов {g['name']}, мастер по котлам {g['name']}",
        content=content,
        active_path=f"/geo/{slug}"
    )


def page_geo_index():
    cards = []
    for slug, g in GEO_CITIES.items():
        cards.append(f'''
        <a href="/geo/{slug}" class="service-card-link">
          <article class="service">
            <h3>Ремонт котлов в {g["prep"]}</h3>
            <p>{g["desc_extra"]}</p>
            <span class="btn btn-outline">Подробнее</span>
          </article>
        </a>''')
    crumbs = render_breadcrumbs([("Главная", "/"), ("География", "/geo")])
    content = f'''
    {crumbs}
    <section class="section">
      <div class="container">
        <h1>География обслуживания</h1>
        <p class="lead">Работаем по всей Москве и Московской области. Выезд мастера — от 40 минут.</p>
        <div class="services">
          {"".join(cards)}
        </div>
      </div>
    </section>
    {render_cta_block()}
    '''
    return render_page(
        title="Ремонт котлов в Москве и МО — география обслуживания | Тёплый Дом",
        description="Ремонт котлов в Москве, Одинцово, Химках, Мытищах, Балашихе и всей Московской области.",
        content=content,
        active_path="/geo"
    )


# ─── ADDITIONAL PAGES ───────────────────────────────────────────────────

def page_price():
    crumbs = render_breadcrumbs([("Главная", "/"), ("Прайс-лист", "/price")])
    content = f'''
    {crumbs}
    <section class="section">
      <div class="container">
        <h1>Прайс-лист на услуги</h1>
        <p class="lead">Актуальные цены на ремонт, монтаж и обслуживание котлов. Диагностика — бесплатно!</p>

        {render_price_table([
            ("Диагностика неисправности", "Бесплатно"),
            ("Замена платы управления", "от 3 500 ₽"),
            ("Замена теплообменника", "от 4 000 ₽"),
            ("Замена циркуляционного насоса", "от 2 700 ₽"),
            ("Замена трёхходового клапана", "от 2 500 ₽"),
            ("Замена газового клапана", "от 3 000 ₽"),
            ("Замена вентилятора (турбины)", "от 3 500 ₽"),
            ("Устранение течи теплообменника", "от 4 500 ₽"),
            ("Чистка и настройка горелки", "от 2 700 ₽"),
            ("Замена датчиков (NTC, давления, протока)", "от 1 500 ₽"),
        ], "Ремонт котлов")}

        {render_price_table([
            ("Монтаж настенного газового котла", "от 9 900 ₽"),
            ("Монтаж напольного газового котла", "от 14 000 ₽"),
            ("Монтаж электрического котла", "от 7 500 ₽"),
            ("Установка радиатора отопления", "от 3 500 ₽"),
            ("Обвязка котельной", "от 25 000 ₽"),
            ("Монтаж коллекторной системы", "от 15 000 ₽"),
            ("Опрессовка системы отопления", "от 4 000 ₽"),
        ], "Монтаж отопления")}

        {render_price_table([
            ("Промывка первичного теплообменника", "от 4 500 ₽"),
            ("Промывка вторичного теплообменника (ГВС)", "от 4 000 ₽"),
            ("Промывка двух теплообменников", "от 7 000 ₽"),
            ("Промывка системы отопления (до 10 радиаторов)", "от 8 000 ₽"),
            ("Промывка системы отопления (10–20 радиаторов)", "от 12 000 ₽"),
        ], "Химическая промывка")}

        {render_price_table([
            ("ТО настенного газового котла", "от 3 000 ₽"),
            ("ТО напольного газового котла", "от 4 500 ₽"),
            ("ТО двухконтурного котла", "от 3 500 ₽"),
            ("Годовой контракт на обслуживание", "от 8 000 ₽/год"),
        ], "Техническое обслуживание")}

        {render_price_table([
            ("Монтаж тёплого пола (за м²)", "от 500 ₽/м²"),
            ("Установка коллектора тёплого пола", "от 5 000 ₽"),
            ("Установка контроллера ZONT", "от 3 500 ₽"),
            ("Расчёт системы отопления", "от 3 000 ₽"),
        ], "Дополнительные услуги")}
      </div>
    </section>
    {render_cta_block()}
    '''
    return render_page(
        title="Прайс-лист — цены на ремонт и обслуживание котлов | Тёплый Дом",
        description="Актуальные цены на ремонт, монтаж и обслуживание газовых котлов. Диагностика бесплатно. Ремонт от 2 700 ₽, монтаж от 9 900 ₽.",
        keywords="цены на ремонт котлов, прайс-лист ремонт котлов, стоимость обслуживания котла",
        content=content,
        active_path="/price"
    )


def page_portfolio():
    crumbs = render_breadcrumbs([("Главная", "/"), ("Портфолио", "/portfolio")])
    content = f'''
    {crumbs}
    <section class="section section-dark">
      <div class="container">
        <h1>Портфолио выполненных работ</h1>
        <p class="center">Фотографии наших работ по ремонту, монтажу и обслуживанию котлов. Прокручивайте для просмотра.</p>
        <div class="carousel">
          <div class="carousel-track"></div>
          <button class="carousel-btn prev" aria-label="Предыдущее">‹</button>
          <button class="carousel-btn next" aria-label="Следующее">›</button>
          <div class="carousel-dots"></div>
        </div>
      </div>
    </section>
    {render_cta_block()}
    '''
    return render_page(
        title="Портфолио — примеры выполненных работ | Тёплый Дом",
        description="Фотографии выполненных работ по ремонту, монтажу и обслуживанию котлов. Более 2000 успешных проектов.",
        content=content,
        active_path="/portfolio"
    )


def page_otzyvy():
    crumbs = render_breadcrumbs([("Главная", "/"), ("Отзывы", "/otzyvy")])
    content = f'''
    {crumbs}
    <section class="section section-dark">
      <div class="container">
        <h1>Отзывы клиентов</h1>
        <p class="center">Подборка отзывов с Avito. Полная история доступна по ссылке ниже.</p>
        <div id="reviews-list" class="cards reviews-grid"></div>
        <div class="cta-wrap center">
          <a href="https://www.avito.ru/brands/i160621003/all?src=search_seller_info&iid=7528209497&sellerId=c2b40ad72d9d2d39d8de28e340fff1f0" class="btn btn-outline" target="_blank" rel="noopener">Смотреть все отзывы на Avito</a>
        </div>
      </div>
    </section>
    {render_cta_block()}
    '''
    return render_page(
        title="Отзывы клиентов — Тёплый Дом",
        description="Отзывы клиентов о ремонте и обслуживании котлов компанией Тёплый Дом. Более 100 отзывов на Avito.",
        content=content,
        active_path="/otzyvy"
    )


def page_kody_oshibok():
    crumbs = render_breadcrumbs([("Главная", "/"), ("Коды ошибок", "/kody-oshibok")])
    brand_sections = []
    for slug, b in BRANDS.items():
        rows = "\n".join([f'<tr><td class="error-code">{code}</td><td>{desc}</td></tr>' for code, desc in b["error_codes"]])
        brand_sections.append(f'''
        <div class="error-brand-section">
          <h3><a href="/brendy/{slug}">{b["name"]}</a></h3>
          <table class="price-table error-table">
            <thead><tr><th>Код</th><th>Описание</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>''')

    content = f'''
    {crumbs}
    <section class="section">
      <div class="container">
        <h1>Коды ошибок газовых котлов</h1>
        <p class="lead">Расшифровка кодов ошибок котлов по брендам. Если ваш котёл показывает ошибку — позвоните нам, мастер быстро устранит проблему!</p>
        {"".join(brand_sections)}
      </div>
    </section>
    {render_cta_block("Котёл показывает ошибку?", "Звоните — мастер выезжает в течение 40 минут!")}
    '''
    return render_page(
        title="Коды ошибок газовых котлов — расшифровка по брендам | Тёплый Дом",
        description="Расшифровка кодов ошибок газовых котлов Baxi, Vaillant, Bosch, Buderus, Viessmann, Protherm, Navien, Ariston.",
        keywords="коды ошибок котлов, ошибка котла, расшифровка ошибок Baxi, ошибки Vaillant",
        content=content,
        active_path="/kody-oshibok"
    )


def page_about():
    crumbs = render_breadcrumbs([("Главная", "/"), ("О компании", "/about")])
    content = f'''
    {crumbs}
    <section class="section">
      <div class="container">
        <h1>О компании «Тёплый Дом»</h1>
        <p class="lead">Компания «Тёплый Дом» — профессиональный ремонт, монтаж и обслуживание газовых котлов в Москве и Московской области с 2012 года.</p>

        <div class="about-content">
          <div class="trust-grid">
            <div class="trust-item"><div class="trust-number">12+</div><div class="trust-label">лет на рынке</div></div>
            <div class="trust-item"><div class="trust-number">2000+</div><div class="trust-label">довольных клиентов</div></div>
            <div class="trust-item"><div class="trust-number">8</div><div class="trust-label">брендов котлов</div></div>
            <div class="trust-item"><div class="trust-number">2</div><div class="trust-label">года гарантии</div></div>
          </div>

          <div class="about-features">
            <ul class="about-list">
              <li>Работаем с 2012 года — более 12 лет опыта</li>
              <li>Более 2000 довольных клиентов</li>
              <li>Сервис «под ключ»: проектирование, монтаж, ремонт, обслуживание</li>
              <li>Москва и вся Московская область</li>
              <li>Обслуживаем частных и юридических клиентов</li>
              <li>Собственный склад запчастей — быстрый ремонт за один визит</li>
              <li>Бесплатная диагностика при заказе ремонта</li>
              <li>Гарантия на работы — 2 года</li>
              <li>Выезд мастера в течение 40 минут</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section class="section section-dark">
      <div class="container features">
        <div class="feature">
          <div class="feature-icon">👤</div>
          <h3>Работаем с частными клиентами</h3>
          <p>Более 2000 частных клиентов за 12 лет работы. Мастера всегда на связи. Оплата любым удобным способом.</p>
        </div>
        <div class="feature">
          <div class="feature-icon">👥</div>
          <h3>Работаем с юридическими лицами</h3>
          <p>Сервис и установка промышленного оборудования, договор, отчётность. Более 300 выполненных проектов.</p>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2>Реквизиты</h2>
        <div class="requisites">
          <p><strong>ИП Хачатрян В.В.</strong></p>
          <p>ИНН: 616615453880</p>
          <p>ОГРНИП: 325508100235555</p>
        </div>
      </div>
    </section>
    {render_cta_block()}
    '''
    return render_page(
        title="О компании «Тёплый Дом» — ремонт и обслуживание котлов с 2012 года",
        description="Компания «Тёплый Дом» — более 12 лет опыта в ремонте и обслуживании газовых котлов в Москве и МО. 2000+ довольных клиентов.",
        content=content,
        active_path="/about"
    )


def page_contacts():
    crumbs = render_breadcrumbs([("Главная", "/"), ("Контакты", "/contacts")])
    content = f'''
    {crumbs}
    <section class="section section-blue">
      <div class="container contact-grid">
        <div>
          <h1 style="text-align:left; font-size: clamp(28px,3vw,36px)">Контакты</h1>
          <p>Телефон: <a href="tel:{PHONE_RAW}" class="phone-static" style="color:#fff">{PHONE}</a></p>
          <p>Режим работы: ежедневно, 8:00–22:00</p>
          <p>Адрес: Москва, Алтуфьевское шоссе, 37к1</p>
          <div class="socials">
            <a class="social tg" href="https://t.me/Vardan39" target="_blank" rel="noopener" aria-label="Telegram">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21.5 3.5L2.8 10.3c-.8.3-.8 1.4 0 1.7l4.8 1.6 1.8 5.7c.2.8 1.2.9 1.7.3l2.5-2.6 4.6 3.4c.6.4 1.4.1 1.6-.6l3-15.4c.2-.8-.6-1.4-1.3-1.2zM8.1 13.1l9.8-6.2-7.7 7.9-.3 3.7-1.8-5.4z"></path></svg>
            </a>
            <a class="social avito" href="https://www.avito.ru/brands/i160621003/all?src=search_seller_info&iid=7528209497&sellerId=c2b40ad72d9d2d39d8de28e340fff1f0" target="_blank" rel="noopener" aria-label="Avito">
              <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="8" cy="8" r="3" style="fill:#61BC47"></circle><circle cx="16" cy="8" r="3" style="fill:#4A86CF"></circle><circle cx="8" cy="16" r="3" style="fill:#8B65C0"></circle><circle cx="16" cy="16" r="3" style="fill:#EA3A3C"></circle></svg>
            </a>
          </div>
        </div>
        <div class="map-wrap">
          <iframe title="Карта: Алтуфьевское шоссе, 37к1" src="https://yandex.ru/map-widget/v1/?ll=37.575253%2C55.867369&z=15&pt=37.575253,55.867369,pm2rdm" frameborder="0" loading="lazy"></iframe>
        </div>
      </div>
    </section>

    {FEEDBACK_FORM}
    '''
    return render_page(
        title="Контакты — Тёплый Дом | Ремонт котлов в Москве",
        description="Контакты компании Тёплый Дом. Телефон, адрес, Telegram, карта проезда. Звоните — ответим в течение минуты.",
        content=content,
        active_path="/contacts"
    )


def page_spasibo():
    content = f'''
    <section class="section section-blue" style="min-height:60vh;display:flex;align-items:center">
      <div class="container center">
        <div style="font-size:64px;margin-bottom:24px">✅</div>
        <h1 style="font-size:clamp(28px,4vw,42px);margin-bottom:16px">Спасибо за заявку!</h1>
        <p class="lead" style="max-width:500px;margin:0 auto 24px">Мы получили ваше обращение и свяжемся с вами в ближайшие 15 минут.</p>
        <p style="opacity:.8;margin-bottom:32px">Если вопрос срочный — позвоните нам:</p>
        <a href="tel:{PHONE_RAW}" class="btn btn-cta btn-lg" style="font-size:20px">📞 {PHONE}</a>
        <div style="margin-top:32px">
          <a href="/" style="color:#fff;opacity:.7;text-decoration:underline">← Вернуться на главную</a>
        </div>
      </div>
    </section>
    '''
    return render_page(
        title="Спасибо за заявку — Тёплый Дом",
        description="Ваша заявка принята. Мы свяжемся с вами в ближайшие 15 минут.",
        content=content,
        active_path="/spasibo"
    )


# ─── URL ROUTING ────────────────────────────────────────────────────────

def get_page(path):
    """Return (html_content, status_code) for the given URL path."""
    path = path.rstrip("/") or "/"

    if path == "/":
        return page_index(), 200

    # Service pages
    if path == "/uslugi":
        return page_uslugi_index(), 200
    if path.startswith("/uslugi/"):
        slug = path.split("/uslugi/")[1]
        if slug in SERVICES:
            return render_service_page(slug), 200

    # Brand pages
    if path == "/brendy":
        return page_brendy_index(), 200
    if path.startswith("/brendy/"):
        slug = path.split("/brendy/")[1]
        if slug in BRANDS:
            return render_brand_page(slug), 200

    # Geo pages
    if path == "/geo":
        return page_geo_index(), 200
    if path.startswith("/geo/"):
        slug = path.split("/geo/")[1]
        if slug in GEO_CITIES:
            return render_geo_page(slug), 200

    # Additional pages
    if path == "/price":
        return page_price(), 200
    if path == "/portfolio":
        return page_portfolio(), 200
    if path == "/otzyvy":
        return page_otzyvy(), 200
    if path == "/kody-oshibok":
        return page_kody_oshibok(), 200
    if path == "/about":
        return page_about(), 200
    if path == "/contacts":
        return page_contacts(), 200
    if path == "/spasibo":
        return page_spasibo(), 200

    return None, 404
