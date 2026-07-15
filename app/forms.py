from django import forms

from .models import Contact

MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024


class ContactForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Contact
        fields = ["name", "email", "message", "attachment"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your name",
                    "class": "form-input",
                    "autocomplete": "name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Your email",
                    "class": "form-input",
                    "autocomplete": "email",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "placeholder": "Tell me about your project...",
                    "class": "form-input min-h-[140px]",
                    "rows": 6,
                }
            ),
            "attachment": forms.ClearableFileInput(
                attrs={
                    "class": "form-input",
                    "accept": "image/*",
                }
            )
        }

    def clean_honeypot(self):
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError("Spam submission detected.")
        return value

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if attachment and attachment.size > MAX_ATTACHMENT_SIZE:
            raise forms.ValidationError("Attachment must be 5MB or smaller.")
        return attachment
