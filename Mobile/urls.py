from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Ecom import views
from Ecom.views import CustomLoginView, SearchResultsView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Login.
    path('login/', CustomLoginView.as_view(), name='login'),
    # Logout
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    # Main Home Page
    path('', views.HomeView.as_view(), name='home'),
    # Detail Product Page
    path('detail/<int:id>/', views.ProductDetail.as_view(), name='product_detail'),
    # Signup
    path("signup/", views.RegisterFormView.as_view(), name="signup/"),
    # Checkout Cart
    path("checkout_cart/", views.Checkoutcart.as_view(), name="checkout_cart"),
    # Payment
    path("create_card/", views.CreateCard.as_view(), name="card"),
    # Shipping
    path("check_shipping/", views.Shipping.as_view(), name="shipping"),
    # Search
    path('search/', SearchResultsView.as_view(), name='search'),
    # Contact Us
    path('contact/', views.Contact, name='contact'),
    # FAQ Page
    path('faq/', views.Faq, name='faq'),
    # About Us Page
    path('about_us/', views.AboutUs, name='about_us'),
    # My Account Page
    path('my_account/', views.MyAccount, name='my_account'),
    # All Products
    path('products/', views.Products, name='products'),
]
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
