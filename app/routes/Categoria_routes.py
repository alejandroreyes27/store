from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.Categoria import Categoria
from app import db

# Definir el blueprint
bp = Blueprint('categoria', __name__)

@bp.route('/categorias/index')
@login_required
def index():
    categorias = Categoria.query.all()
    return render_template('categorias/index.html', categorias=categorias)

@bp.route('/categorias/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        nombre_categoria = request.form.get('nombreCategoria')

        if not nombre_categoria:
            flash('El nombre de la categoría es obligatorio.', 'error')
            return redirect(url_for('categoria.add'))

        nueva_categoria = Categoria(nombreCategoria=nombre_categoria)

        try:
            db.session.add(nueva_categoria)
            db.session.commit()
            flash('Categoría agregada correctamente.', 'success')
            return redirect(url_for('categoria.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar la categoría: {str(e)}', 'error')

    return render_template('categorias/add.html')

@bp.route('/categorias/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    # Buscar la categoría por su ID
    categoria = Categoria.query.get_or_404(id)

    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_categoria = request.form.get('nombreCategoria')

        # Validar que el nombre no esté vacío
        if not nombre_categoria:
            flash('El nombre de la categoría es obligatorio.', 'error')
            return redirect(url_for('categoria.edit', id=id))

        # Actualizar los datos de la categoría
        categoria.nombreCategoria = nombre_categoria

        try:
            # Guardar los cambios en la base de datos
            db.session.commit()
            flash('Categoría actualizada correctamente.', 'success')
            return redirect(url_for('categoria.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la categoría: {str(e)}', 'error')

    # Mostrar el formulario con los datos actuales
    return render_template('categorias/edit.html', categoria=categoria)

@bp.route('/categorias/delete/<int:id>')
@login_required
def delete(id):
    # Buscar la categoría por su ID
    categoria = Categoria.query.get_or_404(id)

    # Verificar si hay productos asociados a la categoría
    if categoria.productos:
        flash('No se puede eliminar la categoría porque tiene productos asociados.', 'error')
        return redirect(url_for('categoria.index'))

    try:
        # Eliminar la categoría de la base de datos
        db.session.delete(categoria)
        db.session.commit()
        flash('Categoría eliminada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la categoría: {str(e)}', 'error')

    return redirect(url_for('categoria.index'))