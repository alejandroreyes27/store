import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import jsonify
from app.models.Categoria import Categoria
from werkzeug.utils import secure_filename
from app.models.Carrito import Carrito
from app.models.Productos import Productos
from app import db

bp = Blueprint('carrito', __name__)

@bp.route('/carrito')
@login_required  # Asegura que el usuario esté logueado
def index():
    # Filtra los productos del carrito por el usuario actual
    data = Carrito.query.filter_by(idUser=current_user.idUser).all()
    data_producto = Productos.query.all()
    categorias = Categoria.query.all()
    return render_template('carrito/index.html', data=data, usuario=current_user, producto=data_producto,categorias=categorias)

@bp.route('/carrito/add/<int:id>', methods=['POST'])
@login_required
def add(id):
    data = request.get_json()  # Obtener datos en formato JSON
    idProducto = data.get('idproducto')
    cantidad = int(data.get('cantidad'))
    idUser = current_user.idUser

    dataexit = Carrito.query.filter_by(idProducto=idProducto, idUser=idUser).first()
    
    if dataexit:
        dataexit.cantidad += cantidad
    else:
        new_carrito = Carrito(
            idProducto=idProducto,
            idUser=idUser,
            cantidad=cantidad
        )
        db.session.add(new_carrito)
    
    db.session.commit()
    return {'success': True}, 200

@bp.route('/carrito/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'GET':
        # Obtener los datos del producto para mostrar en el modal
        item = Carrito.query.filter_by(idCarrito=id, idUser=current_user.idUser).first_or_404()
        return jsonify({
            'nombre': item.producto.nombreProducto,
            'precio': item.producto.precioProducto,
            'cantidad': item.cantidad,
            'imagen': url_for('static', filename=item.producto.imagenProducto)
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            nueva_cantidad = int(data.get('cantidad'))

            # Buscar el producto en el carrito
            item = Carrito.query.filter_by(idCarrito=id, idUser=current_user.idUser).first_or_404()

            # Validar que la cantidad no sea menor a 1
            if nueva_cantidad < 1:
                return {'success': False, 'message': 'La cantidad debe ser al menos 1'}, 400

            # Actualizar la cantidad
            item.cantidad = nueva_cantidad
            db.session.commit()

            return {'success': True}, 200

        except Exception as e:
            print(f"Error al guardar los cambios: {str(e)}")
            return {'success': False, 'message': 'Error al guardar los cambios'}, 500

@bp.route('/carrito/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    item = Carrito.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('❌ Producto eliminado del carrito correctamente')
    return redirect(url_for('carrito.index'))