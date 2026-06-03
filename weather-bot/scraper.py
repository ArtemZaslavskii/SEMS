import requests
from bs4 import BeautifulSoup


def get_weather_news() -> str:
    """
    Функция 3 — Получение новостей о погоде методом скрапинга HTML.
    Парсим сайт Гидрометцентра России — meteoinfo.ru
    """
    url = "https://meteoinfo.ru/news"
    headers = {
        # Представляемся браузером чтобы сайт не заблокировал запрос
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return f"❌ Не удалось загрузить новости. Код: {response.status_code}"

        soup = BeautifulSoup(response.text, "html.parser")

        # Ищем заголовки новостей на странице
        news_items = soup.select("div.news-item h3 a") or \
                     soup.select("h3 a") or \
                     soup.select(".news a")

        if not news_items:
            return "❌ Не удалось найти новости на странице. Сайт мог изменить структуру."

        result = "📰 Последние новости о погоде:\n\n"

        # Берём первые 5 новостей
        for i, item in enumerate(news_items[:5], start=1):
            title = item.get_text(strip=True)
            href  = item.get("href", "")

            # Если ссылка относительная — добавляем домен
            if href and not href.startswith("http"):
                href = "https://meteoinfo.ru" + href

            if title:
                result += f"{i}. {title}\n"
                if href:
                    result += f"   🔗 {href}\n"
                result += "\n"

        return result

    except requests.exceptions.ConnectionError:
        return "❌ Нет соединения с интернетом."
    except requests.exceptions.Timeout:
        return "❌ Сайт не отвечает. Попробуй позже."
    except Exception as e:
        return f"❌ Ошибка при скрапинге: {e}"