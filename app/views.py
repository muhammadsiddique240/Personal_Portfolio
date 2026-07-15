import logging
import markdown
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.core.mail import BadHeaderError
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .forms import ContactForm
from .models import (
    BlogCategory,
    BlogPost,
    BlogTag,
    DeveloperStat,
    ExperienceItem,
    Project,
    Resource,
    Service,
    SiteSettings,
    Testimonial,
)
from .serializers import ContactSerializer, ProjectSerializer

logger = logging.getLogger(__name__)


def _site_settings():
    return SiteSettings.objects.first() or SiteSettings(
        site_name="Muhammad Siddique",
        site_tagline="Full Stack Engineer | AI Developer | Technical Writer | SEO Learner",
        primary_email="muhammedsiddique240@gmail.com",
        github_url="https://github.com/muhammadsiddique240",
        linkedin_url="https://www.linkedin.com/in/muhammad-siddique-88aa98284/",
        twitter_url="https://x.com/sidd07mh",
        seo_description="Full Stack Engineer and AI Developer building scalable SaaS products, technical content, and developer tools.",
    )


def _base_context(request):
    return {
        "site_settings": _site_settings(),
        "canonical_url": request.build_absolute_uri(),
        "nav_links": [
            ("home", "Home"),
            ("projects", "Projects"),
            ("blog", "Blog"),
            ("resources", "Resources"),
            ("seo", "SEO"),
            ("experience", "Experience"),
            ("about", "About"),
            ("contact", "Contact"),
        ],
    }


def _wants_json(request):
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )


def _form_errors(form):
    return {field: [str(error) for error in errors] for field, errors in form.errors.items()}


def _resolve_project_descriptions(projects):
    description_overrides = {
        "duality-hotel": "Luxury hotel management platform with booking, room management, payment integration and admin analytics.",
        "duality": "Luxury hotel management platform with booking, room management, payment integration and admin analytics.",
        "school-erp": "Complete ERP system for schools including students, teachers, attendance, exams, fees and reporting dashboards.",
        "school": "Complete ERP system for schools including students, teachers, attendance, exams, fees and reporting dashboards.",
        "cad": "Custom apparel management system with product catalog, order tracking and manufacturing workflow.",
        "custom-apparel": "Custom apparel management system with product catalog, order tracking and manufacturing workflow.",
        "bookair": "Flight booking platform with fast search, booking flow, ticket management and realtime pricing integrations.",
        "bookairflight": "Flight booking platform with fast search, booking flow, ticket management and realtime pricing integrations.",
        "filler": "Provider scheduling platform with appointment booking, analytics, notifications and provider availability management.",
        "mediflow": "Clinic and practice management system with patient records, appointment queues and operational analytics.",
        "booking": "Booking and reservation platform with inventory controls, payment integrations and confirmation workflows.",
        "apparel": "E-commerce and custom design flow for apparel with mockups, catalog management and order fulfillment.",
    }

    result = []
    for p in projects:
        desc = (p.description or "").strip()
        if not desc or desc.lower().startswith("a production project focused") or desc.lower().startswith("placeholder"):
            key = (p.slug or slugify(p.title or "")).lower()
            chosen = None
            for dk, dv in description_overrides.items():
                if dk in key or dk in (p.title or "").lower():
                    chosen = dv
                    break
            if chosen:
                desc = chosen
        p.display_description = desc
        result.append(p)
    return result


