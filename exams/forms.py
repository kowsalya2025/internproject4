
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Subject, Exam, Question, Choice

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES)
    phone = forms.CharField(max_length=15, required=False)
    roll_number = forms.CharField(max_length=20, required=False)
    department = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type', 'phone', 'roll_number', 'department']


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


# forms.py - Update ExamForm
class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'subject', 'description', 'duration', 'total_marks', 
                  'passing_marks', 'difficulty', 'start_time', 'end_time']
                  # Removed 'is_active' from here
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        self.fields['duration'].initial = 60  # 60 minutes default
        self.fields['total_marks'].initial = 100
        self.fields['passing_marks'].initial = 40


# forms.py
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'marks', 'order', 'question_image']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter the question...'}),
            'marks': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'order': forms.NumberInput(attrs={'min': 1, 'max': 100}),
        }
        help_texts = {
            'order': 'Leave as 0 for auto-numbering',
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']
        widgets = {
            'choice_text': forms.TextInput(attrs={'class': 'form-control'}),
        }

from django import forms
from django.contrib.auth.models import User

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

