import os

from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, default="Muhammad Siddique")
    site_tagline = models.CharField(
        max_length=160,
        default="Full Stack Engineer | AI Developer | Technical Writer | SEO Learner",
    )
    primary_email = models.EmailField(default="muhammedsiddique240@gmail.com")
    location = models.CharField(max_length=120, blank=True, default="Remote")
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    resume_url = models.URLField(blank=True)
    seo_description = models.TextField(blank=True)
    newsletter_cta = models.CharField(
        max_length=180,
        default="Get practical full stack, AI, and SEO learning insights in your inbox.",
    )

    def __str__(self):
        return self.site_name


class Project(TimeStampedModel):
    STATUS_CHOICES = (
        ("active", "Active"),
        ("maintenance", "Maintenance"),
        ("archived", "Archived"),
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField()
    case_study = models.TextField(blank=True)
    problem = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    architecture = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    github_link = models.URLField(blank=True)
    live_link = models.URLField(blank=True)
    case_study_link = models.URLField(blank=True)
    tech_stack = models.CharField(
        max_length=200,
        help_text="Comma separated technologies",
        default="Python, Django",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    is_featured = models.BooleanField(default=False)
    is_flagship = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    api_count = models.PositiveIntegerField(default=0)
    database_used = models.CharField(max_length=120, blank=True, default="PostgreSQL")
    deployment_stack = models.CharField(max_length=140, blank=True, default="Railway, Vercel")
    category = models.CharField(max_length=100, blank=True, help_text="Project category e.g. SaaS ERP")
    screenshots_gallery = models.TextField(
        blank=True,
        help_text="Primary static image filename (e.g. duality_hotel_pool.jpg) or comma-separated list.",
    )
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def tech_items(self):
        return [item.strip() for item in self.tech_stack.split(",") if item.strip()]

    @property
    def static_image(self):
        """Return the first static image filename stored in screenshots_gallery.

        Fallback behaviour:
        1. If screenshots_gallery set, return first filename.
        2. Otherwise attempt to locate a best-match image file under the project's
           static imgs directory (app/static/imgs) by matching slug or title words.
        This allows the Projects page to display images even when the DB image
        fields are empty but static screenshots exist in the repository.
        """
        # 1) explicit gallery entry in the model
        if self.screenshots_gallery:
            return self.screenshots_gallery.split(",")[0].strip()

        # 2) attempt to locate a static file by heuristics
        try:
            from django.conf import settings
        except Exception:
            settings = None

        # Build a list of candidate filenames to look for
        slug_base = (self.slug or slugify(self.title or "")).lower()
        title_base = (self.title or "").lower()
        candidates = []
        if slug_base:
            candidates += [f"{slug_base}.png", f"{slug_base}.jpg", f"{slug_base}.jpeg", f"{slug_base}_mockup.png", f"{slug_base}_dashboard.png"]
            candidates += [f"{slug_base.replace('-', '_')}.png", f"{slug_base.replace('-', '_')}.jpg"]
        # words from title
        for part in title_base.replace('-', ' ').replace('_', ' ').split():
            if len(part) > 2:
                candidates += [f"{part}.png", f"{part}.jpg"]

        # try known folder under the project (STATICFILES_DIRS includes BASE_DIR/app/static)
        possible_dirs = []
        if settings and getattr(settings, 'BASE_DIR', None):
            possible_dirs.append(os.path.join(settings.BASE_DIR, 'app', 'static', 'imgs'))
            possible_dirs.append(os.path.join(settings.BASE_DIR, 'app', 'staticfiles', 'imgs'))
            possible_dirs.append(os.path.join(settings.BASE_DIR, 'staticfiles', 'imgs'))

        # also check the app package relative path
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            possible_dirs.append(os.path.join(base_dir, 'static', 'imgs'))
        except Exception:
            pass

        # Collect actual filenames in imgs dirs and try best match
        seen_files = []
        for d in possible_dirs:
            try:
                for fn in os.listdir(d):
                    if fn.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif')):
                        seen_files.append(fn)
            except Exception:
                continue

        # Exact candidate match
        for c in candidates:
            if c in seen_files:
                return c

        # fuzzy match: prefer filename containing slug or title words
        lowered = [f.lower() for f in seen_files]
        for needle in [slug_base] + title_base.split():
            if not needle:
                continue
            for i, fname in enumerate(lowered):
                if needle in fname:
                    return seen_files[i]

        # nothing found
        return None


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    attachment = models.ImageField(upload_to="contact_attachments/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"


class BlogCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Blog categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(TimeStampedModel):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    cover_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    excerpt = models.TextField(max_length=320)
    content = models.TextField(help_text="Markdown supported content")
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
    )
    tags = models.ManyToManyField(BlogTag, blank=True, related_name="posts")
    reading_time = models.PositiveIntegerField(default=5, help_text="In minutes")
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("blog_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Resource(TimeStampedModel):
    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(max_length=280)
    file_url = models.URLField(blank=True)
    external_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ExperienceItem(TimeStampedModel):
    TYPE_CHOICES = (
        ("education", "Education"),
        ("internship", "Internship"),
        ("employment", "Professional Experience"),
        ("freelance", "Freelance"),
        ("project", "Project"),
        ("learning", "Learning Journey"),
        ("certification", "Certification"),
    )

    title = models.CharField(max_length=160)
    organization = models.CharField(max_length=160)
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="project")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    summary = models.TextField(max_length=320)
    details = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-start_date", "order"]

    def __str__(self):
        return f"{self.title} - {self.organization}"


class Service(TimeStampedModel):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    short_description = models.TextField(max_length=220)
    icon = models.CharField(max_length=60, blank=True, help_text="FontAwesome icon class")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Testimonial(TimeStampedModel):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    quote = models.TextField(max_length=420)
    avatar = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.name} - {self.role}"


class DeveloperStat(models.Model):
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=80)
    helper_text = models.CharField(max_length=120, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "label"]

    def __str__(self):
        return self.label



