from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("authentication/", include("authentication.urls")),
    path("expenses/", include("expenses.urls")),
    path("", include("expenses.urls")),
    path("income/", include("income.urls")),
    path('admin/', admin.site.urls),


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
