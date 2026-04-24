# parse_all_news.py
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser as date_parser
from database import SessionLocal
from models import News as DBNews

def parse_kb_csu_news_all():
    base_url = "http://kb.csu.ru/index.php/news"
    db = SessionLocal()
    offset = 0
    total_added = 0
    max_pages = 100

    while offset < max_pages * 4:
        url = f"{base_url}?start={offset}" if offset > 0 else base_url
        print(f"📄 Загрузка: {url}")

        try:
            resp = httpx.get(url, timeout=10, follow_redirects=True)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            # 🔍 Ищем элементы новостей в блоге
            # Новости находятся в div с классом "item column-1"
            news_items = soup.select('div.item.column-1')
            
            if not news_items:
                # Альтернативный селектор, если структура другая
                news_items = soup.select('div.blog div.items-row div.item')
                
            if not news_items:
                print("⏹️ Новостей больше нет.")
                break

            added_on_page = 0
            for item in news_items:
                try:
                    # Заголовок и ссылка
                    header = item.select_one('div.page-header h2[itemprop="name"] a')
                    if not header:
                        # Пробуем найти заголовок другим способом
                        header = item.select_one('h2 a')
                    
                    if not header:
                        continue
                    
                    title = header.get_text(strip=True)
                    link = header.get('href')
                    
                    if not link:
                        continue

                    # Абсолютный URL
                    if link.startswith('/'):
                        link = 'http://kb.csu.ru' + link
                    elif not link.startswith('http'):
                        link = 'http://kb.csu.ru/' + link

                    # Проверка дубликата
                    exists = db.query(DBNews).filter(DBNews.external_link == link).first()
                    if exists:
                        continue

                    # Дата публикации
                    pub_date = datetime.utcnow()
                    time_tag = item.select_one('time[datetime]')
                    if time_tag and time_tag.get('datetime'):
                        try:
                            pub_date = date_parser.parse(time_tag['datetime'])
                        except Exception as e:
                            print(f"⚠️ Не удалось распарсить дату: {time_tag.get('datetime')} | {e}")

                    # Контент новости
                    content = ""
                    
                    # Ищем параграфы внутри item после dl.article-info
                    article_info = item.select_one('dl.article-info')
                    if article_info:
                        # Берем все параграфы после dl.article-info
                        content_parts = []
                        for p in item.find_all('p'):
                            text = p.get_text(strip=True)
                            if text and 'Published:' not in text:
                                content_parts.append(text)
                        
                        if content_parts:
                            content = ' '.join(content_parts)
                    
                    # Если не нашли через параграфы, пробуем другой способ
                    if not content:
                        # Ищем любой текст после dl.article-info
                        article_info = item.select_one('dl.article-info')
                        if article_info:
                            for element in article_info.find_next_siblings():
                                if element.name == 'p':
                                    text = element.get_text(strip=True)
                                    if text:
                                        content_parts.append(text)
                            
                            if content_parts:
                                content = ' '.join(content_parts)

                    # Сохраняем новость
                    news = DBNews(
                        title=title,
                        content=content[:500] if content else "",  # Ограничиваем длину
                        date=pub_date,
                        external_link=link
                    )
                    db.add(news)
                    added_on_page += 1
                    print(f"  ➕ Добавлено: {title[:50]}...")
                    
                except Exception as e:
                    print(f"❌ Ошибка при обработке новости: {e}")
                    continue

            db.commit()
            total_added += added_on_page
            print(f"✅ На странице добавлено: {added_on_page} новостей")

            # Проверяем наличие пагинации для определения конца
            pagination = soup.select('ul.pagination-list li a[title]')
            if not pagination or offset >= 44:  # 44 = (12 страниц - 1) * 4
                print("⏹️ Достигнут конец списка новостей.")
                break

            offset += 4

        except httpx.TimeoutException:
            print(f"❌ Таймаут при загрузке {url}")
            break
        except Exception as e:
            print(f"❌ Ошибка при загрузке {url}: {e}")
            break

    db.close()
    print(f"🎉 Всего добавлено: {total_added} новостей")

if __name__ == "__main__":
    parse_kb_csu_news_all()