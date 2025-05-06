from app import db
from datetime import datetime

class Productos(db.Model):
    __tablename__ = 'productos'
    idProducto = db.Column(db.Integer, primary_key=True)
    nombreProducto = db.Column(db.String(255), nullable=False)
    descripcionProducto = db.Column(db.Text, nullable=False)
    precioProducto = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    imagenProducto = db.Column(db.String(255), nullable=True)
    talla = db.Column(db.String(10), nullable=True)

    idCategoria = db.Column(db.Integer, db.ForeignKey('categoria.idCategoria'), nullable=True)
    categoria = db.relationship('Categoria', back_populates='productos')
    fechaCreacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Producto {self.nombreProducto}>'
    
    def get_img(self, img_field):
        return getattr(self, img_field, 'default.jpg')