from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product, Category, Review, Wishlist, ProductVariant
from .forms import ReviewForm
from cart.cart import Cart  # make sure your Cart import path is correct


# --------------------------
# Product List (search, filter, sort, pagination)
# --------------------------
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    # Filter by category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Search filter
    query = request.GET.get("q")
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Sorting
    sort = request.GET.get("sort")
    if sort == "price_low":
        products = products.order_by("price")
    elif sort == "price_high":
        products = products.order_by("-price")
    elif sort == "newest":
        products = products.order_by("-created_at")

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "products/product_list.html", {
        "category": category,
        "categories": categories,
        "products": page_obj,
    })


# --------------------------
# Product Detail (variants, reviews)
# --------------------------
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variants = ProductVariant.objects.filter(product=product)

    # Reviews
    all_reviews = Review.objects.filter(product=product)
    reviews = all_reviews.order_by('-created_at')[:5]
    avg_rating = all_reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    review_count = all_reviews.aggregate(count=Count('id'))['count']

    # Review form
    review_form = ReviewForm(request.POST or None)
    if request.method == "POST" and 'submit_review' in request.POST:
        if request.user.is_authenticated:
            if review_form.is_valid():
                new_review = review_form.save(commit=False)
                new_review.user = request.user
                new_review.product = product
                new_review.save()
                messages.success(request, "Your review has been submitted.")
                return redirect('products:product_detail', slug=slug)
        else:
            messages.info(request, "You need to login to submit a review.")
            return redirect('accounts:login')

    return render(request, "products/product_detail.html", {
        "product": product,
        "variants": variants,
        "reviews": reviews,
        "avg_rating": round(avg_rating, 1),
        "review_count": review_count,
        "review_form": review_form,
    })


# --------------------------
# Wishlist
# --------------------------
@login_required
def add_to_wishlist(request, slug):
    product = get_object_or_404(Product, slug=slug)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
    )

    if created:
        messages.success(request, f"{product.name} has been added to your wishlist 💖")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")

    return redirect("products:wishlist")


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, "products/wishlist.html", {"wishlist_items": wishlist_items})


@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    item.delete()
    messages.success(request, f"{item.product.name} removed from wishlist.")
    return redirect('products:wishlist')


@login_required
def move_to_cart(request, item_id):
    wishlist_item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    cart = Cart(request)
    cart.add(product=wishlist_item.product, quantity=1, override_quantity=False)
    wishlist_item.delete()
    messages.success(request, f"{wishlist_item.product.name} moved to cart.")
    return redirect('cart:cart_detail')


# --------------------------
# Optional: Category Products (already covered in product_list_by_category)
# --------------------------
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    return render(request, 'products/category_products.html', {
        'category': category,
        'products': products
    })

# products/views.py
# products/views.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.cart import Cart
from products.models import Wishlist

@login_required
def move_all_to_cart(request):
    """
    Move all wishlist items for the current user to the cart.
    """
    wishlist_items = Wishlist.objects.filter(user=request.user)
    if not wishlist_items.exists():
        messages.info(request, "No items in your wishlist to move.")
        return redirect("products:wishlist")

    cart = Cart(request)
    for item in wishlist_items:
        cart.add(product=item.product, quantity=1)
        item.delete()

    messages.success(request, "All wishlist items have been moved to your cart.")
    return redirect("products:wishlist")
