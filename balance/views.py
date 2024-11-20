from datetime import date

from flask import render_template, request

from . import ALMACEN, app
from .forms import MovimientoForm
from .models import ListaMovimientosCsv, ListaMovimientosDB


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


@app.route('/editar/<int:id>')
def actualizar(id):
    if request.method == 'GET':
        lista = ListaMovimientosDB()
        movimiento = lista.buscarMovimiento(id)
        formulario = MovimientoForm(data=movimiento)
        return render_template('form_movimiento.html', form=formulario)
    return f'TODO: tratar el método POST para actualizar el movimiento {id}'
