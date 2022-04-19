class Product:
    def __init__(self, id_, name, price, amount=0):
        self.id = id_
        self.name = name
        self.price = price
        self.amount = amount
    
    def __eq__(self, o: object):
        return isinstance(o, Product) and self.to_dict() == o.to_dict()

    def is_out_of_stock(self):
        return self.amount == 0

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'price': self.price, 'amount': self.amount}

    @staticmethod
    def from_dict(props):
        return Product(id_=props['id'], name=props['name'],
                       price=props['price'], amount=props['amount'])
