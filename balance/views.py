from datetime import date

from flask import render_template, request

from . import ALMACEN, app
from .forms import MovimientoForm
from .models import ListaMovimientosCsv, ListaMovimientosDB, Movimiento


@app.route('/')
def home():
    if ALMACEN == 0:
        lista = ListaMovimientosCsv()
    else:
        lista = ListaMovimientosDB()
    return render_template('inicio.html', movs=lista.movimientos)


@app.route('/eliminar/<int:id>')
def delete(id):
    lista = ListaMovimientosDB()
    template = 'borrado.html'
    try:
        result = lista.eliminar(id)
        if not result:
            template = 'error.html'
    except:
        template = 'error.html'

    return render_template(template, id=id)


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def actualizar(id):
    if request.method == 'GET':
        lista = ListaMovimientosDB()
        movimiento = lista.buscarMovimiento(id)
        formulario = MovimientoForm(data=movimiento)
        return render_template('form_movimiento.html', form=formulario, id=movimiento.get('id'))

    if request.method == 'POST':
        lista = ListaMovimientosDB()
        formulario = MovimientoForm(data=request.form)

        fecha = formulario.fecha.data
        mov_dict = {
            'fecha': fecha.isoformat(),
            'concepto': formulario.concepto.data,
            'tipo': formulario.tipo.data,
            'cantidad': formulario.cantidad.data,
            'id': formulario.id.data
        }

        movimiento = Movimiento(mov_dict)

        resultado = lista.editarMovimiento(movimiento)

        if resultado == 1:
            template = 'guardado_ok.html'
        elif resultado == -1:
            template = 'error_edit.html'
        else:
            template = 'error_inesperado.html'

    return render_template(template)
