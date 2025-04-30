from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.users import Users
from app import db

bp = Blueprint('auth', __name__)

@bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nameUser = request.form['nameUser']
        passwordUser = request.form['passwordUser']

        user = Users.query.filter_by(nameUser=nameUser, passwordUser=passwordUser).first()

        if user:
            login_user(user)
            flash("¡Inicio de sesión exitoso!", "success")
            if user.rolUser == 'administrador':
                return redirect(url_for('productos.index'))
            else:
                return redirect(url_for('productos.index'))

        
        flash('Credenciales no válidas. Por favor, inténtelo de nuevo.', 'danger')
    
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    return render_template("login/login.html")

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Se ha cerrado la sesión.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rolUser == 'administrador':
        data_user = Users.query.all()
        return render_template('login/index.html',data_user=data_user)
    else:
        return redirect(url_for('productos.index'))
    
@bp.route('/auth/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nameUser = request.form['nameUser']
        passwordUser = request.form['passwordUser']

        # Verificar si ya existe algún usuario registrado
        first_user = Users.query.first()
        
        # Si no existe, asignamos el rol de 'administrador'
        if not first_user:
            new_User = Users(nameUser=nameUser, passwordUser=passwordUser, rolUser='administrador')
        else:
            new_User = Users(nameUser=nameUser, passwordUser=passwordUser)
        
        db.session.add(new_User)
        db.session.commit()
        
        return redirect(url_for('auth.login'))

    return render_template('login/add.html')

@bp.route('/auth/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    user = Users.query.get_or_404(id)

    if request.method == 'POST':
        user.nameUser = request.form['nameUser']
        user.passwordUser = request.form['passwordUser']

        if current_user.idUser == 1:
            user.rolUser = request.form['rolUser']

        db.session.commit()
        return redirect(url_for('auth.dashboard'))

    return render_template('login/edit.html', user=user, current_user=current_user)

@bp.route('/auth/delete/<int:id>')
def delete(id):
    User = Users.query.get_or_404(id)
    
    db.session.delete(User)
    db.session.commit()

    return redirect(url_for('auth.dashboard'))