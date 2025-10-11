from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import SignUpForm, LoginForm, AddressForm

User = get_user_model()

# ---------------- Auth Views ----------------
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:login')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if next_url:
                if next_url.startswith("/cart/add/"):
                    return redirect("cart:cart_detail")
                return redirect(next_url)
            return redirect('core:home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("accounts:login")

# ---------------- Profile View ----------------
@login_required
def profile_view(request):
    user = request.user
    orders = user.orders.all().order_by("-created_at") if hasattr(user, 'orders') else []
    addresses = user.addresses.all()  # ✅ Fetch all addresses for the profile
    return render(request, "accounts/profile.html", {"user": user, "orders": orders, "addresses": addresses})

# ---------------- Address Book Views ----------------
@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})

@login_required
def address_add(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if address.default:
                # Remove default from other addresses of same type
                request.user.addresses.filter(address_type=address.address_type, default=True).update(default=False)
            address.save()
            messages.success(request, "Address added successfully!")
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form})

@login_required
def address_edit(request, pk):
    address = get_object_or_404(request.user.addresses, pk=pk)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            if address.default:
                request.user.addresses.filter(address_type=address.address_type, default=True).exclude(pk=pk).update(default=False)
            address.save()
            messages.success(request, "Address updated successfully!")
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form})

@login_required
def address_delete(request, pk):
    address = get_object_or_404(request.user.addresses, pk=pk)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address deleted successfully!")
        return redirect('accounts:address_list')
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Address

@login_required
def set_default_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    # Unset other default addresses
    Address.objects.filter(user=request.user, default=True).update(default=False)
    
    # Set this one as default
    address.default = True
    address.save()
    
    messages.success(request, "Default address updated successfully!")
    return redirect('accounts:address_list')
