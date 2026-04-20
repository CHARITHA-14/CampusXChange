# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserRegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    course = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    year = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    branch = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']  # ✅ remove invalid fields
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Activate user immediately so they can log in without email verification
        user.is_active = True

        # Save email
        user.email = self.cleaned_data['email']

        # Save full name into first_name
        user.first_name = self.cleaned_data['full_name']

        if commit:
            user.save()
            # Save Profile fields and mark as verified
            profile, created = Profile.objects.get_or_create(user=user)
            profile.course = self.cleaned_data['course']
            profile.year = self.cleaned_data['year']
            profile.branch = self.cleaned_data['branch']
            profile.is_verified = True
            profile.save()

        return user

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['course', 'year', 'branch', 'phone_number', 'location', 'bio', 'profile_picture']
        widgets = {
            'course': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Science'}),
            'year': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select Year'),
                ('1st Year', '1st Year'),
                ('2nd Year', '2nd Year'),
                ('3rd Year', '3rd Year'),
                ('4th Year', '4th Year'),
                ('Graduate', 'Graduate'),
                ('Post Graduate', 'Post Graduate'),
            ]),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Computer Science Engineering'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9876543210'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mumbai, Maharashtra'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself...'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }