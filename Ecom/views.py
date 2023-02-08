import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, FormView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import Product, Company, CheckoutCart, ShippingAddress, ProductReview, Image
from django.views.generic.edit import CreateView
from .forms import Shipping_Form, NewUserForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q
# import self as self
from django.template import context
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LogoutView

stripe.api_key = "sk_test_51MGnkUB9cJ4i47NRJUHCwwZvpfl9AV8SHzCazQiCmnvSlMO2caHLy3oORaA9Dgc3PtQmPawU0vXhm5WHHPVx33SW00NkegILHO"


# Search Results
class SearchResultsView(ListView):
    model = Product
    template_name = "search_results.html"

    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        object_list = Product.objects.filter(
            Q(name__icontains=query)
        )
        return object_list
# def Search(request):
#     query = request.GET.get('q')
#     if query:
#         products = Product.objects.filter(name__icontains=query)
#     else:
#         products = []
#     return render(request, 'search_results.html', {'products': products})


# Login
class CustomLoginView(LoginView):
    template_name = 'login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')


# Register/Signup
class RegisterFormView(CreateView):
    def get(self, request, *args, **kwargs):
        form = NewUserForm()
        return render(request=request, template_name="register.html", context={"register_form": form})

    def post(self, request, *args, **kwargs):
        global form
        if request.method == "POST":
            form = NewUserForm(request.POST)
            if form.is_valid():
                user = form.save()

                login(request, user)

                messages.success(request, "Registration successful.")
                return redirect("/login/")
            messages.error(
                request, "Unsuccessful registration. Invalid information.")
        return render(request=request, template_name="register.html", context={"register_form": form})


# Main Home Page
class HomeView(ListView):
    model = Product
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        mobile = request.GET.get('mobile', None)
        tablet = request.GET.get('tablet', None)
        A = Product.objects.filter(category=1)
        B = Product.objects.filter(category=2)
        C = Product.objects.filter(trending=True)
        D = Company.objects.all()
        if mobile is not None:
            A = Product.objects.filter(category=1, company=mobile)
        if tablet is not None:
            B = Product.objects.filter(category=2, company=tablet)
        context = {
            'mobile': A, 'trending': C, 'tablet': B, 'company': D
        }
        return render(request, self.template_name, context)


# Detail Page
class ProductDetail(DetailView):
    model = Product
    template_name = 'product_detail.html'

    def get(self, request, id, *args, **kwargs):
        p = Product.objects.get(id=id)
        st = Image.objects.filter(product_id=id)
        context = {
            'product': p, 'st': st
        }
        return render(request, self.template_name, context=context)


# Reviews or Ratings
class ProductDetail(DetailView, CreateView):
    model = Product, ProductReview
    fields = '__all__'
    template_name = 'product_detail.html'

    def get(self, request, id, *args, **kwargs):
        product = Product.objects.get(id=id)
        data = request.POST.copy()
        data.update({"product": product})
        if request.method == 'POST':
            form = ProductReview(data)
            if form.is_valid():
                form.save()
        else:
            form = ProductReview()
        reviews = ProductReview.objects.filter(product=id)
        img = Image.objects.filter(product=id)
        context = {
            'img': img, 'product': product, 'form': form, 'reviews': reviews
        }
        return render(request, self.template_name, context=context)

    def post(self, request, id, *args, **kwargs):
        product = Product.objects.get(id=id)
        data = request.POST.copy()
        w = {
            'name': data['name'],
            'title': data['title'],
            'review': data['review'],
            'rating': data['rating'],
            'product_id': id
        }
        data.update({"product_id": id})
        review = ProductReview(**w)
        review.save()
        reviews = ProductReview.objects.filter(product=id)
        img = Image.objects.filter(product=id)
        form = ProductReview()
        context = {
            'img': img, 'product': product, 'reviews': reviews, 'form': form
        }
        return render(request, self.template_name, context=context)


