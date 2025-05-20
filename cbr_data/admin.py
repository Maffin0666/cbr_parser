from django.contrib import admin
#from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
from .models import CurrencyRate, Bank, TaskLog

# Register your models here.


admin.site.register(CurrencyRate)
admin.site.register(Bank)
admin.site.register(TaskLog)

#admin.site.register(IntervalSchedule)
#admin.site.register(CrontabSchedule)
#admin.site.register(PeriodicTask)


