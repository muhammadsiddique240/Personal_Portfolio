from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app.sitemaps import BlogSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "blog": BlogSitemap,
}
handler404 = "app.views.custom_404"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("app.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)