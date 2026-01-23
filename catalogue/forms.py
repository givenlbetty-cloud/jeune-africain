from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    """
    Formulaire pour ajouter ou modifier une critique.
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Partagez votre avis sur ce livre...'}),
        }
        labels = {
            'rating': 'Votre note',
            'comment': 'Votre commentaire',
        }
