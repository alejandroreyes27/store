from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.Productos import Productos
from flask_login import current_user
from app.models.Categoria import Categoria 
from flask_login import login_required
from app import db
import os
from flask import current_app
from werkzeug.utils import secure_filename

bp = Blueprint('productos', __name__)

@bp.route('/productos')
@login_required
def index():

    edit_producto_id = request.args.get('edit')
    producto_edit = Productos.query.get(edit_producto_id) if edit_producto_id else None

    data_producto = Productos.query.filter_by(activo=True).all()
    categorias = Categoria.query.all()
    
    return render_template('productos/index.html', 
                           data_producto=data_producto, 
                           categorias=categorias,
                           producto_edit=producto_edit,
                           user=current_user)

@bp.route('/productos_categoria/<int:id>', methods=['GET'])
@login_required
def index_categoria(id):
    data_producto = Productos.query.filter_by(idCategoria=id,activo=True).all()
    categorias = Categoria.query.all()
    return render_template('productos/index.html', data_producto=data_producto, categorias=categorias, user=current_user)

@bp.route('/productos/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        try:
            # Validar campos obligatorios
            nombre_producto = request.form.get('nombreProducto')
            descripcion_producto = request.form.get('descripcionProducto')
            precio_producto = request.form.get('precioProducto')
            stock = request.form.get('stock')
            categoria = request.form.get('categoria')

            if not nombre_producto or not descripcion_producto or not precio_producto or not stock or not categoria:
                flash('Todos los campos son obligatorios.', 'error')
                return redirect(url_for('productos.add'))

            # Procesar imagen
            imagen_file = request.files.get('imagenProducto')
            imagen_filename = None
            if imagen_file and imagen_file.filename != '':
                imagen_filename = secure_filename(imagen_file.filename)
                imagen_path = os.path.join(current_app.root_path, 'static/IMG', imagen_filename)
                imagen_file.save(imagen_path)

            # Crear nuevo producto
            nuevo_producto = Productos(
                nombreProducto=nombre_producto,
                descripcionProducto=descripcion_producto,
                precioProducto=float(precio_producto),
                stock=int(stock),
                idCategoria=int(categoria),
                imagenProducto=f'IMG/{imagen_filename}' if imagen_filename else None
            )

            db.session.add(nuevo_producto)
            db.session.commit()

            flash('Producto agregado exitosamente.', 'success')
            return redirect(url_for('productos.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar el producto: {str(e)}', 'error')
            return redirect(url_for('productos.add'))

    # Obtener todas las categorías para mostrar en el formulario
    categorias = Categoria.query.all()
    return render_template('productos/add.html', categorias=categorias)

@bp.route('/productos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    producto = Productos.query.get_or_404(id)

    if request.method == 'POST':
        try:
            # Validar campos obligatorios
            nombre_producto = request.form.get('nombreProducto')
            descripcion_producto = request.form.get('descripcionProducto')
            precio_producto = request.form.get('precioProducto')
            stock = request.form.get('stock')
            categoria = request.form.get('categoria')

            if not nombre_producto or not descripcion_producto or not precio_producto or not stock or not categoria:
                flash('Todos los campos son obligatorios.', 'error')
                return redirect(url_for('productos.edit', id=id))

            # Actualizar campos del producto
            producto.nombreProducto = nombre_producto
            producto.descripcionProducto = descripcion_producto
            producto.precioProducto = float(precio_producto)
            producto.stock = int(stock)
            producto.idCategoria = int(categoria)

            # Procesar nueva imagen
            imagen_file = request.files.get('imagenProducto')
            if imagen_file and imagen_file.filename != '':
                # Eliminar imagen anterior si existe
                if producto.imagenProducto:
                    old_image_path = os.path.join(current_app.root_path, 'static', producto.imagenProducto)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                # Guardar nueva imagen
                imagen_filename = secure_filename(imagen_file.filename)
                imagen_path = os.path.join(current_app.root_path, 'static/IMG', imagen_filename)
                imagen_file.save(imagen_path)
                producto.imagenProducto = f'IMG/{imagen_filename}'

            # Guardar cambios en la base de datos
            db.session.commit()
            flash('Producto actualizado exitosamente.', 'success')
            return redirect(url_for('productos.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el producto: {str(e)}', 'error')
            return redirect(url_for('productos.index', edit=id))

    # Obtener todas las categorías para mostrar en el formulario
    categorias = Categoria.query.all()
    return render_template('productos/edit.html', producto=producto, categorias=categorias)

@bp.route('/productos/delete/<int:id>')
@login_required
def delete(id):
    producto = Productos.query.get_or_404(id)

    try:
        # Eliminar imagen asociada si existe
        if producto.imagenProducto:
            image_path = os.path.join(current_app.root_path, 'static', producto.imagenProducto)
            if os.path.exists(image_path):
                os.remove(image_path)

        # Eliminar producto de la base de datos
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el producto: {str(e)}', 'error')

    return redirect(url_for('productos.index'))

@bp.route('/mercado')
@login_required
def index_mercado():

    data_mercado = Productos.query.filter_by(activo=True).all()
    categorias = Categoria.query.all()
    
    return render_template('productos/mercado.html', data_producto=data_mercado, categorias=categorias,user=current_user)

@bp.route('/mercado2')
@login_required
def index_mercado2():

    data_mercado = Productos.query.filter_by(activo=True).all()
    categorias = Categoria.query.all()
    
    return render_template('productos/mercado2.html', data_producto=data_mercado, categorias=categorias,user=current_user)