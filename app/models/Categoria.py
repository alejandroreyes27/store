from app import db

class Categoria(db.Model):
    __tablename__ = 'categoria'
    idCategoria = db.Column(db.Integer, primary_key=True)
    nombreCategoria = db.Column(db.String(100), nullable=False, unique=True)

    productos = db.relationship('Productos', back_populates='categoria')

    def __repr__(self):
        return f'<Categoria {self.nombreCategoria}>'