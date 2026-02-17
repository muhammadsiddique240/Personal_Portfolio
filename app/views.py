from django.shortcuts import render
from rest_framework import viewsets
from .models import Project , Contact
from .serializers import ProjectSerializer , ContactSerializer




from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

def home(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Save to database
        contact = Contact.objects.create(name=name, email=email, message=message)
        
        # Send Email notification
        subject = f"New Portfolio Contact from {name}"
        email_message = f"You have a new message from your portfolio website.\n\nName: {name}\nEmail: {email}\nMessage:\n{message}"
        
        try:
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
            messages.error(request, "There was an error sending your message. Please try again later.")

    flagship_titles = ["School Management System", "Custom Apparel Design", "Filler"]
    projects = Project.objects.exclude(title__in=flagship_titles).order_by('-created_at')
    return render(request, "portfolio/index.html", {'projects': projects})


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

