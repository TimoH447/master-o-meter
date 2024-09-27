from django import forms
from .models import Timers

class PomodoroForm(forms.ModelForm):
  class Meta:
      model = Timers
      fields = ['title','hours','minutes','seconds','category','priority']
      widgets = {
          'title': forms.TextInput(attrs={'required': 'required'}),
          'hours': forms.NumberInput(attrs={'required': 'required'}),
          'minutes': forms.NumberInput(attrs={'required': 'required'}),
          'seconds': forms.NumberInput(attrs={'required': 'required'}),
          'category': forms.TextInput(attrs={'required': 'required'}),
          'priority': forms.NumberInput(attrs={'required': 'required'}),
      }

  def clean(self):
      cleaned_data = super().clean()
      hours = cleaned_data.get('hours', 0)
      minutes = cleaned_data.get('minutes', 0)
      seconds = cleaned_data.get('seconds', 0)

      if hours < 0 or minutes < 0 or seconds < 0:
          raise forms.ValidationError("Hours, minutes, and seconds must be non-negative.")

      return cleaned_data
