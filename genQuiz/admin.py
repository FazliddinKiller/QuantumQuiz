from django.contrib import admin
from .models import *

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ['user','created_at']

