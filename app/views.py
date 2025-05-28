from django.shortcuts import render
from rest_framework import viewsets
from .models import Project , Contact
from .serializers import ProjectSerializer , ContactSerializer



def home(request):
    return render(request , "portfolio/index.html")


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

