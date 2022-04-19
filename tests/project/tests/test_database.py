import json

from project.user import User
from project.product import Product
from project.access_level import AccessLevel
from project.database import Database, DEFAULT_DATABASE_FILE

ADMIN_USER = User(name='Admin', birthday='1970-01-01', social_number='00011122233', phone='+5511912345678', access_level=AccessLevel.ADMIN)


def test_delete_product():
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
