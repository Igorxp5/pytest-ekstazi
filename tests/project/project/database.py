import re
import json
import uuid
import pathlib
import functools

from .user import User
from .exceptions import *
from .access_level import AccessLevel, PermissionDenied
from .product import Product


DEFAULT_DATABASE_FILE = 'database.json'


def required_access(required_level):
    def wrapper(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            if not self._logged_user:
                raise UnauthorizedAccess
            if self._logged_user.access_level.value > required_level.value:
                raise PermissionDenied(self._logged_user.access_level, required_level)
            return func(self, *args, **kwargs)
        return inner
    return wrapper


class Database:
    def __init__(self, filepath=DEFAULT_DATABASE_FILE):
        self.filepath = pathlib.Path(filepath)
        self._logged_user = None
        self._products = dict()
        self._users = dict()

        if self.filepath.exists():
           self._load() 

    def login(self, user):
        self._logged_user = user

    @required_access(AccessLevel.MANAGER)
    def insert_product(self, name, price, amount=0):
        id_ = str(uuid.uuid4())
        product = Product(id_, name, price, amount)
        self._products[id_] = product
        self._save()
        return product

    @required_access(AccessLevel.MANAGER)
    def delete_product(self, id_):
        if id_ not in self._products:
            raise ProductNotFound(f'Product {id_} not found')
        product = self._products[id_]
        del self._products[id_]
        self._save()
        return product

    @required_access(AccessLevel.CASHIER)
    def search_products_by_name(self, name):
        return [product for product in self._products.values() if re.search(re.escape(name), product.name)]

    @required_access(AccessLevel.CASHIER)
    def search_product_by_id(self, id_):
        return self._products.get(id_)

    @required_access(AccessLevel.CASHIER)
    def settle_product_by_id(self, id_, amount):
        if id_ not in self._products:
            raise ProductNotFound(f'Product {id_} not found')
        product = self._products[id_]
        if product.amount - amount < 0:
            raise InvalidOperation(f'There are no items enough to settle. Current available is {product.amount}')
        product.amount -= amount
        self._save()

    @required_access(AccessLevel.ADMIN)
    def insert_user(self, name, birthday, social_number, phone, access_level):
        user = User(name, birthday, social_number, phone, access_level)
        self._users[user.social_number] = user
        self._save()
        return user

    @required_access(AccessLevel.ADMIN)
    def delete_user(self, social_number):
        if social_number not in self._users:
            raise UserNotFound(f'User {social_number} not found')
        user = self._users[social_number]
        del self._users[social_number]
        self._save()
        return user
    
    @required_access(AccessLevel.MANAGER)
    def search_user_by_social_number(self, social_number):
        return self._users.get(social_number)

    def _to_dict(self):
        database = dict()
        database['products'] = {product.id: product.to_dict() for product in self._products.values()}
        database['users'] = {user.social_number: user.to_dict() for user in self._users.values()}
        return database
    
    def _save(self):
        with open(self.filepath, 'w') as file:
            json.dump(self._to_dict(), file, indent=4)
    
    def _load(self):
        with open(self.filepath) as file:
            database = json.load(file)
        self._products = {product_id: Product.from_dict(product) for product_id, product in database.get('products', {}).items()}
        self._users = {user_id: User.from_dict(user) for user_id, user in database.get('users', {}).items()}
