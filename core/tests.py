import time

from selenium import webdriver

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from core.models import *
from core.views import *
from core.templatetags.slide_template_tags import *
from core.templatetags.category_template_tags import *
from core.templatetags.cart_template_tags import *


class SlideTest(TestCase):
    def setUp(self) -> None:
        self.slide = Slide.objects.create(caption1='caption1', caption2='caption2')

    def test_str(self):
        self.assertEqual(self.slide.__str__(), 'caption1 - caption2')


class CategoryTest(TestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create(title='title', slug='slug')

    def test_slide_creation(self):
        self.assertTrue(isinstance(self.category, Category))
        self.assertEqual(self.category.__str__(), 'title')

    def test_get_absolute_url(self):
        self.assertEqual(self.category.get_absolute_url(), '/category/slug/')


class ItemTest(TestCase):
    def setUp(self) -> None:
        category = Category.objects.create()

        self.item = Item.objects.create(
            title='title',
            slug='slug',
            category=category,
            price=100,
        )

    def test_str(self):
        self.assertEqual(self.item.__str__(), 'title')

    def test_get_url(self):
        self.assertEqual(self.item.get_absolute_url(), '/product/slug/')
        self.assertEqual(self.item.get_add_to_cart_url(), '/add-to-cart/slug/')
        self.assertEqual(self.item.get_remove_from_cart_url(), '/remove-from-cart/slug/')


class OrderItemTestCase(TestCase):
    def setUp(self):
        category = Category.objects.create()
        user = User.objects.create(username='')
        item_with_discount_price = Item.objects.create(
            title='item_with_discount_price',
            category=category,
            price=100,
            discount_price=75,
        )
        item_without_discount_price = Item.objects.create(
            title='item_without_discount_price',
            category=category,
            price=100,
        )
        self.order_item_with_discount_price = OrderItem.objects.create(
            user=user,
            item=item_with_discount_price,
            quantity=2,
        )
        self.order_item_without_discount_price = OrderItem.objects.create(
            user=user,
            item=item_without_discount_price,
        )

    def test_str(self):
        self.assertEqual(self.order_item_with_discount_price.__str__(), '2 of item_with_discount_price')
        self.assertEqual(self.order_item_without_discount_price.__str__(), '1 of item_without_discount_price')

    def test_get_price_with_discount(self):
        self.assertEqual(self.order_item_with_discount_price.get_total_item_price(), 200)
        self.assertEqual(self.order_item_with_discount_price.get_total_discount_item_price(), 150)
        self.assertEqual(self.order_item_with_discount_price.get_amount_saved(), 50)
        self.assertEqual(self.order_item_with_discount_price.get_final_price(), 150)

    def test_get_price_without_discount(self):
        self.assertEqual(self.order_item_without_discount_price.get_total_item_price(), 100)
        self.assertEqual(self.order_item_without_discount_price.get_final_price(), 100)


class OrderTestCase(TestCase):
    def setUp(self):
        category = Category.objects.create()
        user = User.objects.create(username='username')
        item_with_discount_price = Item.objects.create(
            category=category,
            price=100,
            discount_price=75,
        )
        item_without_discount_price = Item.objects.create(
            category=category,
            price=100,
        )
        order_item_with_discount_price = OrderItem.objects.create(
            user=user,
            item=item_with_discount_price,
            quantity=2,
        )
        order_item_without_discount_price = OrderItem.objects.create(
            user=user,
            item=item_without_discount_price,
        )

        self.order = Order.objects.create(
            user=user,
            ordered_date=timezone.now(),
        )
        self.order.items.add(order_item_with_discount_price)
        self.order.items.add(order_item_without_discount_price)

    def test_str(self):
        self.assertEqual(self.order.__str__(), 'username')

    def test_get_total(self):
        self.assertEqual(self.order.get_total(), 250)


class BillingAddressTest(TestCase):
    def setUp(self) -> None:
        user = User.objects.create(username='username')
        self.billing_address = BillingAddress.objects.create(user=user)

    def test_str(self):
        self.assertEqual(self.billing_address.__str__(), 'username')


class PaymentTest(TestCase):
    def setUp(self) -> None:
        user = User.objects.create(username='username')
        self.payment = Payment.objects.create(user=user, amount=0)

    def test_str(self):
        self.assertEqual(self.payment.__str__(), 'username')


class ReffCodeCreationTEst(TestCase):

    def setUp(self) -> None:
        random.seed(0)

    def test_create_ref_code(self):
        self.assertEqual(create_ref_code(), '41pjso2krv6sk1wj6936')


class PaymentViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='username')
        billing_address = BillingAddress.objects.create(user=self.user)
        Order.objects.create(user=self.user,
                             ordered_date=timezone.now(),
                             billing_address=billing_address)
        self.request_factory = RequestFactory()

    def test_get(self) -> None:
        request = self.request_factory.get('payment/')
        request.user = self.user
        view = PaymentView()
        view.setup(request, slug='slug')

        response = view.get()
        self.assertEqual(response.status_code, 200)


class OrderSummaryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="username")
        Order.objects.create(user=self.user,
                             ordered_date=timezone.now())
        self.request_factory = RequestFactory()

    def test(self) -> None:
        request = self.request_factory.get('order-summary/')
        request.user = self.user
        view = OrderSummaryView()
        view.setup(request)

        response = view.get()
        self.assertEqual(response.status_code, 200)


class CategoryViewTest(TestCase):
    def setUp(self):
        Category.objects.create(slug='slug')
        self.user = User.objects.create_user(username="username")
        self.request_factory = RequestFactory()

    def test(self) -> None:
        request = self.request_factory.get('category/')
        request.user = self.user
        view = CategoryView()
        view.setup(request, slug='slug')

        response = view.get()
        self.assertEqual(response.status_code, 200)


class CheckoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="username")
        Order.objects.create(user=self.user,
                             ordered_date=timezone.now())
        self.request_factory = RequestFactory()

        self.driver = webdriver.Chrome()

    def test_get(self) -> None:
        request = self.request_factory.get('checkout/')
        request.user = self.user
        view = CheckoutView()
        view.setup(request)

        response = view.get()
        self.assertEqual(response.status_code, 200)

    def test_post(self) -> None:
        view = CheckoutView()
        request = self.request_factory.get('checkout/')
        request.user = self.user
        form = {
            'street_address': 'street_address',
            'apartment_address': 'apartment_address',
            'country': 'NZ',
            'zip': 'zip',
            'same_shipping_address': False,
            'save_info': False,
            'payment_option': 'S'
        }
        request.POST = form

        view.setup(request)
        response_stripe = view.post()

        request.POST['payment_option'] = 'P'
        view.setup(request)

        response_paypal = view.post()

        self.assertEqual(response_stripe.url, '/payment/stripe/')
        self.assertEqual(response_paypal.url, '/payment/paypal/')

    def test_selenium_Stripe(self):
        self.driver.get("http://127.0.0.1:8000/accounts/login/?next=/checkout/")
        self.driver.find_element(by=By.NAME, value='login').send_keys('LOL')
        self.driver.find_element(by=By.NAME, value='password').send_keys('123456')
        self.driver.find_element(by=By.CLASS_NAME, value='btn-primary').click()
        self.driver.find_element(value='id_street_address').send_keys('street_address')
        self.driver.find_element(value='id_apartment_address').send_keys('apartment_address')
        Select(self.driver.find_element(value='id_country')).select_by_index(1)
        Select(self.driver.find_element(value='state')).select_by_index(1)
        self.driver.find_element(value='id_zip').send_keys('zip')
        self.driver.find_element(value='Stripe').click()
        self.driver.find_element(by=By.CLASS_NAME, value='btn-primary').click()

        self.assertEqual("http://127.0.0.1:8000/payment/stripe/", self.driver.current_url)

    def test_selenium_PayPal(self):
        self.driver.get("http://127.0.0.1:8000/accounts/login/?next=/checkout/")
        self.driver.find_element(by=By.NAME, value='login').send_keys('LOL')
        self.driver.find_element(by=By.NAME, value='password').send_keys('123456')
        self.driver.find_element(by=By.CLASS_NAME, value='btn-primary').click()
        self.driver.find_element(value='id_street_address').send_keys('street_address')
        self.driver.find_element(value='id_apartment_address').send_keys('apartment_address')
        Select(self.driver.find_element(value='id_country')).select_by_index(1)
        Select(self.driver.find_element(value='state')).select_by_index(1)
        self.driver.find_element(value='id_zip').send_keys('zip')
        self.driver.find_element(value='PayPal').click()
        self.driver.find_element(by=By.CLASS_NAME, value='btn-primary').click()

        self.assertEqual("http://127.0.0.1:8000/payment/paypal/", self.driver.current_url)

    def tearDown(self):
        self.driver.quit()


