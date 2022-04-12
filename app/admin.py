from django.contrib import admin, messages
from .models import Students, Payments, TgUserLang, BotHistory, Payments, Admins, Documents
import requests
from bot.database import get_user_infos_by_bot
admin.site.site_header = 'TIUE FINANCE ADMIN'
admin.site.site_title = 'TIUE FINANCE'



@admin.action(description="Отправка остатков от бота на студенческие аккаунты")
def sending_remains(modeladmin, request, queryset):
    counter = 0
    all_obj = queryset.count()
    for obj in queryset:
        user_id=obj.user_id or None
        lang = obj.bot_lang or obj.edu_lang
        message = get_user_infos_by_bot(user_id=user_id, lang=lang)
        if message is not None:
            r = requests.get('https://api.telegram.org/bot5001994350:AAGxGPmysy27ArnBKaQlTVktcdblCPTGJCA/sendMessage',
                params = {'chat_id':user_id, 'text':message}
                )
            print('Status code: ', r.status_code)
            if r.status_code == 200:
                counter += 1
        else:
            messages.add_message(request, messages.WARNING, f'Не отправлено сообщение {obj.fish} из-за того, что он не использует бот-сервис')

    messages.add_message(request, messages.INFO, f'Отправлено сообщение {counter} из {all_obj} студентов')
        

        


class PaymentsInline(admin.TabularInline):
    model = Payments
    extra = 0
    can_delete = False

@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ('fish', 'id_raqam', 'faculty', 'phone_number', 'bot_used')
    list_filter = ('faculty', 'edu_lang', 'bot_used')
    search_fields = ('fish','phone_number')
    
    fieldsets = (
        ('', {
            'fields':('fish', ('contract_soums', 'date_contracted', 'id_raqam'), ('level', 'faculty', 'edu_lang', ), 'bot_used'),
            'classes':('wide',)
        }),
        ('PHONE NUMBER', {
            'fields':('phone_number', ),
            'classes':('wide',)
        }),
        ('PAYMENT AND REMAINS', {
            'fields':(('remains_year_begin', 'paid_percentage'), ),
            'classes':('wide',)
        })

    )

    inlines = [
        PaymentsInline
    ]

    actions = [sending_remains]



@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('FILE', {
            'fields':('document', 'by_admin'),
            'classes':('wide',),
        }),
        ('DATES', {
            'fields':(('date_created', 'date_updated'),)
        })
    )
    readonly_fields = ['by_admin', 'date_created', 'date_updated']
    
    def save_model(self, request, obj, form, change):
        obj.by_admin = request.user
        super().save_model(request, obj, form, change)


admin.site.register(BotHistory)

@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('student', 'soums_paid', 'date_paid')
    search_fields = ('student',)

admin.site.register(Admins)
