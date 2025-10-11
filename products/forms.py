from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                    "class": "w-20 border rounded-lg px-2 py-1"
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full border rounded-lg px-3 py-2"
                }
            ),
        }


