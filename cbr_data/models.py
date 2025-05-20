from django.db import models
from django.utils import timezone
from datetime import date
from decimal import Decimal

# Create your models here.


class CurrencyRate(models.Model):
    CONVERSION_TYPES = [
        ('DAILY', 'Ежедневный курс'),
        ('WEEKLY', 'Еженедельный курс'),
        ('MONTHLY', 'Ежемесячный курс'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Активный'),
        ('HISTORICAL', 'Исторический'),
        ('DELETED', 'Удален'),
    ]

    from_currency = models.CharField(max_length=3, default="USD", verbose_name="Из валюты")
    to_currency = models.CharField(max_length=3, default='RUB', verbose_name="В валюту")
    conversion_date = models.DateField(default=date.today, verbose_name="Дата курса")
    conversion_type = models.CharField(
        max_length=7,
        choices=CONVERSION_TYPES,
        default='DAILY',
        verbose_name="Тип курса"
    )
    conversion_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=Decimal('1.0'),
        verbose_name="Курс обмена"
    )
    status_code = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        verbose_name="Статус"
    )
    creation_date = models.DateTimeField(default=timezone.now, editable=False, verbose_name="Дата создания")
    created_by = models.CharField(
        max_length=30,
        default='SYSTEM',
        verbose_name="Кем создано"
    )
    last_update_date = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    last_update_by = models.CharField(
        max_length=30,
        default='SYSTEM',
        verbose_name="Кем обновлено"
    )
    last_update_login = models.CharField(
        max_length=30,
        default='AUTO_IMPORT',
        verbose_name="Логин обновления"
    )

    class Meta:
        verbose_name = "Курс валюты"
        verbose_name_plural = "Курсы валют"
        unique_together = ('from_currency', 'to_currency', 'conversion_date')
        ordering = ['-conversion_date', 'from_currency']

    def __str__(self):
        return f"{self.from_currency}->{self.to_currency} ({self.conversion_date}): {self.conversion_rate}"


class Bank(models.Model):
    bic = models.CharField(max_length=9, primary_key=True, verbose_name="БИК")
    pzn = models.CharField(max_length=4, blank=True, verbose_name="Признак участника")
    rgn = models.CharField(max_length=4, blank=True, verbose_name="Регион")
    ind = models.CharField(max_length=18, blank=True, verbose_name="Индекс")
    tnp = models.CharField(max_length=15, blank=True, verbose_name="Тип населенного пункта")
    nnp = models.CharField(max_length=50, blank=True, verbose_name="Населенный пункт")
    adr = models.TextField(blank=True, verbose_name="Адрес")
    namep = models.CharField(max_length=255, blank=True, verbose_name="Наименование")
    newnum = models.CharField(max_length=12, blank=True, verbose_name="Новый номер")
    regn = models.CharField(max_length=18, blank=True, verbose_name="Рег. номер")
    ksnp = models.CharField(max_length=30, blank=True, verbose_name="Корр. счет")
    datein = models.CharField(max_length=10, blank=True, verbose_name="Дата включения")
    cbrfdate = models.CharField(max_length=10, blank=True, verbose_name="Дата файла ЦБ")
    cbrffile = models.CharField(max_length=100, blank=True, verbose_name="Имя файла")
    crc7 = models.CharField(max_length=25, blank=True, verbose_name="UID")
    import_date = models.DateTimeField(default=timezone.now, verbose_name="Дата импорта")
    json_data = models.JSONField(default=dict, verbose_name="Доп. данные")

    class Meta:
        verbose_name = "Банк"
        verbose_name_plural = "Банки"
        ordering = ['namep']

    def __str__(self):
        return f"{self.bic} - {self.namep}"


class TaskLog(models.Model):
    TASK_CHOICES = [
        ('currency', 'Загрузка курсов валют'),
        ('banks', 'Загрузка данных банков'),
    ]
    
    task_type = models.CharField(max_length=10, choices=TASK_CHOICES, verbose_name='Тип задачи')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Время начала')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='Время завершения')
    success = models.BooleanField(default=False, verbose_name='Успешно')
    details = models.TextField(blank=True, null=True, verbose_name='Детали выполнения')
    items_processed = models.IntegerField(default=0, verbose_name='Обработано записей')

    class Meta:
        verbose_name = 'Лог задачи'
        verbose_name_plural = 'Логи задач'

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.started_at} ({'Успешно' if self.success else 'Ошибка'})"