def _send_contact_emails(contact):
    owner_subject = f"New Portfolio Contact from {contact.name}"
    owner_body = (
        "You have a new message from your portfolio website.\n\n"
        f"Name: {contact.name}\n"
        f"Email: {contact.email}\n"
        f"Message:\n{contact.message}"
    )
    owner_email = EmailMessage(
        subject=owner_subject,
        body=owner_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_EMAIL],
        reply_to=[contact.email],
    )
    if contact.attachment:
        owner_email.attach_file(contact.attachment.path)

    visitor_subject = "Thanks for contacting Muhammad Siddique"
    visitor_text = (
        f"Hi {contact.name},\n\n"
        "Thanks for reaching out. I received your message and will reply with a thoughtful next step soon.\n\n"
        "Best,\nMuhammad Siddique"
    )
    visitor_html = (
        f"<p>Hi {contact.name},</p>"
        "<p>Thanks for reaching out. I received your message and will reply with a thoughtful next step soon.</p>"
        "<p>Best,<br>Muhammad Siddique</p>"
    )
    visitor_email = EmailMultiAlternatives(
        subject=visitor_subject,
        body=visitor_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[contact.email],
        reply_to=[settings.CONTACT_EMAIL],
    )
    visitor_email.attach_alternative(visitor_html, "text/html")

    owner_email.send(fail_silently=False)
    visitor_email.send(fail_silently=False)


def _handle_contact_submission(request, form):
    if not form.is_valid():
        return None, False, _form_errors(form)

    contact = form.save()
    try:
        _send_contact_emails(contact)
    except (BadHeaderError, OSError, Exception) as exc:
        logger.exception("Contact email delivery failed for contact_id=%s", contact.pk)
        return contact, False, {"email": ["Message saved, but email delivery failed. I will still see it in the admin."]}
    return contact, True, {}


def home(request):
    context = _base_context(request)
    featured_projects = _resolve_project_descriptions(Project.objects.filter(is_featured=True)[:6])
    latest_posts = BlogPost.objects.filter(is_published=True).select_related("category")[:3]
    experience_preview = ExperienceItem.objects.all()[:4]
    services = Service.objects.all()[:6]
    testimonials = Testimonial.objects.filter(is_featured=True)[:3]
    stats = DeveloperStat.objects.all()[:6]
    tech_stack = [
        "Python", "Django", "Django REST Framework", "PostgreSQL", "SQLite", "Docker",
        "Redis", "Celery", "Git", "GitHub", "HTML", "CSS", "Bootstrap", "JavaScript",
        "REST API", "JWT", "Stripe", "Linux", "Render", "Railway", "Vercel", "Cloudinary",
    ]
    context.update(
        {
            "page_title": "Muhammad Siddique | Full Stack Engineer, AI Developer, Technical Writer",
            "meta_description": "Full Stack Engineer, AI Developer, and Technical Writer building scalable SaaS products, AI-powered applications, and developer content.",
            "featured_projects": featured_projects,
            "latest_posts": latest_posts,
            "experience_preview": experience_preview,
            "services": services,
            "testimonials": testimonials,
            "stats": stats,
            "tech_stack": tech_stack,
            "contact_form": ContactForm(),
            "hero_metrics": [
                ("Articles Written", "10+"),
                ("Projects Built", "25+"),
                ("Years of Learning", "3+"),
            ],
            "journey_steps": [
                "Started learning programming",
                "HTML CSS JavaScript",
                "Python",
                "Django",
                "REST APIs",
                "Docker",
                "PostgreSQL",
                "Authentication",
                "Payment Integration",
                "Celery",
                "Redis",
                "Full Stack Development",
                "AI Development",
                "Prompt Engineering",
                "SEO",
                "Technical Blogging",
                "Building personal brand",
                "Helping startups",
            ],
            "ai_stack": [
                "OpenAI", "Claude", "Gemini", "Cursor", "OpenRouter", "LangChain", "MCP",
                "Vector Databases", "Prompt Engineering", "AI Agents", "Automation",
            ],
        }
    )
    return render(request, "pages/home.html", context)


