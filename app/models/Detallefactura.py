from app import db

class DetalleFactura(db.Model):
    __tablename__ = 'detalles_factura'
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('productos.idProducto'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)

    def __init__(self, factura_id, product_id, quantity, price, total):
        self.factura_id = factura_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.total = total
