from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accounts_views.landing_page, name='landing_page'),
    path('accounts/login/', accounts_views.CustomLoginView.as_view(), name='account_login'),
    path('accounts/signup/', accounts_views.CustomSignupView.as_view(), name='account_signup'),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path("chat/", include("chat.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
