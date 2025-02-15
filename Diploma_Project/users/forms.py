from django import forms
from .models import Team

class TeamAdminForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'

    def save(self, commit=True):
        team = super().save(commit=False)
        if commit:
            team.save()
            self.save_m2m()
        return team