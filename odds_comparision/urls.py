
from django.contrib import admin
from django.urls import path,include
admin.site.site_header = 'Odds Comparision Tool Administration'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('oct.urls')),
]

