from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ProjectViewSet,
    contact_api,
    about_page,
    blog_detail,
    blog_page,
    contact_page,
    experience_page,
    home,
    privacy_page,
    project_detail,
    projects_page,
    resources_page,
    seo_page,
    robots_txt,
    rss_feed,
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"Project", ProjectViewSet, basename="legacy-project")

urlpatterns = [
    path("api/contact/", contact_api, name="contact_api"),
    path("api/", include(router.urls)),
    path("", home, name="home"),
    path("projects/", projects_page, name="projects"),
    path("projects/<slug:slug>/", project_detail, name="project_detail"),
    path("blog/", blog_page, name="blog"),
    path("blog/<slug:slug>/", blog_detail, name="blog_detail"),
    path("resources/", resources_page, name="resources"),
    path("seo/", seo_page, name="seo"),
    path("experience/", experience_page, name="experience"),
    path("about/", about_page, name="about"),
    path("contact/", contact_page, name="contact"),
    path("privacy/", privacy_page, name="privacy"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("feed.xml", rss_feed, name="rss_feed"),
]