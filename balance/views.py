from flask import render_template

from balance.models import ListaMovimientosCsv, ListaMovimientosDB

from . import ALMACEN, app


@app.route('/')
def home():
    if ALMACEN == 0:
        lista = ListaMovimientosCsv()
    else:
        lista = ListaMovimientosDB()
    return render_template('inicio.html', movs=lista.movimientos)
