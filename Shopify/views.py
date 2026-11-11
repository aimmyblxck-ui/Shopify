
from decimal import Decimal

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Category, Product, Order, OrderItem
from .cart import Cart
from .forms import CheckoutForm


# 1. HOME PAGE
def home_view(request):

    featured_products = Product.objects.filter(
        is_available=True
    ).order_by('-created_at')[:8]

    categories = Category.objects.all()

    context = {
        'featured_products': featured_products,
        'categories': categories
    }

    return render(request, 'home.html', context)


# 2. PRODUCTS PAGE
def products_view(request):

    products = Product.objects.filter(is_available=True)

    categories = Category.objects.all()

    category_slug = request.GET.get('category')

    if category_slug:
        products = products.filter(
            category__slug=category_slug
        )

    stock = request.GET.get('stock')

    if stock == 'in':
        products = products.filter(stock__gt=0)

    elif stock == 'out':
        products = products.filter(stock=0)

    context = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'products.html', context)


# 3. PRODUCT DETAIL PAGE
def product_detail_view(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug
    )

    return render(
        request,
        'product_detail.html',
        {'product': product}
    )


# 4. CART PAGE
def cart_detail_view(request):

    cart = Cart(request)

    context = {
        'cart': cart,
        'cart_items': list(cart),
        'cart_total': cart.get_total_price(),
    }

    return render(request, 'cart.html', context)


# 5. ADD TO CART
@require_POST
def cart_add_view(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart = Cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))

        cart.add(
            product=product,
            quantity=quantity
        )

        messages.success(
            request,
            f'{product.name} added to your cart!'
        )

    except (ValueError, TypeError, ValidationError) as error:

        messages.error(request, str(error))

    return redirect('cart')


# 6. UPDATE CART
@require_POST
def cart_update_view(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart = Cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))

        cart.update(product, quantity)

        messages.success(
            request,
            'Cart updated successfully.'
        )

    except (ValueError, TypeError, ValidationError) as error:

        messages.error(request, str(error))

    return redirect('cart')


# 7. REMOVE FROM CART
@require_POST
def cart_remove_view(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart = Cart(request)

    cart.remove(product)

    messages.success(
        request,
        f'{product.name} removed from your cart.'
    )

    return redirect('cart')


# 8. CHECKOUT
def checkout_view(request):

    cart = Cart(request)

    if len(cart) == 0:

        messages.warning(
            request,
            'Your shopping cart is empty.'
        )

        return redirect('cart')

    if request.method == 'POST':

        form = CheckoutForm(request.POST)

        if form.is_valid():

            try:

                with transaction.atomic():

                    cart_items = list(cart.cart.items())

                    product_ids = [
                        int(product_id)
                        for product_id, item in cart_items
                    ]

                    if not product_ids:
                        raise ValueError(
                            'Your shopping cart is empty.'
                        )

                    locked_products = list(
                        Product.objects.select_for_update()
                        .filter(id__in=product_ids)
                        .order_by('id')
                    )

                    product_map = {
                        product.id: product
                        for product in locked_products
                    }

                    if len(product_map) != len(set(product_ids)):
                        raise ValueError(
                            'One or more products no longer exist.'
                        )

                    order_total = Decimal('0.00')

                    validated_items = []

                    for product_id, item in cart_items:

                        product = product_map.get(
                            int(product_id)
                        )

                        quantity = int(item['quantity'])

                        if quantity < 1:
                            raise ValueError(
                                'Invalid product quantity.'
                            )

                        if not product.is_available:
                            raise ValueError(
                                f'{product.name} is unavailable.'
                            )

                        if product.stock < quantity:
                            raise ValueError(
                                f'Only {product.stock} '
                                f'{product.name} items are available.'
                            )

                        subtotal = product.price * quantity

                        order_total += subtotal

                        validated_items.append(
                            (product, quantity)
                        )

                    order = form.save(commit=False)

                    order.total_amount = order_total

                    order.save()

                    for product, quantity in validated_items:

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )

                        product.stock -= quantity

                        product.save(
                            update_fields=['stock']
                        )

                cart.clear()

                messages.success(
                    request,
                    'Your order was placed successfully!'
                )

                return redirect(
                    'order_success',
                    order_number=order.order_number
                )

            except (ValueError, TypeError) as error:

                messages.error(request, str(error))

                return redirect('cart')

    else:

        form = CheckoutForm()

    context = {
        'form': form,
        'cart': cart,
        'cart_items': list(cart),
        'cart_total': cart.get_total_price(),
    }

    return render(request, 'checkout.html', context)


# 9. ORDER SUCCESS
def order_success_view(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        order_number=order_number
    )

    return render(
        request,
        'order_success.html',
        {'order': order}
    )


# 10. ABOUT PAGE
def about_view(request):

    return render(request, 'about.html')


# 11. CONTACT PAGE
def contact_view(request):

    return render(request, 'contact.html')
