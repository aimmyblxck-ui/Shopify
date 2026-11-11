
from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):

    class Meta:

        model = Order

        fields = [
            'full_name',
            'email',
            'phone',
            'address'
        ]

        widgets = {

            'full_name': forms.TextInput(attrs={
                'class': 'w-full border p-3 rounded',
                'placeholder': 'Full Name'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'w-full border p-3 rounded',
                'placeholder': 'Email Address'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'w-full border p-3 rounded',
                'placeholder': 'Phone Number'
            }),

            'address': forms.Textarea(attrs={
                'class': 'w-full border p-3 rounded',
                'placeholder': 'Delivery Address',
                'rows': 4
            }),
        }

    def clean_phone(self):

        phone = self.cleaned_data.get('phone', '')

        digits = ''.join(
            char for char in phone
            if char.isdigit()
        )

        if len(digits) < 10:

            raise forms.ValidationError(
                "Phone number must contain at least 10 digits."
            )

        return phone

    def clean_email(self):

        email = self.cleaned_data.get('email')

        return email.strip().lower()
