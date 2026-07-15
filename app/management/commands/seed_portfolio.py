from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import (
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


class Command(BaseCommand):
    help = "Seed premium portfolio dummy content"

    def handle(self, *args, **options):
        settings_obj, _ = SiteSettings.objects.get_or_create(
            id=1,
            defaults={
                "site_name": "Muhammad Siddique",
                "site_tagline": "Full Stack Engineer | AI Developer | Technical Writer | SEO Learner",
                "primary_email": "muhammedsiddique240@gmail.com",
            },
        )
        settings_obj.github_url = settings_obj.github_url or "https://github.com/muhammadsiddique240"
        settings_obj.linkedin_url = settings_obj.linkedin_url or "https://www.linkedin.com/in/muhammad-siddique-88aa98284/"
        settings_obj.twitter_url = settings_obj.twitter_url or "https://x.com/sidd07mh"
        settings_obj.save()

        categories = {}
        for name in ["Python", "Django", "AI Tools", "DevOps", "Career", "Backend Engineering"]:
            categories[name], _ = BlogCategory.objects.get_or_create(name=name)

        tags = {}
        for name in [
            "Django", "DRF", "OpenAI", "Docker", "Linux", "Git", "Redis", "Celery",
            "Deployment", "Freelancing", "Programming Tips", "SaaS", "API Design",
        ]:
            tags[name], _ = BlogTag.objects.get_or_create(name=name)

        topic_titles = [
            "Python patterns for clean backend architecture",
            "Scaling Django APIs with practical caching",
            "Designing DRF serializers for long-term maintainability",
            "Using OpenAI tools inside production Django workflows",
            "Dockerizing backend services for reliable shipping",
            "Linux commands every backend engineer should automate",
            "Git workflows for high-trust engineering teams",
            "Redis strategies for session and queue optimization",
            "Celery pipelines for asynchronous product features",
            "Deployment checklist for startup-grade Django apps",
            "Freelancing systems for technical founders",
            "Programming habits that accelerate backend growth",
            "Architecting multi-tenant SaaS with Django",
            "API reliability techniques beyond happy-path testing",
            "Career journey lessons from early engineering years",
        ]
        for idx, title in enumerate(topic_titles):
            post, _ = BlogPost.objects.get_or_create(
                title=title,
                defaults={
                    "excerpt": "Practical engineering notes focused on architecture, performance, and product outcomes.",
                    "content": (
                        f"# {title}\n\n"
                        "## Core idea\n\n"
                        "This article shares actionable practices for building scalable backend systems.\n\n"
                        "```python\n"
                        "def healthcheck(service):\n"
                        "    return {'service': service, 'status': 'ok'}\n"
                        "```\n\n"
                        "## Production checklist\n\n"
                        "- Observability\n- Security baseline\n- Performance budget\n"
                    ),
                    "category": list(categories.values())[idx % len(categories)],
                    "reading_time": 7 + (idx % 5),
                    "is_published": True,
                    "is_featured": idx < 4,
                    "published_at": timezone.now() - timedelta(days=idx * 2),
                },
            )
            post.tags.set(list(tags.values())[idx % 4 : (idx % 4) + 3])

        resource_items = [
            "Python Cheat Sheet", "Git Cheat Sheet", "Docker Commands", "Linux Commands",
            "Django Roadmap", "DRF Interview Guide", "API Design Guide", "PostgreSQL Notes",
            "VS Code Setup", "AI Productivity Guide",
        ]
        for idx, title in enumerate(resource_items):
            Resource.objects.get_or_create(
                title=title,
                defaults={
                    "description": f"Actionable and concise {title.lower()} for backend engineers.",
                    "external_url": "https://example.com/resource",
                    "is_featured": idx < 4,
                    "order": idx,
                },
            )

        services = [
            "Backend Development", "REST APIs", "SaaS Development", "Automation", "API Integration",
            "Payment Integration", "AI Integration", "Deployment", "Database Design", "Bug Fixing",
        ]
        for idx, title in enumerate(services):
            Service.objects.get_or_create(
                title=title,
                defaults={
                    "short_description": f"Professional {title.lower()} for modern digital products.",
                    "order": idx,
                },
            )

        stats = [("Products Shipped", "40+"), ("APIs Built", "80+"), ("Client Satisfaction", "98%"), ("Years Engineering", "5+")]
        for idx, (label, value) in enumerate(stats):
            DeveloperStat.objects.get_or_create(label=label, defaults={"value": value, "order": idx})

        experiences = [
            {
                "title": "Co-founder & CTO",
                "organization": "DualSync Agency",
                "item_type": "freelance",
                "start_date": date(2026, 1, 1),
                "end_date": None,
                "is_current": True,
                "summary": "Leading product engineering, client delivery, and technical strategy for agency projects.",
                "details": "",
                "order": 0,
            },
            {
                "title": "Senior Full Stack Developer",
                "organization": "Freelance & Contract",
                "item_type": "freelance",
                "start_date": date(2024, 1, 1),
                "end_date": date(2025, 12, 30),
                "is_current": False,
                "summary": "Built systems, delivered client impact, and improved platform reliability.",
                "details": "",
                "order": 1,
            },
            {
                "title": "Software Engineer",
                "organization": "Fabulous Technology Solution",
                "item_type": "employment",
                "start_date": date(2023, 1, 1),
                "end_date": date(2025, 1, 1),
                "is_current": False,
                "summary": "Started with a 3-month internship and grew into a Python Django developer role — building APIs, database layers, and production-ready backend services.",
                "details": "",
                "order": 2,
            },
            {
                "title": "Professional Certification Program",
                "organization": "Tech Skills Training",
                "item_type": "certification",
                "start_date": date(2022, 7, 1),
                "end_date": date(2022, 12, 31),
                "is_current": False,
                "summary": "Completed two intensive 3-month certification tracks covering modern frontend and backend engineering foundations.",
                "details": "",
                "order": 3,
            },
            {
                "title": "Engineering Mentorship Program",
                "organization": "Self-Driven Learning",
                "item_type": "learning",
                "start_date": date(2022, 1, 1),
                "end_date": date(2022, 12, 1),
                "is_current": False,
                "summary": "Structured self-learning path covering programming fundamentals, problem solving, and software engineering mindset.",
                "details": "",
                "order": 4,
            },
        ]
        for item in experiences:
            ExperienceItem.objects.update_or_create(
                title=item["title"],
                organization=item["organization"],
                defaults={
                    "item_type": item["item_type"],
                    "start_date": item["start_date"],
                    "end_date": item["end_date"],
                    "is_current": item["is_current"],
                    "summary": item["summary"],
                    "details": item["details"],
                    "order": item["order"],
                },
            )

        ExperienceItem.objects.filter(
            title="Backend Developer",
            organization="Fabulous Technology Solution",
        ).delete()

        ExperienceItem.objects.filter(
            title="Backend Engineer",
            organization="Fabulous Technology Solution",
        ).delete()

        testimonials = [
            ("Ayesha Khan", "Product Manager", "StartupX"),
            ("Daniel Reyes", "Founder", "Velocity Labs"),
            ("Hassan Ali", "CTO", "BuildStack"),
        ]
        for idx, entry in enumerate(testimonials):
            Testimonial.objects.get_or_create(
                name=entry[0],
                role=entry[1],
                company=entry[2],
                defaults={
                    "quote": "Muhammad brings strong backend clarity and ownership to complex product challenges.",
                    "is_featured": True,
                    "order": idx,
                },
            )

        for idx, title in enumerate(["Duality Hotel", "School ERP", "CAD - Custom Apparel Design", "BookAirFlight", "Filler - Provider Booking"]):
            Project.objects.get_or_create(
                title=title,
                defaults={
                    "description": "A production project focused on full stack reliability and smooth product workflows.",
                    "tech_stack": "Python, Django, DRF, PostgreSQL, Docker",
                    "is_featured": True,
                    "is_flagship": True,
                    "status": "active",
                    "order": idx + 1,
                },
            )

        Project.objects.update_or_create(
            title="RORAAN Collection",
            defaults={
                "description": "Authenticated sneaker and streetwear marketplace for RORAAN Archive — a Pakistan-based retailer specializing in condition-graded sneakers and modern streetwear.",
                "case_study": "Full-stack e-commerce platform with REST API backend, React 19 frontend, single-SKU inventory model, dual checkout (website payment + WhatsApp), and admin dashboard with revenue analytics.",
                "tech_stack": "Python, Django REST Framework, PostgreSQL, JWT, React 19, TypeScript, Vite, Tailwind CSS v4, Zustand, Recharts",
                "is_featured": True,
                "is_flagship": True,
                "status": "active",
                "order": 0,
                "category": "E-Commerce Marketplace",
                "database_used": "PostgreSQL",
                "deployment_stack": "Railway, Vercel",
                "screenshots_gallery": "roraan1.png,roraan2.png",
                "meta_title": "RORAAN Collection — Sneaker Marketplace",
                "meta_description": "Authenticated sneaker and streetwear marketplace built with Django REST Framework, React 19, and PostgreSQL.",
            },
        )

        self.stdout.write(self.style.SUCCESS("Portfolio dummy content has been seeded."))
