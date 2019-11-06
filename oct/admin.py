from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

class Competition_Admin(admin.ModelAdmin):
    list_display = ['name', 'com_id', 'game_name']
    list_filter = ['game_name']


class BookmarkerAdmin(ImportExportModelAdmin):
    pass


admin.site.register(Bookmarker, BookmarkerAdmin)
admin.site.register(Game)
admin.site.register(Competition, Competition_Admin)