def test_delete_product():
    database = Database()
    product_id = database.insert_product(name='Product name', price=10.5, amount=10)
    product = database.search_product_by_id(product_id)
    assert product, 'Product not found by ID'

    product = database.delete_product_by_id(product_id)
    product = database.search_product_by_id(product_id)
    assert not product, 'Product not deleted'


def test_assert_false():
    assert False, 'The assert shuold fail'
