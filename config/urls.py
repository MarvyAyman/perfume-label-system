"""
config/urls.py — project-level URL configuration.

i18n_patterns() automatically prefixes every URL below with the active
language code (/ar/..., /en/..., /de/...). LocaleMiddleware picks the
right language from that prefix, then the user's saved choice, then the
browser's Accept-Language header - no app code changes needed to add a
language later.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Not translated: the language-switcher POST target itself.
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='labels/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('labels.urls')),
    prefix_default_language=True,
)
