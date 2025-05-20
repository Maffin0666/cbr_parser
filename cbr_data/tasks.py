import requests
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from django.conf import settings
from celery import shared_task
from .models import CurrencyRate, Bank, TaskLog
from datetime import datetime, timedelta
from django.utils import timezone
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

@shared_task
def load_currency_rates():
    task_log = TaskLog.objects.create(task_type='currency')
    
    try:
        url = getattr(settings, 'CBR_CURRENCY_URL', 'https://www.cbr.ru/scripts/XML_daily.asp')
        response = requests.get(url)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        date_str = root.attrib['Date']
        conversion_date = datetime.strptime(date_str, '%d.%m.%Y').date()
        
        count = 0
        for valute in root.findall('Valute'):
            from_currency = valute.find('CharCode').text
            to_currency = 'RUB'  # Все курсы к рублю
            value = valute.find('Value').text.replace(',', '.')
            nominal = int(valute.find('Nominal').text)
            conversion_rate = float(value) / nominal
            
            CurrencyRate.objects.update_or_create(
                from_currency=from_currency,
                to_currency=to_currency,
                conversion_date=conversion_date,
                defaults={
                    'conversion_type': 'DAILY',
                    'conversion_rate': conversion_rate,
                    'status_code': 'ACTIVE',
                    'last_update_date': timezone.now(),
                    'last_update_by': 'SYSTEM',
                    'last_update_login': 'AUTO_IMPORT'
                }
            )
            count += 1
        
        task_log.success = True
        task_log.items_processed = count
        task_log.details = f"Successfully loaded {count} currency rates for {conversion_date}"
    except Exception as e:
        task_log.success = False
        task_log.details = f"Error loading currency rates: {str(e)}"
        logger.error(f"Error in load_currency_rates: {str(e)}", exc_info=True)
    finally:
        task_log.finished_at = timezone.now()
        task_log.save()
    
    return task_log.success



@shared_task
def load_banks_data():
    task_log = TaskLog.objects.create(task_type='banks')
    NS = {'ns': 'urn:cbr-ru:ed:v2.0'}  # Пространство имен XML

    try:
        today = datetime.now().strftime('%Y%m%d')
        base_url = 'https://www.cbr.ru/vfs/mcirabis/BIKNew/'
        filename = f'{today}ED01OSBR.zip'
        url = urljoin(base_url, filename)
        response = requests.get(url)
        if response.status_code == 404:
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            filename = f'{yesterday}ED01OSBR.zip'
            url = urljoin(base_url, filename)
            response = requests.get(url)
        response.raise_for_status()
        
        with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
            xml_files = [f for f in zip_file.namelist() if f.endswith('.xml')]
            if not xml_files:
                raise ValueError("No XML files found in the archive")
            
            xml_filename = xml_files[0]  # Сохраняем имя файла для CBRFFILE
            
            with zip_file.open(xml_filename) as xml_file:
                raw_data = xml_file.read()
                
                xml_content = raw_data.decode('windows-1251')
                logger.info(f"Successfully decoded XML with windows-1251.")                
                
                root = ET.fromstring(xml_content)
            
            # Получаем общие данные из корня документа
            creation_date = root.get('CreationDateTime', '')[:10]  # Берем только дату без времени
            ed_author = root.get('EDAuthor', '')
            
            count = 0
            for entry in root.findall('.//ns:BICDirectoryEntry', NS):
                bic = entry.get('BIC')
                participant_info = entry.find('ns:ParticipantInfo', NS)
                
                if participant_info is None:
                    continue
                
                # Получаем основной корр. счет (KSNP)
                ksnps = [acc.get('Account') for acc in entry.findall('ns:Accounts', NS)]
                ksnp = ksnps[0] if ksnps else ''
                
                Bank.objects.update_or_create(
                    bic=bic,
                    defaults={
                        'pzn': participant_info.get('PtType', ''),
                        'rgn': participant_info.get('Rgn', ''),
                        'ind': participant_info.get('Ind', ''),
                        'tnp': participant_info.get('Tnp', ''),
                        'nnp': participant_info.get('Nnp', ''),
                        'adr': participant_info.get('Adr', ''),
                        'namep': participant_info.get('NameP', ''),
                        'newnum': bic,
                        'regn': participant_info.get('RegN', ''),
                        'ksnp': ksnp,  # Первый корр. счет из списка
                        'datein': participant_info.get('DateIn', ''),
                        'cbrfdate': creation_date,
                        'cbrffile': xml_filename, 
                        'crc7': participant_info.get('UID', ''),
                        'import_date': timezone.now(),
                        'json_data': {
                            'ed_author': ed_author,
                            'accounts': [acc.attrib for acc in entry.findall('ns:Accounts', NS)],
                            'participant_info': participant_info.attrib,
                            'source_encoding': 'Windows-1251'
                        }
                    }
                )
                count += 1
        
        task_log.success = True
        task_log.items_processed = count
        task_log.details = f"Successfully loaded {count} bank records"
    except Exception as e:
        task_log.success = False
        task_log.details = f"Error loading banks data: {str(e)}"
        logger.error(f"Error in load_banks_data: {str(e)}", exc_info=True)
    finally:
        task_log.finished_at = timezone.now()
        task_log.save()
    
    return task_log.success