class SlidesTemplateTagTest(TestCase):
    def setUp(self) -> None:
        Slide.objects.create(image='image', caption1='caption1', caption2='caption2', link='link')

    def test_slides(self):
        items_div_res = slides()
        items_div_test = """<div class="item-slick1 item2-slick1" style="background-image: url(/media/{});">
        <div class="wrap-content-slide1 sizefull flex-col-c-m p-l-15 p-r-15 p-t-150 p-b-170">
        <span class="caption1-slide1 m-text1 t-center animated visible-false m-b-15" data-appear="rollIn">{}</span>
        <h2 class="caption2-slide1 xl-text1 t-center animated visible-false m-b-37" data-appear="lightSpeedIn">{}</h2>
        <div class="wrap-btn-slide1 w-size1 animated visible-false" data-appear="slideInUp"><a href="{}" 
        class="flex-c-m size2 bo-rad-23 s-text2 bgwhite hov1 trans-0-4">Shop Now</a></div></div></div>""".format(
            'image', 'caption1', 'caption2', 'link')
        self.assertEqual(items_div_res, items_div_test)


class CategoriesDivTest(TestCase):
    def setUp(self) -> None:
        Category.objects.create(image='image', slug='slug', title='title')
        Category.objects.create(image='image1', slug='slug1', title='title1')

    def test_categories_div(self):
        items_div_res = categories_div()
        items_div_test = """<div class="col-sm-10 col-md-8 col-lg-4 m-l-r-auto">""" + """<div class="block1 hov-img-zoom pos-relative m-b-30"><img src="/media/{}" alt="IMG-BENNER"><div class="block1-wrapbtn w-size2"><a href="/category/{}" class="flex-c-m size2 m-text2 bg3 hov1 trans-0-4">{}</a></div></div>""".format(
            'image', 'slug',
            'title') + """<div class="block1 hov-img-zoom pos-relative m-b-30"><img src="/media/{}" alt="IMG-BENNER"><div class="block1-wrapbtn w-size2"><a href="/category/{}" class="flex-c-m size2 m-text2 bg3 hov1 trans-0-4">{}</a></div></div>""".format(
            'image1', 'slug1', 'title1') + """</div>"""
        self.assertEqual(items_div_res, items_div_test)


class CartItemPriceTest(TestCase):
    def setUp(self) -> None:
        self.anonim = AnonymousUser()

        category = Category.objects.create()
        self.user = User.objects.create(username='username')
        item_with_discount_price = Item.objects.create(
            category=category,
            price=100,
            discount_price=75,
        )
        item_without_discount_price = Item.objects.create(
            category=category,
            price=100,
        )
        order_item_with_discount_price = OrderItem.objects.create(
            user=self.user,
            item=item_with_discount_price,
            quantity=2,
        )
        order_item_without_discount_price = OrderItem.objects.create(
            user=self.user,
            item=item_without_discount_price,
        )

        self.order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
        )
        self.order.items.add(order_item_with_discount_price)
        self.order.items.add(order_item_without_discount_price)

    def test_cart_item_price_total(self):
        self.assertEqual(cart_item_price(self.user), 300)

    def test_cart_item_price_anonim(self):
        self.assertEqual(cart_item_price(self.anonim), 0)


class GetCArtTest(TestCase):
    def setUp(self) -> None:
        self.anonim = AnonymousUser()

        category = Category.objects.create()
        self.user = User.objects.create(username='username')
        item_with_discount_price = Item.objects.create(
            image='image',
            title='title',
            category=category,
            price=100,
            discount_price=75,
        )
        order_item_with_discount_price = OrderItem.objects.create(
            user=self.user,
            item=item_with_discount_price,
            quantity=2,
        )

        self.order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
        )
        self.order.items.add(order_item_with_discount_price)

    def test_cart_item_price_total(self):
        total_res = get_cart(self.user)
        total_test = """<li class="header-cart-item">
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
                                    </li>""".format('/media/image', 'title', 2, 100.0)

        self.assertEqual(total_res, total_test)

    def test_get_cart_anonim(self):
        self.assertEqual(get_cart(self.anonim), 0)
