from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import BlogCategory, BlogPost, Contact, Project


class CorePageTests(TestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_projects_page_renders(self):
        Project.objects.create(
            title="Test Project",
            description="Testing project render",
            tech_stack="Python, Django",
        )
        response = self.client.get(reverse("projects"))
        self.assertContains(response, "Test Project")

    def test_contact_submission_creates_contact(self):
        response = self.client.post(
            reverse("contact"),
            {"name": "Test User", "email": "test@example.com", "message": "Hello from tests", "honeypot": ""},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 1)

    def test_project_api_contract(self):
        Project.objects.create(
            title="API Project",
            description="API contract test",
            tech_stack="Python, Django",
        )
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(len(payload) >= 1)
        first = payload[0]
        self.assertIn("title", first)
        self.assertIn("description", first)
        self.assertIn("tech_stack", first)

    def test_seo_page_renders(self):
        response = self.client.get(reverse("seo"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SEO Learning Journey")

    def test_legacy_project_api_still_works(self):
        Project.objects.create(
            title="Legacy API Project",
            description="Legacy API contract test",
            tech_stack="Python, Django",
        )
        response = self.client.get("/api/Project/")
        self.assertEqual(response.status_code, 200)

    def test_contact_ajax_submission_saves_and_sends_emails(self):
        response = self.client.post(
            reverse("contact"),
            {"name": "Ajax User", "email": "ajax@example.com", "message": "Hello from ajax", "honeypot": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(Contact.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 2)

    def test_contact_api_validation(self):
        response = self.client.post(reverse("contact_api"), {"name": "Bot", "honeypot": "filled"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Contact.objects.count(), 0)


class BlogTests(TestCase):
    def setUp(self):
        category = BlogCategory.objects.create(name="Django")
        second_category = BlogCategory.objects.create(name="AI Tools")
        self.post = BlogPost.objects.create(
            title="Django test post",
            excerpt="Short excerpt",
            content="# Heading\n\nSome content",
            category=category,
            is_published=True,
            published_at=timezone.now(),
        )
        BlogPost.objects.create(
            title="AI test post",
            excerpt="AI excerpt",
            content="# AI Heading\n\nAI content",
            category=second_category,
            is_published=True,
            published_at=timezone.now(),
        )

    def test_blog_list_contains_post(self):
        response = self.client.get(reverse("blog"))
        self.assertContains(response, "Django test post")

    def test_blog_detail_increments_views(self):
        self.client.get(reverse("blog_detail", args=[self.post.slug]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 1)

    def test_blog_filter_by_category(self):
        response = self.client.get(reverse("blog"), {"category": self.post.category.slug})
        self.assertContains(response, "Django test post")
        listed_titles = [item.title for item in response.context["page_obj"].object_list]
        self.assertEqual(listed_titles, ["Django test post"])
