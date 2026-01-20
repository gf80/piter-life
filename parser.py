import json
import requests
import os
import re
from pathlib import Path

def sanitize_filename(filename):
    """Очистка имени файла от недопустимых символов"""
    # Удаляем недопустимые символы для имен файлов
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Заменяем пробелы на подчеркивания
    filename = filename.replace(' ', '_')
    # Укорачиваем слишком длинные имена
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def download_image(url, filepath, max_retries=3):
    """Скачивание изображения с обработкой ошибок"""
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"  ✓ Скачано: {os.path.basename(filepath)} ({len(response.content)} байт)")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Попытка {attempt + 1}/{max_retries} для {url}: {e}")
            if attempt < max_retries - 1:
                continue
            return False
    
    return False

def main():
    with open("info.json", 'r', encoding='utf-8') as file:
        info = json.load(file)

    categories = info["payload"].get("categories", [])
    
    # Базовый путь для сохранения
    base_path = Path("Изображения/ПитерЛайф")
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Статистика
    stats = {
        'total_categories': 0,
        'total_items': 0,
        'successful_downloads': 0,
        'failed_downloads': 0,
        'categories': {}
    }
    
    # Пропускаемые категории
    skip_categories = ["Выбор пользователей", "Что нового", "Акции"]
    
    for category in categories:
        category_name = category.get("name")
        if not category_name or category_name in skip_categories:
            continue
        
        stats['total_categories'] += 1
        stats['categories'][category_name] = {
            'items_processed': 0,
            'successful': 0,
            'failed': 0
        }
        
        print(f'\n{"="*60}')
        print(f'КАТЕГОРИЯ: {category_name}')
        print(f'{"="*60}')
        
        # Создаем папку для категории
        category_path = base_path / sanitize_filename(category_name)
        category_path.mkdir(exist_ok=True)
        
        items = category.get("items", [])
        category_stats = stats['categories'][category_name]
        
        for item in items:
            # Проверяем доступность товара
            if not item.get("available", True):
                continue
            
            item_name = item.get("name")
            if not item_name:
                continue
            
            stats['total_items'] += 1
            category_stats['items_processed'] += 1
            
            # Получаем описание
            item_description = item.get("descriptions", [])
            if len(item_description) > 1:
                description = item_description[1]["text"]
            else:
                description = item.get("description", "")
            
            # Получаем URL изображения
            item_picture = item.get("picture")
            if not item_picture:
                print(f"  ✗ {item_name} - нет изображения")
                category_stats['failed'] += 1
                stats['failed_downloads'] += 1
                continue
            
            url_picture = "https://eda.yandex.ru" + item_picture['uri'].replace('{w}x{h}', '600x600')
            
            # Получаем вес
            item_weight = item.get("weight", "N/A")
            
            # Формируем имя файла
            safe_name = sanitize_filename(item_name)
            
            # Определяем расширение файла
            if url_picture.endswith('.jpeg') or url_picture.endswith('.jpg'):
                extension = '.jpg'
            elif url_picture.endswith('.png'):
                extension = '.png'
            elif url_picture.endswith('.webp'):
                extension = '.webp'
            else:
                # Определяем по Content-Type или используем jpg по умолчанию
                extension = '.jpg'
            
            filename = f"{safe_name}{extension}"
            filepath = category_path / filename
            
            # Если файл уже существует, добавляем суффикс
            counter = 1
            original_filepath = filepath
            while filepath.exists():
                filename = f"{safe_name}_{counter}{extension}"
                filepath = category_path / filename
                counter += 1
            
            # Выводим информацию о товаре
            print(f'\n{category_stats["items_processed"]}. {item_name}')
            print(f'   Описание: {description[:80]}...' if len(description) > 80 else f'   Описание: {description}')
            print(f'   Вес: {item_weight}')
            print(f'   URL: {url_picture}')
            
            # Скачиваем изображение
            if download_image(url_picture, filepath):
                category_stats['successful'] += 1
                stats['successful_downloads'] += 1
            else:
                category_stats['failed'] += 1
                stats['failed_downloads'] += 1
        
        # Выводим статистику по категории
        print(f'\n{"-"*40}')
        print(f'Итого по категории "{category_name}":')
        print(f'  Обработано товаров: {category_stats["items_processed"]}')
        print(f'  Успешно скачано: {category_stats["successful"]}')
        print(f'  Не удалось: {category_stats["failed"]}')
    
    # Общая статистика
    print(f'\n{"="*60}')
    print('ОБЩАЯ СТАТИСТИКА:')
    print(f'{"="*60}')
    print(f'Всего категорий: {stats["total_categories"]}')
    print(f'Всего товаров: {stats["total_items"]}')
    print(f'Успешно скачано изображений: {stats["successful_downloads"]}')
    print(f'Не удалось скачать: {stats["failed_downloads"]}')
    
    # Детальная статистика по категориям
    print(f'\nДЕТАЛИ ПО КАТЕГОРИЯМ:')
    for category_name, category_stats in stats['categories'].items():
        success_rate = (category_stats['successful'] / category_stats['items_processed'] * 100) if category_stats['items_processed'] > 0 else 0
        print(f'  {category_name}: {category_stats["successful"]}/{category_stats["items_processed"]} ({success_rate:.1f}%)')
    
    # Сохраняем статистику в файл
    stats_path = base_path / "статистика.txt"
    with open(stats_path, 'w', encoding='utf-8') as f:
        f.write(f"СТАТИСТИКА СКАЧИВАНИЯ ИЗОБРАЖЕНИЙ\n")
        f.write(f"="*50 + "\n")
        f.write(f"Всего категорий: {stats['total_categories']}\n")
        f.write(f"Всего товаров: {stats['total_items']}\n")
        f.write(f"Успешно скачано: {stats['successful_downloads']}\n")
        f.write(f"Не удалось: {stats['failed_downloads']}\n\n")
        
        f.write(f"ПО КАТЕГОРИЯМ:\n")
        for category_name, category_stats in stats['categories'].items():
            success_rate = (category_stats['successful'] / category_stats['items_processed'] * 100) if category_stats['items_processed'] > 0 else 0
            f.write(f"  {category_name}: {category_stats['successful']}/{category_stats['items_processed']} ({success_rate:.1f}%)\n")
    
    print(f'\nСтатистика сохранена в: {stats_path}')
    print(f'Все изображения сохранены в папке: {base_path}')

if __name__ == "__main__":
    # Установите необходимые зависимости:
    # pip install requests
    
    main()