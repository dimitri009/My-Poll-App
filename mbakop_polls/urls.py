"""mbakop_polls URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from polls.views import home

handler400 = 'polls.views.bad_request'
handler403 = 'polls.views.permission_denied'
handler404 = 'polls.views.page_not_found'
handler500 = 'polls.views.server_error'

urlpatterns = [
    re_path('admin/', admin.site.urls),
    re_path(r'^polls/', include('polls.urls')),
    re_path(r'^accounts/', include('accounts.urls')),
    re_path(r'^$',home, name='home'),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += staticfiles_urlpatterns()
