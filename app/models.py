from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from datetime import datetime
User = get_user_model()

class Documents(models.Model):
    document = models.FileField(upload_to='files')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    by_admin = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        ordering = ('-date_created',)

    def __str__(self):
        return self.document.name




class Students(models.Model):
    LANGUAGES = (('en','en'), ('ru', 'ru'), ('uz', 'uz'))
    EDU_LANGUAGES = (('en','инглиз'), ('ru', 'рус'), ('uz', 'uz'))
    
    fish = models.CharField(max_length=200, null=True, blank=True, verbose_name="Ф.И.Ш.")
    #contract
    id_raqam = models.IntegerField(null=True, blank=True, verbose_name="рақами")
    date_contracted = models.DateField(null=True, blank=True, verbose_name="санаси")
    contract_soums = models.IntegerField(verbose_name="сумма", null=True, blank=True,)

    level = models.CharField(max_length=30, null=True, blank=True, verbose_name="Даражаси Курс")
    faculty = models.CharField(max_length=30, null=True, blank=True, verbose_name="Йўналиши")
    edu_lang = models.CharField(max_length=20, choices=EDU_LANGUAGES, null=True, blank=True, verbose_name="Таълим тили")

    remains_year_begin = models.IntegerField( null=True, blank=True, verbose_name="Ўқув йили бошига қолдиқ")
    # remains_year_end = models.IntegerField( null=True, blank=True, verbose_name="Ўқув йили охирига қолдиқ")

    paid_percentage = models.FloatField(null=True, blank=True)

    #tg user data
    bot_used = models.BooleanField(default=False, verbose_name='Он использует бота?')

    @property
    def all_paid(self):
        payments = self.payments_set.all()
        return sum([payment.soums_paid for payment in payments])
    @property
    def phones(self):
        return self.studentuser_ids_set.all() 
    @property
    def remains_year_end(self):
        return self.contract_soums - self.all_paid

    def __str__(self):
        return self.fish
 
    # class Meta:
    #     extra_kwargs = {
    #         'all_paid':{'verbose_name':'Жами'},
    #         'remains_year_end':{'verbose_name':'Изоҳ'}
    #     }


class Payments(models.Model):

    student = models.ForeignKey(Students, on_delete=models.CASCADE)    
    #Тушум
    date_paid = models.DateField(null=True, blank=True, verbose_name="санаси")
    soums_paid = models.IntegerField(null=True, blank=True,verbose_name="сумма")

    def __str__(self):
        return self.student.fish

class BotHistory(models.Model):

    user = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.user.fish

    def save(self, *args, **kwargs):
        if not self.date_time:
            self.date_time = datetime.now()
        return super(BotHistory, self).save(*args, **kwargs)


class TgUserLang(models.Model):
    LANGUAGES = (('en','en'), ('ru', 'ru'), ('uz', 'uz'))
    
    user_id = models.CharField(max_length=30, null=True, blank=True)
    bot_lang = models.CharField(max_length=3, choices=LANGUAGES, null=True, blank=True)


class Admins(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, help_text='+998971661186')
    date_added = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.first_name or self.phone_number


class BotMessages(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    students = models.ManyToManyField(Students, null=True, blank=True)

    def __str__(self):
       return str(self.id)   #self.admin.username or 
    
    @property
    def sent_messages(self):
        if self.students.all().count()>0:
            return self.students.filter(bot_used=True).count()
        else:
            return 10

    def save(self, *args, **kwargs):
        super(BotMessages, self).save(*args, **kwargs)


        

class MessagesByStudents(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student.fish

class StudentUser_ids(models.Model):
    LANGUAGES = (('en','en'), ('ru', 'ru'), ('uz', 'uz'))

    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=100, null=True, blank=True)
    bot_lang = models.CharField(max_length=3, choices=LANGUAGES, null=True, blank=True)
    phone_number = models.CharField(max_length=100)
    bot_used = models.BooleanField(default=False, verbose_name='Он(a) использует бота?')

    class Meta:
        verbose_name = 'Phone Number'
        verbose_name_plural = 'Phone Numbers'

    def __str__(self):
        return self.student.fish

