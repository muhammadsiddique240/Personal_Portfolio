from django.shortcuts import render
from rest_framework import viewsets
from .models import Project , Contact
from .serializers import ProjectSerializer , ContactSerializer




def home(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, "portfolio/index.html", {'projects': projects})


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

