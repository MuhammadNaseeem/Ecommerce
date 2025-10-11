from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Accounts app (for login, signup, profile, etc.)
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),

    # Products app (listings, detail, categories)
    path('products/', include(('products.urls', 'products'), namespace='products')),

    # Cart app (shopping cart functionality)
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),

    # Orders app (checkout, payments, order history)
    path('orders/', include(('orders.urls', 'orders'), namespace='orders')),

    # Core app (home page, hero, featured products)
    path('', include(('core.urls', 'core'), namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


