from django import template
from django.core.exceptions import ObjectDoesNotExist

from core.models import Order
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0


@register.filter
def cart_item_price(user):
    if user.is_authenticated:
        try:
            qs = Order.objects.get(user=user, ordered=False)
            total = 0
            for order_item in qs.items.all():
                total += order_item.get_total_item_price()
            return total
        except ObjectDoesNotExist:
            return 0
    return 0


@register.filter
def get_cart(user):
    if user.is_authenticated:
        try:
            order = Order.objects.get(user=user, ordered=False)
            total = ""
            for order_item in order.items.all():
                total += """<li class="header-cart-item">
                                        <div class="header-cart-item-img">
                                            <img src="{}" alt="IMG">
                                        </div>
    
                                        <div class="header-cart-item-txt">
                                            <a href="#" class="header-cart-item-name">
                                                {}
                                            </a>
    
                                            <span class="header-cart-item-info">
                                                {} x ${}
                                            </span>
                                        </div>
                                    </li>""".format(order_item.item.image.url, order_item.item.title, order_item.quantity,
                                                    order_item.item.price)
            return mark_safe(total)
        except ObjectDoesNotExist:
            return 'Empty'
    return 0
