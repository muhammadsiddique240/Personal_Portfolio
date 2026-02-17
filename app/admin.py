from django.contrib import admin

# Register your models here.
from .models import Project, Contact

admin.site.register(Project)
admin.site.register(Contact)