def projects_page(request):
    context = _base_context(request)
    queryset = Project.objects.all()
    projects = _resolve_project_descriptions(queryset)

    context.update(
        {
            "page_title": "Projects",
            "meta_description": "Case studies and production projects by Muhammad Siddique.",
            "projects": projects,
        }
    )
    return render(request, "pages/projects.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    gallery = []
    if project.screenshots_gallery:
        gallery = [item.strip() for item in project.screenshots_gallery.split(",") if item.strip()]
    if not gallery and project.static_image:
        gallery = [project.static_image]

    context = _base_context(request)
    context.update(
        {
            "page_title": project.meta_title or project.title,
            "meta_description": project.meta_description or project.description[:160],
            "project": project,
            "gallery_images": gallery,
        }
    )
    return render(request, "pages/project_detail.html", context)


def blog_page(request):
    context = _base_context(request)
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    tag_slug = request.GET.get("tag", "").strip()
    posts = BlogPost.objects.filter(is_published=True).select_related("category").prefetch_related("tags")
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(excerpt__icontains=query) | Q(content__icontains=query))
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    paginator = Paginator(posts.distinct(), 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    context.update(
        {
            "page_title": "Blog",
            "meta_description": "Articles on Django, APIs, AI tools, backend development, and engineering growth.",
            "page_obj": page_obj,
            "featured_posts": BlogPost.objects.filter(is_published=True, is_featured=True)[:3],
            "popular_posts": BlogPost.objects.filter(is_published=True).order_by("-views")[:5],
            "categories": BlogCategory.objects.all(),
            "tags": BlogTag.objects.all(),
            "search_query": query,
            "active_category": category_slug,
            "active_tag": tag_slug,
        }
    )
    return render(request, "pages/blog.html", context)


def blog_detail(request, slug):
    context = _base_context(request)
    post = get_object_or_404(
        BlogPost.objects.select_related("category").prefetch_related("tags"),
        slug=slug,
        is_published=True,
    )
    BlogPost.objects.filter(pk=post.pk).update(views=F("views") + 1)
    post.refresh_from_db()
    md = markdown.Markdown(
        extensions=["fenced_code", "tables", "toc", "codehilite", "sane_lists"],
        extension_configs={"toc": {"permalink": False}},
    )
    html_content = md.convert(post.content)
    toc_html = md.toc
    related_posts = (
        BlogPost.objects.filter(is_published=True, category=post.category)
        .exclude(pk=post.pk)[:3]
    )
    previous_post = (
        BlogPost.objects.filter(is_published=True, published_at__lt=post.published_at)
        .order_by("-published_at")
        .first()
    )
    next_post = (
        BlogPost.objects.filter(is_published=True, published_at__gt=post.published_at)
        .order_by("published_at")
        .first()
    )
    context.update(
        {
            "page_title": post.meta_title or post.title,
            "meta_description": post.meta_description or post.excerpt[:160],
            "post": post,
            "html_content": html_content,
            "related_posts": related_posts,
            "popular_posts": BlogPost.objects.filter(is_published=True).exclude(pk=post.pk).order_by("-views")[:5],
            "previous_post": previous_post,
            "next_post": next_post,
            "toc_html": toc_html,
            "canonical_url": request.build_absolute_uri(reverse("blog_detail", args=[post.slug])),
        }
    )
    return render(request, "pages/blog_detail.html", context)


def resources_page(request):
    context = _base_context(request)
    context.update(
        {
            "page_title": "Resources",
            "meta_description": "Curated engineering resources, cheat sheets, and practical playbooks.",
            "resources": Resource.objects.filter(file_url__isnull=False).exclude(file_url=""),
        }
    )
    return render(request, "pages/resources.html", context)


def experience_page(request):
    context = _base_context(request)
    context.update(
        {
            "page_title": "Experience",
            "meta_description": "Professional timeline covering education, freelance work, and technical leadership.",
            "timeline": ExperienceItem.objects.all(),
        }
    )
    return render(request, "pages/experience.html", context)


def about_page(request):
    context = _base_context(request)
    context.update(
        {
            "page_title": "About",
            "meta_description": "Story of a Full Stack Engineer, AI Developer, Technical Writer, and SEO learner building modern SaaS products.",
        }
    )
    return render(request, "pages/about.html", context)


def seo_page(request):
    context = _base_context(request)
    context.update(
        {
            "page_title": "SEO Learning Journey",
            "meta_description": "Technical SEO learning roadmap: Core Web Vitals, schema, indexing, and content strategy for developer publications.",
            "seo_topics": [
                "Technical SEO",
                "Core Web Vitals",
                "Google Search Console",
                "Schema Markup",
                "Semantic HTML",
                "Keyword Research",
                "Content Strategy",
                "Indexing",
                "Programmatic SEO",
                "Future Learning Roadmap",
            ],
        }
    )
    return render(request, "pages/seo.html", context)


def contact_page(request):
    context = _base_context(request)
    form = ContactForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        contact, email_sent, errors = _handle_contact_submission(request, form)
        if _wants_json(request):
            if contact and email_sent:
                return JsonResponse(
                    {
                        "ok": True,
                        "message": "Your message was sent. Check your inbox for a confirmation note.",
                        "contact_id": contact.pk,
                    },
                    status=201,
                )
            if contact:
                return JsonResponse(
                    {
                        "ok": True,
                        "email_sent": False,
                        "message": "Your message was saved, but email delivery failed. I will still see it in the admin.",
                        "contact_id": contact.pk,
                    },
                    status=202,
                )
            return JsonResponse({"ok": False, "errors": errors}, status=400)

        if contact and email_sent:
            messages.success(request, "Your message has been sent successfully. A confirmation email is on its way.")
            return redirect("contact")
        if contact:
            messages.warning(request, "Message saved, but email delivery failed. I will still see it in the admin.")
            return redirect("contact")
        messages.error(request, "Please fix the highlighted fields and try again.")

    context.update(
        {
            "page_title": "Contact",
            "meta_description": "Get in touch for backend engineering, API architecture, and SaaS development.",
            "contact_form": form,
        }
    )
    return render(request, "pages/contact.html", context)


def privacy_page(request):
    context = _base_context(request)
    context.update({"page_title": "Privacy Policy"})
    return render(request, "pages/privacy.html", context)


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def rss_feed(request):
    posts = BlogPost.objects.filter(is_published=True)[:20]
    items = []
    for post in posts:
        url = request.build_absolute_uri(reverse("blog_detail", args=[post.slug]))
        items.append(
            f"<item><title>{post.title}</title><link>{url}</link>"
            f"<description>{strip_tags(post.excerpt)}</description>"
            f"<pubDate>{timezone.localtime(post.published_at or post.created_at).strftime('%a, %d %b %Y %H:%M:%S %z')}</pubDate></item>"
        )
    body = (
        '<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel>'
        "<title>Muhammad Siddique Blog</title>"
        f"<link>{request.build_absolute_uri('/')}</link>"
        "<description>Backend engineering articles and playbooks</description>"
        + "".join(items)
        + "</channel></rss>"
    )
    return HttpResponse(body, content_type="application/rss+xml")


def custom_404(request, exception):
    context = _base_context(request)
    context.update(
        {
            "page_title": "Page not found",
            "meta_description": "The requested page was not found.",
        }
    )
    return render(request, "404.html", context=context, status=404)


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all().order_by("order", "-created_at")
    serializer_class = ProjectSerializer
    lookup_field = "slug"


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def contact_api(request):
    serializer = ContactSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"ok": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    contact = serializer.save()
    try:
        _send_contact_emails(contact)
    except (BadHeaderError, OSError, Exception):
        logger.exception("Contact API email delivery failed for contact_id=%s", contact.pk)
        return Response(
            {
                "ok": True,
                "email_sent": False,
                "message": "Message saved, but email delivery failed.",
                "contact_id": contact.pk,
            },
            status=status.HTTP_202_ACCEPTED,
        )

    return Response(
        {
            "ok": True,
            "message": "Your message was sent. Check your inbox for a confirmation note.",
            "contact_id": contact.pk,
        },
        status=status.HTTP_201_CREATED,
    )

