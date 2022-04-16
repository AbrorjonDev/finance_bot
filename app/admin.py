from django.contrib import admin, messages
from .models import Students, Payments, StudentUser_ids, TgUserLang, BotMessages, BotHistory, Payments, Admins, Documents
import requests
from bot.database import get_user_infos_by_bot
admin.site.site_header = 'TIUE FINANCE ADMIN'
admin.site.site_title = 'TIUE FINANCE'


admin.site.disable_action('delete_selected')
@admin.action(description="Отправка остатков от бота на студенческие аккаунты")
def sending_remains(modeladmin, request, queryset):
    counter = 0
    all_obj = 0
    # all_obj = queryset.count()
    for obj in queryset:
        user_id=obj.id or None
        phones = obj.phones
        for phone in phones:
            lang = phone.bot_lang or obj.edu_lang
            message = get_user_infos_by_bot(id=user_id, lang=lang)
            if message is not None:
                r = requests.get('https://api.telegram.org/bot1617387026:AAHOITypgcGpKp6AVLdyCMBmww0Yx8WFNhE/sendMessage',
                    params = {'chat_id':phone.user_id, 'text':message}
                    )
                if r.status_code == 200:
                    counter += 1
            all_obj += 1 
    messages.add_message(request, messages.WARNING, f'Не отправлено сообщение {all_obj-counter} из {all_obj} студентов')
    messages.add_message(request, messages.INFO, f'Отправлено сообщение {counter} из {all_obj} студентов')
        

        
class StudentUser_idsInlines(admin.TabularInline):
    model = StudentUser_ids
    extra = 0
    can_delete = False


class PaymentsInline(admin.TabularInline):
    model = Payments
    extra = 0
    can_delete = False

@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ('fish', 'id_raqam', 'faculty', 'bot_used')
    list_filter = ('faculty', 'edu_lang', 'bot_used')
    search_fields = ('fish',)
    
    fieldsets = (
        ('', {
            'fields':('fish', ('contract_soums', 'date_contracted', 'id_raqam'), ('level', 'faculty', 'edu_lang', ), 'bot_used'),
            'classes':('wide',)
        }),
        # ('PHONE NUMBER', {
        #     'fields':('phone_number', ),
        #     'classes':('wide',)
        # }),
        ('PAYMENT AND REMAINS', {
            'fields':(('remains_year_begin', 'paid_percentage'), ),
            'classes':('wide',)
        })

    )

    inlines = [
        PaymentsInline,
        StudentUser_idsInlines
    ]

    actions = ['delete_selected', sending_remains]



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


@admin.register(BotHistory)
class BotHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_time')
    search_fields = ('user', 'phone')
    readonly_fields = ('date_time', 'phone', 'user')

    fieldsets = (
        ('', {
            'fields':('user', 'phone'),
                }),
        ('',{
            'fields':('message', 'date_time')
        } 
        
        )

    )



@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('student', 'soums_paid', 'date_paid')
    search_fields = ('student__fish',)

admin.site.register(Admins)

@admin.register(BotMessages)
class BotMessageAdmin(admin.ModelAdmin):
    list_display = ('admin', 'date_created')
    search_fields = ('admin__username',)
    filter_horizontal = ('students',)
    readonly_fields = ('date_created', 'date_updated',)

    fieldsets = (
        ('', {
        'fields':('message', 'admin',)
        }),
        (' MESSAGE SENT TO STUDENTS', {
            'fields':('students',)
        }),
        ('', {
            'fields':('date_created', 'date_updated',)
        })
        )
    # actions=['delete_selected']

    def save_model(self, request, obj, form, change):
        obj.admin = request.user
        return super(BotMessageAdmin, self).save_model(request, obj, form, change)

admin.site.register(StudentUser_ids)