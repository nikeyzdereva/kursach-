from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Cart, Product, CartProduct
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


def index(request):
    products = Product.objects.all()
    cart = None
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'index.html', {'products': products, 'cart': cart})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
    cart_product.quantity += 1  # Добавляем один товар или увеличиваем количество
    cart_product.save()
    return redirect('index')

def cart(request):
    if not request.user.is_authenticated:
        return redirect('login')
    cart = Cart.objects.get(user=request.user)
    return render(request, 'cart.html', {'cart': cart})


@login_required
def remove_from_cart(request, product_id):
    cart = get_object_or_404(Cart, user=request.user)  # Получаем корзину пользователя
    product = get_object_or_404(Product, id=product_id)  # Находим товар, который нужно удалить
    cart_product = get_object_or_404(CartProduct, cart=cart, product=product)  # Получаем связь товара с корзиной

    # Удаление товара или уменьшение количества
    if cart_product.quantity > 1:
        cart_product.quantity -= 1
        cart_product.save()
    else:
        cart_product.delete()

    return redirect('index')  # Возвращаем пользователя на главную страницу