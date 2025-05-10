import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.Categoria import Categoria
from werkzeug.utils import secure_filename
from app.models.Carrito import Carrito
from app.models.Productos import Productos
from app import db

bp = Blueprint('carrito', __name__)

@bp.route('/carrito')
@login_required
def index():
    data = Carrito.query.filter_by(idUser=current_user.idUser).all()
    data_producto = Productos.query.all()
    categorias = Categoria.query.all()
    return render_template('carrito/index.html', data=data, usuario=current_user, producto=data_producto, categorias=categorias)

@bp.route('/carrito/add/<int:id>', methods=['POST'])
@login_required
def add(id):
    data = request.get_json()
    idProducto = data.get('idproducto')
    cantidad = int(data.get('cantidad'))
    talla = data.get('talla') 
    idUser = current_user.idUser

    dataexit = Carrito.query.filter_by(idProducto=idProducto, idUser=idUser).first()
    
    if dataexit:
        dataexit.cantidad += cantidad
        dataexit.talla = talla
    else:
        new_carrito = Carrito(
            idProducto=idProducto,
            idUser=idUser,
            cantidad=cantidad,
            talla=talla
        )
        db.session.add(new_carrito)
    
    db.session.commit()
    return {'success': True}, 200 

@bp.route('/carrito/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if request.method == 'GET':
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
            nueva_talla = data.get('talla')
            
            item = Carrito.query.filter_by(idCarrito=id, idUser=current_user.idUser).first_or_404()

            if nueva_cantidad < 1:
                return {'success': False, 'message': 'La cantidad debe ser al menos 1'}, 400

            item.cantidad = nueva_cantidad
            item.talla = nueva_talla
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

@bp.route('/carrito/eliminar-seleccionados', methods=['POST'])
@login_required
def eliminar_seleccionados():
    try:
        data = request.get_json()
        ids_carrito = data.get('ids_carrito', [])
        
        if not ids_carrito:
            return jsonify({'success': False, 'error': 'No hay productos seleccionados'}), 400

        Carrito.query.filter(
            Carrito.idCarrito.in_(ids_carrito),
            Carrito.idUser == current_user.idUser
        ).delete(synchronize_session=False)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/carrito/update-cantidad/<int:id>', methods=['POST'])
@login_required
def update_cantidad(id):
    data = request.json
    carrito = Carrito.query.get(id)
    if carrito:
        carrito.cantidad = data['cantidad']
        db.session.commit()
    return jsonify({'success': True})

@bp.route('/carrito/edit_talla', methods=['POST'])
@login_required
def edit_talla():
    data = request.json
    carrito = Carrito.query.get(data['idCarrito'])
    if carrito:
        carrito.talla = data['talla']
        db.session.commit()
    return jsonify({'success': True})

@bp.route('/carrito/count')
def get_cart_count():
    if current_user.is_authenticated:
        # Usa el campo correcto de tu modelo Carrito (idUser o idUser_id)
        count = Carrito.query.filter_by(idUser=current_user.idUser).count()
        return jsonify({"count": count})
    return jsonify({"count": 0})