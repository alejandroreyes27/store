from app import db
from app.models.users import Users # Importa el modelo User

class Carrito(db.Model):
    __tablename__ = 'carrito'
    idCarrito = db.Column(db.Integer, primary_key=True)
    idProducto = db.Column(db.Integer, db.ForeignKey('productos.idProducto'))
    idUser = db.Column(db.Integer, db.ForeignKey('user.idUser'))
    cantidad = db.Column(db.Integer, nullable=True, default=1)
    
    producto = db.relationship('Productos', backref='carrito', lazy=True)
    usuario = db.relationship('Users', backref='carrito', lazy=True)  # Relación con User

    def get_id(self):
        return str(self.idCarrito)