import stripe
from django import forms
from django.contrib.auth.forms import UserCreationForm
from user.models import User
from .models import ShippingAddress, Create_Card, ProductReview


# Reordering Form and View.

class PositionForm(forms.Form):
    position = forms.CharField()


class ProductReview(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = '__all__'


class Shipping_Form(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = '__all__'


class Create_CardForm(forms.ModelForm):
    class Meta:
        model = Create_Card
        fields = '__all__'


#  Signup form
class NewUserForm(UserCreationForm):
    # email = forms.EmailField(required=True)
    # email = EmailField(widget=forms.EmailField(attrs={"autofocus": True}))
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            customer_id = stripe.Customer.create(
                description=self.cleaned_data['username'],
                email=self.cleaned_data['email'])
            user.stripe_Customer_id = customer_id.id
            user.save()
        return user
    # widgets = {
    #         'email': forms.EmailInput(attrs={'class': 'form-control'}),
    #     }
    # widgets = {
    #         'email': forms.EmailField(attrs={'class':'form-control'}),
    # }    
