from flask import Blueprint, request, jsonify, current_app, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.models.Factura import Factura
from app.models.Detallefactura import DetalleFactura
from app.models.Productos import Productos
from app.models.Carrito import Carrito
import datetime
from io import BytesIO
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
import base64

bp = Blueprint('facturacion', __name__, url_prefix='/facturacion')

@bp.route('/facturas')
@login_required
def facturas_index():
    # Solo administradores pueden entrar
    if current_user.rolUser != 'administrador':
        flash('Acceso denegado.', 'warning')
        return redirect(url_for('productos.index'))
    
    # Obtener todas las facturas, ordenadas por fecha (más recientes primero)
    facturas = Factura.query.order_by(Factura.date_created.desc()).all()
    # También el conteo de no revisadas
    pendientes = Factura.query.filter_by(revisada=False).count()
    
    return render_template('facturacion/index.html',
                           facturas=facturas,
                           pendientes=pendientes)
    
@bp.route('/facturas/<int:id>')
@login_required
def ver(id):
    # Sólo admin
    if current_user.rolUser != 'administrador':
        flash('Acceso denegado.', 'warning')
        return redirect(url_for('productos.index'))

    factura = Factura.query.get_or_404(id)
    detalles = factura.detalles  # lista de DetalleFactura

    return render_template('facturacion/ver.html',
                        factura=factura,
                        detalles=detalles)
    
@bp.route('/facturas/<int:id>/marcar')
@login_required
def marcar_revisada(id):
    if current_user.rolUser != 'administrador':
        flash('Acceso denegado.', 'warning')
        return redirect(url_for('productos.index'))

    factura = Factura.query.get_or_404(id)
    factura.revisada = True
    db.session.commit()
    flash(f'Factura {factura.id} marcada como revisada.', 'success')
    return redirect(url_for('facturacion.facturas_index'))


