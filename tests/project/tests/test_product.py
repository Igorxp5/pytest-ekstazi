import json

import pytest

from project.user import User
from project.product import Product
from project.access_level import AccessLevel, PermissionDenied
from project.database import Database, UnauthorizedAccess, DEFAULT_DATABASE_FILE

ADMIN_USER = User(name='Admin', birthday='1970-01-01', social_number='00011122233', phone='+5511912345678', access_level=AccessLevel.ADMIN)
MANAGER_USER = User(name='Manager', birthday='1970-01-02', social_number='11122233344', phone='+5511912345679', access_level=AccessLevel.MANAGER)
CASHIER_USER = User(name='Cashier', birthday='1970-01-03', social_number='22233344455', phone='+5511912345670', access_level=AccessLevel.CASHIER)


def test_product_access_level():
    """
    Only Manager and Admin should be able to insert and delete products
    """
    products = []
    database = Database()
    for i, user in enumerate([MANAGER_USER, ADMIN_USER]):
        database.login(user)

        product = database.insert_product(name=f'Product name ({i})', price=10.5, amount=10)
        products.append(product)
        database.delete_product(product.id)
    
    database.login(CASHIER_USER)

    with pytest.raises(PermissionDenied):
        database.insert_product(name=f'Product name ({i})', price=10.5, amount=10)

    with pytest.raises(PermissionDenied):
        database.delete_product(products[0].id)


def test_delete_product():
    """
    User should be able to delete products from database and its action should be noticed in the database file
    """
    database = Database()
    database.login(ADMIN_USER)
    product = database.insert_product(name='Product name', price=10.5, amount=10)
    searched_product = database.search_product_by_id(product.id)
    assert searched_product, 'Product not found by ID'
    assert product == searched_product, 'Product found is not the same inserted'

    deleted_product = database.delete_product(product.id)
    assert deleted_product == product, 'Product deleted is not the same inserted'
    assert not database.search_product_by_id(product.id), 'Product not deleted'

    with open(DEFAULT_DATABASE_FILE) as file:
        assert not json.load(file).get('products', {}).get(product.id), 'Product should not be in the database file'


def test_insert_product():
    """
    User should be able to insert products in the database and its action should be noticed in the database file
    """
    database = Database()
    database.login(ADMIN_USER)
    product = database.insert_product(name='Product name', price=10.5, amount=10)

    assert isinstance(product, Product), 'insert_product should return the product created'

    products = database.search_products_by_name('Product name')
    assert isinstance(products, list), 'search_product_by_name return should be a list'
    assert len(products), 'The search result should have just one item'
    assert products[0] == product, 'The search result got a different product than expected one'

    product = database.search_product_by_id(product.id)
    assert product, 'Product not found by ID'

    with open(DEFAULT_DATABASE_FILE) as file:
        assert json.load(file).get('products', {}).get(product.id), 'Product should be in the database file'

def test_unauthorized_access():
    """
    Non-logged user should not be able to do any action in the database
    """
    database = Database()
    database.login(ADMIN_USER)
    product = database.insert_product(name='Product name', price=10.5, amount=10)
    user = database.insert_user(name='Admin', birthday='1970-01-01', social_number='00011122233', phone='+5511912345678', access_level=AccessLevel.ADMIN)

    database = Database()

    with pytest.raises(UnauthorizedAccess):
        database.insert_product(name='Product name', price=10.5, amount=10)

    with pytest.raises(UnauthorizedAccess):
        database.delete_product(product.id)

    with pytest.raises(UnauthorizedAccess):
        database.search_products_by_name('Product name')
    
    with pytest.raises(UnauthorizedAccess):
        database.search_product_by_id(product.id)
    
    with pytest.raises(UnauthorizedAccess):
        database.settle_product_by_id(product.id, 5)
    
    with pytest.raises(UnauthorizedAccess):
        database.insert_user(name='Manager', birthday='1970-01-02', social_number='11122233344', phone='+5511912345679', access_level=AccessLevel.MANAGER)

    with pytest.raises(UnauthorizedAccess):
        database.delete_user(user.social_number)
