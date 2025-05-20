import requests
import zipfile
import os
from io import BytesIO

def extract_and_read_xml_from_url(zip_url):
    # Загружаем ZIP-архив по URL
    response = requests.get(zip_url)
    response.raise_for_status()  # Проверка на успешный ответ

    # Открываем ZIP-архив из загруженных данных
    with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
        # Проходим по всем файлам в архиве
        for file_info in zip_ref.infolist():
            # Если файл является XML, извлекаем его
            if file_info.filename.endswith('.xml'):
                # Читаем содержимое XML-файла непосредственно из ZIP
                with zip_ref.open(file_info.filename) as xml_file:
                    xml_content = xml_file.read().decode('windows-1251')
                return xml_content  # Возвращаем содержимое XML-файла

    return None  # Если XML-файл не найден

# Пример использования
zip_url = 'https://www.cbr.ru/vfs/mcirabis/BIKNew/20250519ED01OSBR.zip'  # Укажите URL к вашему ZIP-файлу

try:
    content = extract_and_read_xml_from_url(zip_url)
    if content:
        print(content)  # Выводим содержимое XML-файла
    else:
        print("XML-файл не найден в архиве.")
except Exception as e:
    print(f'Ошибка: {e}')
