def test_insert_product():
    database = Database()
    product_id = database.insert_product(name='Product name', price=10.5, amount=10)

    assert product_id, 'No product ID generated'

    products = database.search_product_by_name('Product name')
    assert products, 'product not found by name'

    products = database.search_product_by_id(product_id)
    assert products, 'Product not found by ID'

