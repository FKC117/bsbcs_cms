from django import forms
from .models import Member, Speciality, ResearchInterestArea


class MembershipForm(forms.ModelForm):
    """Form for submitting/editing member information."""
    
    specialties = forms.ModelMultipleChoiceField(
        queryset=Speciality.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select one or more specialties"
    )
    
    research_interest_areas = forms.ModelMultipleChoiceField(
        queryset=ResearchInterestArea.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select one or more research interest areas"
    )
    
    class Meta:
        model = Member
        fields = [
            'name',
            'location',
            'years_of_experience',
            'profile_description',
            'image',
            'institution',
            'position',
            'specialties',
            'research_interest_areas',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, Country',
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Years of Experience',
                'min': '0',
            }),
            'profile_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Tell us about yourself, your experience, and interests...',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'institution': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Institution/Organization Name',
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job Title/Position',
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # Add custom validation if needed
        return cleaned_data
