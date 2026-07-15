from django.contrib import admin
from django.utils.html import format_html

from .models import (
    BlogCategory,
    BlogPost,
    BlogTag,
    Contact,
    DeveloperStat,
    ExperienceItem,
    Project,
    Resource,
    Service,
    SiteSettings,
    Testimonial,
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "status",
        "api_count",
        "database_used",
        "is_featured",
        "is_flagship",
        "order",
        "created_at",
        "image_preview",
    )
    list_filter = ("status", "is_featured", "is_flagship")
    search_fields = ("title", "description", "tech_stack", "problem", "solution", "architecture")
    ordering = ("order", "-created_at")
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" style="border-radius:8px;" />', obj.image.url)
        return "-"


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "attachment", "submitted_at")
    search_fields = ("name", "email", "message")
    ordering = ("-submitted_at",)


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "is_featured", "reading_time", "views", "published_at")
    list_filter = ("is_published", "is_featured", "category", "tags")
    search_fields = ("title", "excerpt", "content")
    ordering = ("-published_at", "-created_at")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    fieldsets = (
        ("Core", {"fields": ("title", "slug", "category", "tags", "cover_image", "excerpt", "content")}),
        ("Publishing", {"fields": ("is_published", "is_featured", "reading_time", "published_at", "views")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "order", "created_at")
    list_filter = ("is_featured",)
    search_fields = ("title", "description")
    ordering = ("order", "title")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(ExperienceItem)
class ExperienceItemAdmin(admin.ModelAdmin):
    list_display = ("title", "organization", "item_type", "start_date", "end_date", "is_current")
    list_filter = ("item_type", "is_current")
    search_fields = ("title", "organization", "summary", "details")
    ordering = ("-start_date", "order")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    search_fields = ("title", "short_description")
    ordering = ("order", "title")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "company", "is_featured", "order", "avatar_preview")
    list_filter = ("is_featured",)
    search_fields = ("name", "role", "company", "quote")
    ordering = ("order", "-created_at")

    @admin.display(description="Avatar")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="48" style="border-radius:999px;" />', obj.avatar.url)
        return "-"


@admin.register(DeveloperStat)
class DeveloperStatAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "order")
    search_fields = ("label", "value", "helper_text")
    ordering = ("order", "label")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "primary_email", "location", "github_url", "linkedin_url", "twitter_url")