# Checkout Cart
class Checkoutcart(LoginRequiredMixin, ListView):
    model = CheckoutCart
    template_name = 'checkout_cart.html'

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('prod_id')
        operation = request.POST.get('operation')
        operation1 = request.POST.get('operation1')
        pro_check = CheckoutCart.objects.filter(product_id=product_id, user=request.user)
        if pro_check.exists():
            cart = CheckoutCart.objects.filter(product_id=product_id).first()
            if operation == 'decrease':
                cart.quantity -= 1
                cart.save()
                if cart.quantity == 0:
                    cart.delete()
            elif operation1 == 'increase':
                cart.quantity += 1
                cart.save()

            else:
                cart.quantity += 1
                cart.save()

        else:
            cart_item = CheckoutCart.objects.create(product_id=product_id, user=request.user)
            cart_item.save()
        product_show = CheckoutCart.objects.all()

        shipping = 150
        sub_total = 0
        total = 0
        for item in product_show:
            if item.product:
                item.pro_total = item.quantity * item.product.price
                sub_total += item.pro_total
                total = (sub_total + shipping)
                item.save()
        context = {
            'product_show': product_show,
            'sub_total': sub_total,
            'total': total,

        }
        return render(request, self.template_name, context)


# Shipping Methods
class Shipping(LoginRequiredMixin, CreateView):
    model = ShippingAddress
    form_class = Shipping_Form
    template_name = 'checkout_info.html'

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = self.form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect('card')
        else:
            form = self.form_class()
            return render(request=request, template_name="checkout_info.html", context={"form": form})


# Payment Method
class CreateCard(LoginRequiredMixin, View):
    template_name = 'checkout_payment.html'

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            payment_method_id = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": str(request.POST.get('cardnumber')),
                    "exp_month": request.POST.get('mm'),
                    "exp_year": request.POST.get('yy'),
                    "cvc": str(request.POST.get('number')),
                },
            )
            customer = stripe.Customer.create(
                email=request.user.email,
                name=str(request.POST.get('cardholder')),
            )
            stripe.PaymentMethod.attach(
                payment_method_id.id,
                customer=customer.id,
            )
            product = [i for i in CheckoutCart.objects.filter(user=request.user)]
            for i in product:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(i.product.price),
                    currency="usd",
                    payment_method_types=["card"],
                    customer=customer.id,
                    payment_method=payment_method_id.id,
                )
                confirm_payment = stripe.PaymentIntent.confirm(
                    payment_intent.id,
                    payment_method="pm_card_visa",

                )
            shipping = 150
            sub_total = 0
            total = 0
            product_show = CheckoutCart.objects.all()
            for item in product_show:
                if item.product:
                    item.pro_total = item.quantity * item.product.price
                    sub_total += item.pro_total
                    total = (sub_total + shipping)
                    item.save()
            context = {
                'product_show': product_show,
                'sub_total': sub_total,
                'total': total,

            }
        return render(request, template_name="checkout_complete_backup.html", context={"intent": confirm_payment,
                                                                                       "cart_image": product,
                                                                                       "total": total})

    def get(self, request):
        return render(request, self.template_name)


# Cart Complete
@login_required(login_url='login')
def CartComplete(request):
    if request.method == "POST":
        print(request)
    return render(request, "checkout_complete.html")


# Contact US
@login_required(login_url='login')
def Contact(request):
    if request.method == "POST":
        print(request)
    return render(request, "contact_us.html")


# FAQ
@login_required(login_url='login')
def Faq(request):
    if request.method == "POST":
        print(request)
    return render(request, "faq.html")


# About Us
@login_required(login_url='login')
def AboutUs(request):
    if request.method == "POST":
        print(request)
    return render(request, "about_us.html")


# My Account Page
@login_required(login_url='login')
def MyAccount(request):
    if request.method == "POST":
        print(request)
    return render(request, "my_account.html")


# All Products
@login_required(login_url='login')
def Products(request):
    if request.method == "POST":
        print(request)
    return render(request, "product.html")
