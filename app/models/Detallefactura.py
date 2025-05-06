from app import db
from app.models.Productos import Productos

class DetalleFactura(db.Model):
    __tablename__ = 'detalles_factura'
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('productos.idProducto'), nullable=False)
    talla = db.Column(db.Float)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)

    # relación con Productos
    producto = db.relationship('Productos', backref='detalles_factura', lazy=True,
                               foreign_keys=[product_id])

    def __init__(self, factura_id, product_id, talla, quantity, price, total):
        self.factura_id = factura_id
        self.product_id = product_id
        self.talla      = talla
        self.quantity   = quantity
        self.price      = price
        self.total      = total

