from django.urls import include, path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, re_path
from django.shortcuts import redirect

from .api import CheckAdmin

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

urlpatterns = [
    path('chat/', include('chat.urls')),
    path('calling/', include('calling.urls')),


    path('', RedirectView.as_view(url='/', permanent=True)),

] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)

if settings.DEBUG == 1:
    import debug_toolbar

    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls)),]
