from rest_framework import serializers

from .models import Contact, Project


class ProjectSerializer(serializers.ModelSerializer):
    tech_items = serializers.ListField(read_only=True)

    class Meta:
        model = Project
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "case_study",
            "problem",
            "solution",
            "architecture",
            "challenges",
            "lessons_learned",
            "image",
            "github_link",
            "live_link",
            "case_study_link",
            "tech_stack",
            "tech_items",
            "status",
            "is_featured",
            "is_flagship",
            "api_count",
            "database_used",
            "deployment_stack",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ContactSerializer(serializers.ModelSerializer):
    honeypot = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Contact
        fields = ("id", "name", "email", "message", "attachment", "honeypot", "submitted_at")
        read_only_fields = ("id", "submitted_at")

    def validate_honeypot(self, value):
        if value:
            raise serializers.ValidationError("Spam submission detected.")
        return value

    def validate_attachment(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Attachment must be 5MB or smaller.")
        return value

    def create(self, validated_data):
        validated_data.pop("honeypot", None)
        return super().create(validated_data)
