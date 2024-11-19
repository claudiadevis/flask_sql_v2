from datetime import date

import csv
import sqlite3

RUTA_FICHERO = 'balance/data/movimientos.csv'
RUTA_DB = 'balance/data/balance.db'


class DBManager:
    """
    Clase para interactuar con la base de datos.
    """

    def __init__(self, ruta):
        self.ruta = ruta

    def consultarSQL(self, consulta):

        # 1. Conectar a la base de datos
        conexion = sqlite3.connect(self.ruta)

        # 2. Abrir cursor
        cursor = conexion.cursor()

        # 3. Ejecutar la consulta
        cursor.execute(consulta)

        # 4. Tratar los datos
        # 4.1. Obtener los datos
        datos = cursor.fetchall()

        self.registros = []
        nombres_columna = []

        for columna in cursor.description:
            nombres_columna.append(columna[0])

        # [ "id", "fecha", "concepto", "tipo", "cantidad"  ]
        # (
        # (   1 , '2024-11-01', 'Calabaza', 'G', '3.56'  )
        # )

        # 4.2. Guardar los datos localmente
        for dato in datos:
            movimiento = {}
            indice = 0
            for nombre in nombres_columna:
                movimiento[nombre] = dato[indice]
                indice += 1
            self.registros.append(movimiento)

        # 5. Cerrar la conexión
        conexion.close()

        # 6. Devolver el resultado
        return self.registros


class Movimiento:

    def __init__(self, dict_mov):
        self.errores = []

        fecha = dict_mov.get('fecha', '')
        concepto = dict_mov.get('concepto', 'Gastos varios')
        tipo = dict_mov.get('tipo', 'G')
        cantidad = dict_mov.get('cantidad', 0)

        try:
            self.fecha = date.fromisoformat(fecha)
        except ValueError:
            self.fecha = None
            mensaje = f'La fecha {fecha} no es una fecha ISO 8601 válida'
            self.errores.append(mensaje)
        except TypeError:
            self.fecha = None
            mensaje = f'La fecha {fecha} no es una cadena'
            self.errores.append(mensaje)
        except:
            self.fecha = None
            mensaje = f'Error desconocido con la fecha'
            self.errores.append(mensaje)

        try:
            valor = float(cantidad)
            if valor > 0:
                self.cantidad = valor
            else:
                self.cantidad = 0
                mensaje = f'El importe de la cantidad debe ser un número mayor que cero'
                self.errores.append(mensaje)
        except ValueError:
            self.cantidad = 0
            mensaje = f'El valor no es convertible a número'
            self.errores.append(mensaje)

        self.concepto = concepto
        self.tipo = tipo

    @property
    def has_errors(self):
        return len(self.errores) > 0

    def __str__(self):
        return f'{self.fecha} | {self.concepto} | {self.tipo} | {self.cantidad}'

    def __repr__(self):
        return self.__str__()


class ListaMovimientos:
    def __init__(self):
        try:
            self.cargar_movimientos()
        except:
            self.movimientos = []

    def guardar(self):
        raise NotImplementedError(
            'Debes usar una clase concreta de ListaMovimientos')

    def agregar(self, movimiento):
        raise NotImplementedError(
            'Debes usar una clase concreta de ListaMovimientos')

    def cargar_movimientos(self):
        raise NotImplementedError(
            'Debes usar una clase concreta de ListaMovimientos')

    def __str__(self):
        result = ''
        for mov in self.movimientos:
            result += f'\n{mov}'
        return result

    def __repr__(self):
        return self.__str__()


class ListaMovimientosDB(ListaMovimientos):

    def cargar_movimientos(self):
        db = DBManager(RUTA_DB)
        sql = 'SELECT id, fecha, concepto, tipo, cantidad FROM movimientos'
        datos = db.consultarSQL(sql)

        self.movimientos = []
        for dato in datos:
            mov = Movimiento(dato)
            self.movimientos.append(mov)


class ListaMovimientosCsv(ListaMovimientos):
    def __init__(self):
        super().__init__()

    def cargar_movimientos(self):
        self.movimientos = []
        with open(RUTA_FICHERO, 'r') as fichero:
            reader = csv.DictReader(fichero)
            for fila in reader:
                movimiento = Movimiento(fila)
                self.movimientos.append(movimiento)

    def guardar(self):
        with open(RUTA_FICHERO, 'w') as fichero:
            # cabeceras = ['fecha', 'concepto', 'ingreso_gasto', 'cantidad']
            # writer = csv.writer(fichero)
            # writer.writerow(cabeceras)

            cabeceras = list(self.movimientos[0].__dict__.keys())
            cabeceras.remove('errores')

            writer = csv.DictWriter(fichero, fieldnames=cabeceras)
            writer.writeheader()

            for mov in self.movimientos:
                mov_dict = mov.__dict__
                mov_dict.pop('errores')
                writer.writerow(mov_dict)

    def agregar(self, movimiento):
        """
        Agrega un movimiento a la lista y actualiza el archivo CSV.
        """

        if not isinstance(movimiento, Movimiento):
            raise TypeError(
                'Solo puedes agregar datos usando la clase Movimiento')

        self.movimientos.append(movimiento)
        self.guardar()
