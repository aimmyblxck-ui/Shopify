
from decimal import Decimal
from .models import Product


CART_SESSION_ID = 'cart'


class Cart:

    def __init__(self, request):

        self.session = request.session

        cart = self.session.get(CART_SESSION_ID)

        if cart is None:
            cart = {}
            self.session[CART_SESSION_ID] = cart

        self.cart = cart

    def save(self):

        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True

    def add(self, product, quantity=1):

        quantity = int(quantity)

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        if not product.is_available:
            raise ValueError("Product is unavailable.")

        product_id = str(product.id)

        current_quantity = self.cart.get(
            product_id, {}
        ).get('quantity', 0)

        new_quantity = current_quantity + quantity

        if new_quantity > product.stock:
            raise ValueError(
                f"Only {product.stock} items are available."
            )

        self.cart[product_id] = {
            'quantity': new_quantity,
            'price': str(product.price)
        }

        self.save()

    def update(self, product, quantity):

        quantity = int(quantity)

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        if not product.is_available:
            raise ValueError("Product is unavailable.")

        if quantity > product.stock:
            raise ValueError(
                f"Only {product.stock} items are available."
            )

        product_id = str(product.id)

        if product_id in self.cart:

            self.cart[product_id] = {
                'quantity': quantity,
                'price': str(product.price)
            }

            self.save()

    def remove(self, product):

        product_id = str(product.id)

        if product_id in self.cart:

            del self.cart[product_id]
            self.save()

    def __iter__(self):

        product_ids = list(self.cart.keys())

        products = Product.objects.filter(
            id__in=product_ids
        ).select_related('category')

        product_map = {
            str(product.id): product
            for product in products
        }

        for product_id, item in self.cart.items():

            product = product_map.get(product_id)

            if product is None:
                continue

            quantity = int(item['quantity'])

            # Get current price from database.
            price = product.price

            subtotal = price * quantity

            yield {
                'product': product,
                'quantity': quantity,
                'price': price,
                'subtotal': subtotal
            }

    def __len__(self):

        return sum(
            int(item['quantity'])
            for item in self.cart.values()
        )

    def get_total_price(self):

        total = Decimal('0.00')

        products = Product.objects.filter(
            id__in=self.cart.keys()
        )

        product_map = {
            str(product.id): product
            for product in products
        }

        for product_id, item in self.cart.items():

            product = product_map.get(product_id)

            if product is None:
                continue

            quantity = int(item['quantity'])

            # Never trust the session price.
            total += product.price * quantity

        return total

    def clear(self):

        self.session.pop(CART_SESSION_ID, None)
        self.session.modified = True
