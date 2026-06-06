from django.contrib import admin
from django.urls import path, include
from api.views import frontend_view


# ADMIN BRANDING
admin.site.site_header = "ScamDetector Admin"
admin.site.site_title = "ScamDetector Portal"
admin.site.index_title = "Welcome to ScamDetector Dashboard"


urlpatterns = [

    # DJANGO ADMIN
    path('admin/', admin.site.urls),

    # API
    path('api/', include('api.urls')),

    # FRONTEND PAGES
    path('', frontend_view, {'page': 'login'}),

    path('login', frontend_view, {'page': 'login'}),

    path('register', frontend_view, {'page': 'register'}),

    path('index', frontend_view, {'page': 'index'}),

    path('dashboard', frontend_view, {'page': 'dashboard'}),

]