from django.contrib import admin
from .models import *


class Competition_Admin(admin.ModelAdmin):
    list_display = ['name', 'com_id', 'game_name']
    list_filter = ['game_name']





admin.site.register(Bookmarker)
admin.site.register(Game)
admin.site.register(Competition, Competition_Admin)