def generar_factura_pdf(datos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    style_normal = styles['Normal']
    style_normal.fontName = 'Helvetica'
    style_normal.fontSize = 10
    
    style_title = styles['Title']
    style_title.fontName = 'Helvetica-Bold'
    style_title.fontSize = 14
    
    style_heading = styles['Heading3']
    style_heading.fontName = 'Helvetica-Bold'
    style_heading.fontSize = 12

    story = []
    
    # Logo y encabezado
    logo_path = os.path.join(current_app.root_path, "static", "logo.png")
    try:
        im = Image(logo_path, 2 * inch, 0.7 * inch)
        story.append(im)
    except:
        pass

    # Información de la empresa
    story.append(Paragraph("Zapatería Estilo S.A.", 
                          ParagraphStyle('Company', parent=style_title, textColor=colors.HexColor("#1f6fcb"))))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Av. Principal 456, Ciudad Moda", style_normal))
    story.append(Paragraph("Tel: 555-7890 | Email: info@zapateriaestilo.com", style_normal))
    story.append(Spacer(1, 24))

    # Datos del cliente y factura
    data = [
        [Paragraph("Cliente:", style_heading), Paragraph(datos['cliente'], style_normal)],
        [Paragraph("Fecha:", style_heading), Paragraph(datos['fecha'], style_normal)],
        [Paragraph("Factura #", style_heading), Paragraph(datos['numero'], style_normal)]
    ]
    table = Table(data, colWidths=[100, 300])
    table.setStyle(TableStyle([('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold')]))
    story.append(table)
    story.append(Spacer(1, 24))

    # Tabla de productos
    table_data = [['Descripción', 'Talla', 'Cantidad', 'Precio Unitario', 'Total']] + [
        [
            item['producto'],
            str(item['talla']),
            str(item['cantidad']),
            f"${item['precio_unitario']:,.0f}".replace(",", "."),
            f"${item['total']:,.0f}".replace(",", ".")
        ] for item in datos['items']
    ]
    table = Table(table_data, colWidths=[150, 60, 60, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1f6fcb")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 15),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#f8f9fa")),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#dee2e6")),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#1f6fcb")),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 30))

    # Totales con estilo mejorado
    total_data = [["Total:", f"$ {datos['subtotal']:,.0f}".replace(",", ".")]]
    total_table = Table(total_data, colWidths=[300, 150])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 14),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1f6fcb")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#1f6fcb")),
        ('ROUNDEDCORNERS', [5,5,5,5]),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 30))

    # Mensaje final con estilo
    terms_style = ParagraphStyle(
        'Terms',
        parent=style_normal,
        fontSize=9,
        textColor=colors.HexColor("#6c757d"),
        alignment=1  # Centrado
    )
    
    story.append(Paragraph("¡Gracias por su compra!", 
                          ParagraphStyle('ThankYou', parent=style_title, fontSize=16, textColor=colors.HexColor("#1f6fcb"))))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Política de devolución: 30 días con recibo.", terms_style))
    story.append(Paragraph("www.zapateriaestilo.com", terms_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

@bp.route('/comprar', methods=['POST'])
@login_required
def comprar():
    datos_carrito = request.get_json()
    if not datos_carrito or 'items' not in datos_carrito or len(datos_carrito['items']) == 0:
        return jsonify({'error': 'No hay productos seleccionados'}), 400

    try:
        # Crear factura
        nueva_factura = Factura(
            user_id=current_user.idUser,
            subtotal=0.0,
            iva=0.0,
            total=0.0
        )
        db.session.add(nueva_factura)
        db.session.commit()

        # Validar y crear detalles
        subtotal = 0.0
        for item in datos_carrito['items']:
            producto = Productos.query.get(item['product_id'])
            if not producto:
                raise ValueError(f"Producto {item['product_id']} no encontrado")

            subtotal += item['cantidad'] * item['precio_unitario']

            detalle = DetalleFactura(
                factura_id=nueva_factura.id,
                product_id=item['product_id'],
                talla=item['talla'],  # Guardamos la talla
                quantity=item['cantidad'],
                price=item['precio_unitario'],
                total=item['cantidad'] * item['precio_unitario']
            )
            db.session.add(detalle)

        nueva_factura.subtotal = subtotal
        nueva_factura.total = subtotal
        db.session.commit()

        # Preparar datos para PDF
        datos_factura = {
            'cliente': current_user.nameUser,
            'fecha': datetime.datetime.now().strftime("%d/%m/%Y"),
            'numero': f"FAC-{datetime.datetime.now().strftime('%Y%m%d')}-{nueva_factura.id}",
            'items': [{
                'producto': item['producto'],
                'talla': item['talla'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio_unitario'],
                'total': item['cantidad'] * item['precio_unitario']
            } for item in datos_carrito['items']],
            'subtotal': subtotal,
            'iva': 0.0,
            'total': subtotal
        }

        # Generar PDF y convertir a Base64
        pdf_buffer = generar_factura_pdf(datos_factura)
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

        return jsonify({
            'invoice_data': datos_factura,
            'pdf_base64': pdf_base64
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Error en /facturacion/comprar")
        return jsonify({'error': str(e)}), 500
    

@bp.route('/eliminar_seleccionados', methods=['POST'])
@login_required
def eliminar_seleccionados():
    """
    Recibe JSON con: { "ids_carrito": [1, 2, 5, ...] }
    y elimina de la tabla Carrito todos los registros cuyo id esté en esa lista
    y pertenezcan al usuario logueado.
    """
    data = request.get_json() or {}
    ids = data.get('ids_carrito', [])
    if not isinstance(ids, list) or not ids:
        return jsonify({'success': False, 'error': 'No se recibieron IDs válidos'}), 400

    try:
        deleted = (
            Carrito.query
                   .filter(Carrito.id.in_(ids), Carrito.user_id == current_user.idUser)
                   .delete(synchronize_session=False)
        )
        db.session.commit()
        return jsonify({'success': True, 'deleted_count': deleted})
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error eliminando productos seleccionados")
        return jsonify({'success': False, 'error': 'Error al eliminar del carrito'}), 500