import sys
from xmlrpc.server import SimpleXMLRPCServer 
from PyQt4 import QtGui, QtCore, uic
from random import randint
import uuid

class Snake():
    
    def __init__(self):
        self.id = str(uuid.uuid4())[:8]
        red, green, blue = randint(0,255), randint(0,255), randint(0,255)
        self.color = {"r": red, "g": green, "b": blue}
        self.camino = []
        self.casillas = []
        self.camino = []
        self.tam = len(self.casillas)
        self.direccion = "Abajo"

    def obtener_diccionario(self):
        
        diccionario = dict()
        diccionario = {
            'id': self.id,
            'camino': self.camino, 
            'color': self.color
        }
        return diccionario

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        
        super(MainWindow, self).__init__()
        uic.loadUi('servidor.ui', self)
        self.setStyleSheet("QMainWindow {background-color: #ACE7EF;}")
        self.pushButton_3.hide()
        self.pushButton.clicked.connect(self.iniciar_servidor)
        self.incio = False
        self.pausado = False
        self.timer = None 
        self.timer_s = None
        self.timer_camino = None 
        self.num_snakes = [] 
        self.table() 
        self.pintar_tabla()
        self.Tabla.setSelectionMode(QtGui.QTableWidget.NoSelection)
        self.spinBox_2.valueChanged.connect(self.actualiza_tabla) 
        self.spinBox_3.valueChanged.connect(self.actualiza_tabla)
        self.spinBox.valueChanged.connect(self.actualiza_timer) 
        self.time.valueChanged.connect(self.actualizar_timeout)
        self.pushButton_2.clicked.connect(self.inicia_juego) 
        self.pushButton_3.clicked.connect(self.terminar_juego)
        self.show() 

    def inicia_juego(self):
        
        if not self.incio:
            self.pushButton_3.show() 
            self.crear_serpiente() 
            self.pushButton_2.setText("Pausar el Juego") 
            self.dibujar_snakes()
            self.timer = QtCore.QTimer(self) 
            self.timer.timeout.connect(self.mover_serpientes) 
            self.timer.start(200) 
            self.timer_camino = QtCore.QTimer(self)
            self.timer_camino.timeout.connect(self.ac_camino)
            self.timer_camino.start(100)
            self.Tabla.installEventFilter(self) 
            self.incio = True 
        elif self.incio and not self.pausado: 
            self.timer.stop() 
            self.pausado = True 
            self.pushButton_2.setText("Reanudar el Juego") 
        elif self.pausado: 
            self.timer.start() 
            self.pausado = False 
            self.pushButton_2.setText("Pausar el Juego")

    def terminar_juego(self):
        
        self.num_snakes = [] 
        self.lcdNumber.display(0)
        self.timer.stop()
        self.incio = False 
        self.pushButton_3.hide() 
        self.pushButton_2.setText("Inicia Juego")

    def iniciar_servidor(self):
        
        puerto = self.spinBox_4.value()
        direccion = self.lineEdit.text()
        self.servidor = SimpleXMLRPCServer((direccion, 0))
        puerto = self.servidor.server_address[1] 
        self.spinBox_4.setValue(puerto) 
        self.spinBox_4.setReadOnly(True) 
        self.lineEdit.setReadOnly(True) 
        self.pushButton.setEnabled(False)
        self.servidor.register_function(self.ping)
        self.servidor.register_function(self.yo_juego)
        self.servidor.register_function(self.cambia_direccion)
        self.servidor.register_function(self.estado_del_juego)
        self.servidor.timeout = 0 
        self.timer_s = QtCore.QTimer(self)
        self.timer_s.timeout.connect(self.hacer) 
        self.timer_s.start(self.servidor.timeout) 

    

    def cambia_direccion(self, identificador, numero):
        
        for s in self.num_snakes:
            if s.id == identificador:
                if numero == 0:
                    if s.direccion is not "Abajo": 
                        s.direccion = "Arriba"
                if numero == 1:
                    if s.direccion is not "Izquierda":
                        s.direccion = "Derecha"
                if numero == 2: 
                    if s.direccion is not "Arriba":
                        s.direccion = "Abajo"
                if numero == 3: 
                    if s.direccion is not "Derecha":
                        s.direccion = "Izquierda"
        return True 

    def estado_del_juego(self):
        
        diccionario = dict()
        diccionario = {
            'espera': self.spinBox.value(), 
            'tamX': self.Tabla.columnCount(),
            'tamY': self.Tabla.rowCount(),
            'viboras': self.lista_snakes()
            }
        return diccionario


    def crear_serpiente(self):
        
        serpiente_nueva = Snake()
        creada = False
        while not creada:
            creada = True
            uno = randint(1, self.Tabla.rowCount()/2)
            dos = uno + 1
            tres = dos +1 
            ancho = randint(1, self.Tabla.columnCount()-1)
            achecar_1, achecar_2, achecar_3 = [uno, ancho], [dos, ancho], [tres, ancho]
            for s in self.num_snakes:
                if achecar_1 in s.casillas or achecar_2 in s.casillas or achecar_3 in s.casillas:
                    creada = False
                    break
            serpiente_nueva.casillas = [achecar_1, achecar_2, achecar_3]
            self.num_snakes.append(serpiente_nueva) 
            return serpiente_nueva

    def eventFilter(self, source, event):
        
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.Tabla): 
                key = event.key() 
                
                if (key == QtCore.Qt.Key_Up and
                    source is self.Tabla):
                    for serpiente in self.num_snakes:
                        if serpiente.direccion is not "Abajo":
                            serpiente.direccion = "Arriba"
                elif (key == QtCore.Qt.Key_Down and
                    source is self.Tabla):
                    for serpiente in self.num_snakes:
                        if serpiente.direccion is not "Arriba":
                            serpiente.direccion = "Abajo"
                elif (key == QtCore.Qt.Key_Right and
                    source is self.Tabla):
                    for serpiente in self.num_snakes:
                        if serpiente.direccion is not "Izquierda":
                            serpiente.direccion = "Derecha"
                elif (key == QtCore.Qt.Key_Left and
                    source is self.Tabla):
                    for serpiente in self.num_snakes:
                        if serpiente.direccion is not "Derecha":
                            serpiente.direccion = "Izquierda"
        return QtGui.QMainWindow.eventFilter(self, source, event)

    def mover_serpientes(self):
        
        for serpiente in self.num_snakes: 
            if self.sucidarte(serpiente) or self.te_mataron(serpiente):
                self.num_snakes.remove(serpiente) 
                self.pintar_tabla() 
                serpiente_1 = self.crear_serpiente()
                self.num_snakes = [serpiente_1]
            self.Tabla.item(serpiente.casillas[0][0],serpiente.casillas[0][1]).setBackground(QtGui.QColor(206, 254, 241))
            x = 0 
            for tupla in serpiente.casillas[0: len(serpiente.casillas)-1]:
                x += 1
                tupla[0] = serpiente.casillas[x][0]
                tupla[1] = serpiente.casillas[x][1]
            x
            if serpiente.direccion is "Abajo":
                if serpiente.casillas[-1][0] + 1 < self.Tabla.rowCount():
                    serpiente.casillas[-1][0] += 1
                else:
                    serpiente.casillas[-1][0] = 0
            if serpiente.direccion is "Derecha":
                if serpiente.casillas[-1][1] + 1 < self.Tabla.columnCount():
                    serpiente.casillas[-1][1] += 1
                else:
                    serpiente.casillas[-1][1] = 0
            if serpiente.direccion is "Arriba":
                if serpiente.casillas[-1][0] != 0:
                    serpiente.casillas[-1][0] -= 1
                else:
                    serpiente.casillas[-1][0] = self.Tabla.rowCount()-1
            if serpiente.direccion is "Izquierda":
                if serpiente.casillas[-1][1] != 0:
                    serpiente.casillas[-1][1] -= 1
                else:
                    serpiente.casillas[-1][1] = self.Tabla.columnCount()-1
        self.dibujar_snakes() 

    def sucidarte(self, serpiente):
      
        for seccion_corporal in serpiente.casillas[0:len(serpiente.casillas)-2]: 
            if serpiente.casillas[-1][0] == seccion_corporal[0] and serpiente.casillas[-1][1] == seccion_corporal[1]:
                return True
        return False

    def te_mataron(self, serpiente_a_checar):
        
        for serpiente in self.num_snakes:
            if serpiente.id != serpiente_a_checar.id:
                for seccion_corporal in serpiente.casillas[:]: 
                    if serpiente_a_checar.casillas[-1][0] == seccion_corporal[0] and serpiente_a_checar.casillas[-1][1] == seccion_corporal[1]:
                        self.num_snakes.remove(serpiente_a_checar) 

    def pintar_tabla(self):
       
        for i in range(self.Tabla.rowCount()):
            for j in range(self.Tabla.columnCount()):
                self.Tabla.setItem(i,j, QtGui.QTableWidgetItem())
                self.Tabla.item(i,j).setBackground(QtGui.QColor(206, 254, 241))

    def table(self):
        
        self.Tabla.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.Tabla.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def lista_snakes(self):
        
        lista = list()
        for serpiente in self.num_snakes:
            lista.append(serpiente.obtener_diccionario())
        return lista


    def ping(self):
        return "¡Pong!"


    def yo_juego(self):
        
        serpiente_nueva = self.crear_serpiente()
        diccionario = {"id": serpiente_nueva.id, "color": serpiente_nueva.color}
        return diccionario

    def hacer(self):
        self.servidor.handle_request()

    def ac_camino(self):
        
        for serpiente in self.num_snakes:
            serpiente.camino = []
            for casilla in serpiente.casillas:
                serpiente.camino.append((casilla[0], casilla[1]))

    def actualizar_timeout(self):
        
        self.servidor.timeout = self.time.value() 
        self.timer_s.setInterval(self.time.value())

    def actualiza_timer(self):
        
        valor = self.spinBox.value()
        self.timer.setInterval(valor)

    def dibujar_snakes(self):
        
        for serpiente in self.num_snakes:
            for seccion_corporal in serpiente.casillas:
                self.Tabla.item(seccion_corporal[0], seccion_corporal[1]).setBackground(QtGui.QColor(serpiente.color['r'], serpiente.color['g'], serpiente.color['b']))

    def actualiza_tabla(self):
        
        num_filas = self.spinBox_3.value() 
        num_columnas = self.spinBox_2.value()
        self.Tabla.setRowCount(num_filas)
        self.Tabla.setColumnCount(num_columnas)
        self.pintar_tabla()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ventana = MainWindow()
    sys.exit(app.exec_()) 