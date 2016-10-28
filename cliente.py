import sys
from PyQt4 import QtGui, uic, QtCore
from xmlrpc.client import ServerProxy

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('cliente.ui', self)
        self.columnas()
        self.setStyleSheet("QMainWindow {background-color: #ACE7EF;}")
        self.pushButton.clicked.connect(self.admin_servidor)
        self.pushButton_2.clicked.connect(self.integrante_juego)
        self.pushButton_2.clicked.connect(self.reiniciar)
        self.id_usuario = 0
        self.direccion = 2
        self.Tabla.setSelectionMode(QtGui.QTableWidget.NoSelection)
        self.usuario = False
        self.muerto = False
        self.servidor = 0
        self.timer= QtCore.QTimer(self)
        self.timer.timeout.connect(self.actualizar_tabla)
        self.timer.timeout.connect(self.inicia_juego)
        self.timer.timeout.connect(self.actualizar_timer)
        self.timer.start(self.servidor)
        self.server = None
        self.show()

    def inicia_juego(self):
        
        if self.usuario:
            if self.moriste():
                continue
            self.Tabla.installEventFilter(self)
            diccionario = self.server.estado_del_juego()
            lista_viboras = diccionario["viboras"]
            for vibora in lista_viboras:
                lista_camino = vibora["camino"]
                colores = vibora["color"]
                self.dibuja_vibora(lista_camino, colores)

    def actualizar_timer(self):
        
        if self.usuario:
            diccionario = self.server.estado_del_juego()
            intervalo = diccionario["espera"]
            if self.servidor != intervalo:
                self.servidor = intervalo
                self.timer.setInterval(self.servidor)

    def eventFilter(self, source, event):
       
        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.Tabla): 
                key = event.key() 
                if (key == QtCore.Qt.Key_Up and
                    source is self.Tabla):
                    if self.direccion != 2:
                        self.direccion = 0
                elif (key == QtCore.Qt.Key_Down and
                    source is self.Tabla):
                    if self.direccion != 0:
                        self.direccion = 2
                elif (key == QtCore.Qt.Key_Right and
                    source is self.Tabla):
                    if self.direccion != 3:
                        self.direccion = 1
                elif (key == QtCore.Qt.Key_Left and
                    source is self.Tabla):
                    if self.direccion != 1:
                        self.direccion = 3
                self.server.cambia_direccion(self.id_usuario, self.direccion)
        return QtGui.QMainWindow.eventFilter(self, source, event) 

    def integrante_juego(self):
        
        try:
            self.crea_servidor()
            informacion = self.server.yo_juego()
            self.lineEdit.setText(informacion["id"])
            self.id_usuario = informacion["id"]
            self.color = informacion["color"]
            self.red = self.color["r"]
            self.green = self.color["g"]
            self.blue = self.color["b"]
            self.lineEdit_2.setText("R:" + str(self.red) + " G:" + str(self.green) + " B:" + str(self.blue))
            self.lineEdit_2.setStyleSheet('QLineEdit {background-color: rgb('+str(self.red)+','+ str(self.green) + ',' + str(self.blue)+');}')
            self.usuario = True 
        except: 
            self.lineEdit.setText("Conexión fallida.")
            self.lineEdit_2.setText("URL y puerto incorrectos.")

    def admin_servidor(self):
        
        self.pushButton.setText("Pinging...")
        try:
            self.crea_servidor()
            pong = self.server.ping()
            self.pushButton.setText("¡Pong!")
        except: 
            self.pushButton.setText("No PONG :(")

    def dibuja_vibora(self, lista_camino, colores):
        
        for tupla in lista_camino:
            self.Tabla.item(tupla[0], tupla[1]).setBackground(QtGui.QColor(colores['r'], colores['g'], colores['b']))

    def crea_servidor(self):
       
        self.url = self.lineEdit_3.text()
        self.port = self.spinBox.value() 
        self.direccion = "http://" + self.url + ":" + str(self.port)
        self.server = ServerProxy(self.direccion)

    def columnas(self):
        self.Tabla.horizontalHeader().setStretchLastSection(True)
        self.Tabla.verticalHeader().setStretchLastSection(True)
        self.Tabla.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.Tabla.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def actualizar_tabla(self):
        
        if self.usuario:
            game = self.server.estado_del_juego()
            self.Tabla.setRowCount(game["tamY"])
            self.Tabla.setColumnCount(game["tamX"])

    def moriste(self):
        
        diccionario = self.server.estado_del_juego()
        lista_serpientes = diccionario["viboras"]
        for vibora in lista_serpientes:
            if vibora["id"] == self.id_usuario:
                return False
        self.muerto = True
        return True

    def reiniciar(self):
        
        if self.muerto: 
            self.muerto = False
            self.lineEdit.setText("")
            self.lineEdit.setText("")
            self.integrante_juego()
            self.timer.start()
            self.inicia_juego() 

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())