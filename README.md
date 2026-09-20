# engineering-ai.space

Сайт Engineering AI: ИИ для роботизированных платформ и автономных
транспортных систем. Статическая сборка на Hugo, публикация — GitHub Pages
(кастомный домен `engineering-ai.space`, режим deploy через workflow).

## Стек

| Компонент | Что используется |
|---|---|
| Генератор | Hugo **0.158.0 extended** (версия зафиксирована и в CI, и локально) |
| Тема | [`m03315/nomad-tech`](https://github.com/m03315/nomad-tech) — вендорена в `themes/nomad-tech` |
| Хостинг | GitHub Pages, deploy-workflow (`build_type: workflow`) |
| Аналитика | Яндекс.Метрика `112548629` (+ цель `contact_click`) |
| Языки | RU — в корне (`/`), EN — зеркало (`/en/`), выбор по гео и по явному клику |

Тема подключена **вендором** (копия в `themes/`), а не Hugo-модулем: сборка не
обращается к сети и не зависит от изменений в чужом репозитории. Обновление
темы = осознанный diff, а не «подтянулось само».

## Структура

```
hugo.toml            конфиг: языки, меню, params (бренд, email, счётчик Метрики)
content/             RU-контент (contentDir для языка ru)
content.en/          EN-контент (contentDir для языка en)
data/services.yaml   6 направлений работы, ключи ru/en
data/process.yaml    3 этапа запуска, ключи ru/en
i18n/ru.toml         подписи интерфейса (RU)
i18n/en.toml         подписи интерфейса (EN) — ключи обязаны совпадать
layouts/             переопределения темы (head, index, baseof, header, footer, 404, sitemap)
assets/scss/main.scss  дизайн-система сайта (токены light/dark)
assets/js/main.js    переключатель темы + мобильное меню
static/              CNAME, robots.txt, geo-lang.js, favicons, файлы верификации
themes/nomad-tech/   вендоренная тема (каркас: baseof, i18n-механика)
```

## Что переопределено из темы и почему

Файлы с тем же путём, что и в теме, имеют приоритет и заменяют её версии —
тема даёт каркас, но её «nomad-блог»-начинка для корпоративного сайта не нужна:

| Файл | Причина переопределения |
|---|---|
| `layouts/partials/head.html` | тема тянет свой JS/CSS-бандл (particles, SPA-навигация) |
| `layouts/index.html` | другая структура главной: hero, направления, этапы, контакты |
| `layouts/_default/baseof.html` | свой `<html lang>`, skip-link, подключение скриптов |
| `assets/scss/main.scss` | полная замена дизайн-системы (неоновая тема → B2B) |
| `assets/js/main.js` | только тема + мобильное меню, без свайп-навигации по «секциям» |
| `layouts/about/list.html` | тема объявляет СВОЙ `about/list.html` — он перебил бы `_default/list.html` |

## Локальная сборка

```bash
hugo --gc --minify --baseURL "https://engineering-ai.space/"
# результат: public/
```

Локальный предпросмотр: `hugo server -D --baseURL "http://localhost:1313/"`.

## Проверка перед пушем

```bash
# 1. статический проход по артефакту (hreflang, canonical, JSON-LD, sitemap, 404)
python ~/AppData/Local/hermes/skills/web/github-pages-ops/scripts/verify_hugo_build.py \
    public --domain engineering-ai.space

# 2. рендер в реальном браузере: CSS грузится, тема переключается,
#    мобильное меню открывается, утечек классов прежней темы нет;
#    отдельно — языковой переключатель на вложенной странице
```

## URL и редиректы

Прежние адреса сохранены редиректами (`aliases` во front matter):

| Было | Стало |
|---|---|
| `/about.html` | `/about/` |
| `/en/about.html` | `/en/about/` |

Alias в EN-контенте указывается **без** префикса `/en/`: Hugo подставляет
языковой префикс сам, иначе получается вложенный `/en/en/about.html`.

## Гео-роутинг RU/EN

`static/geo-lang.js` (копия без изменений) + hreflang-тройка на каждой
странице: посетитель из России остаётся на RU, остальные уводятся на `/en/`.
Явный клик по переключателю языка запоминается в `localStorage` и важнее гео.
Скрипт не подключается к `404.html`. Логика проверяется харнессом
`test_geo_lang.mjs` (12 сценариев).

## Деплой

Пуш в `main` → `.github/workflows/deploy.yml`: сборка зафиксированной версией
Hugo, гейт на артефакт (`CNAME`, `geo-lang.js`, `robots.txt`, обе главные,
счётчик Метрики, hreflang) → публикация через OIDC. Секретов не требуется.

**Pages должен быть в режиме `workflow`.** В режиме `legacy` GitHub собирает
ветку Jekyll'ом, а собранного `index.html` в репозитории нет — это отдаёт 404
на всех edge'ах.
