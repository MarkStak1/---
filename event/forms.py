import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'example@mail.ru'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Введите логин',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        for name in ('password1', 'password2'):
            self.fields[name].widget.attrs.update({
                'class': 'form-input',
                'placeholder': '••••••••',
            })
            self.fields[name].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Введите логин',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': '••••••••',
        })


class PaymentForm(forms.Form):
    cardholder = forms.CharField(
        label='Имя на карте',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'IVAN IVANOV',
            'autocomplete': 'cc-name',
        }),
    )
    card_number = forms.CharField(
        label='Номер карты',
        min_length=16,
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '0000 0000 0000 0000',
            'autocomplete': 'cc-number',
            'inputmode': 'numeric',
        }),
    )
    expiry = forms.CharField(
        label='Срок действия',
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'MM/YY',
            'autocomplete': 'cc-exp',
        }),
    )
    cvv = forms.CharField(
        label='CVV',
        min_length=3,
        max_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '•••',
            'autocomplete': 'cc-csc',
            'inputmode': 'numeric',
        }),
    )

    def clean_cardholder(self):
        name = self.cleaned_data['cardholder'].strip()
        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-]+$', name):
            raise forms.ValidationError('Укажите имя латиницей или кириллицей')
        return name.upper()

    def clean_card_number(self):
        number = re.sub(r'\s+', '', self.cleaned_data['card_number'])
        if not number.isdigit() or len(number) != 16:
            raise forms.ValidationError('Номер карты должен содержать 16 цифр')
        return number

    def clean_expiry(self):
        expiry = self.cleaned_data['expiry'].strip()
        if not re.match(r'^(0[1-9]|1[0-2])/\d{2}$', expiry):
            raise forms.ValidationError('Формат: MM/YY')
        return expiry

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            raise forms.ValidationError('CVV должен содержать 3 или 4 цифры')
        return cvv
