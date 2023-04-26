'''
Created on 23.06.2015

@author: jrenken
'''

import sys
from qgis.PyQt.QtCore import pyqtSignal, Qt, QPoint, QSize, pyqtSlot, pyqtProperty
from qgis.PyQt.QtWidgets import QWidget, QSpinBox, QVBoxLayout
from qgis.PyQt.QtGui import QPainter, QPalette, QFont, QFontMetricsF, QPen, QPolygon


class CompassWidget(QWidget):

    angleChanged = pyqtSignal(float)
    angle2Changed = pyqtSignal(float)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._angle = -9999.9
        self._angle2 = -9999.9
        self._margins = 10
        self._pointText = {0: "N", 45: "45", 90: "90", 135: "135", 180: "S",
                           225: "225", 270: "270", 315: "315"}

    def paintEvent(self, event):
        if self.height() < 40:
            return
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), self.palette().brush(QPalette.Window))
        self.drawMarkings(painter)
        self.drawNeedle(painter)
        self.drawNeedle2(painter)
        painter.end()

    def drawMarkings(self, painter):
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)

        font = QFont(self.font())
        font.setPixelSize(10)
        metrics = QFontMetricsF(font)

        painter.setFont(font)
        painter.setPen(self.palette().color(QPalette.Shadow))

        i = 0
        while i < 360:
            if i % 45 == 0:
                painter.drawLine(0, -40, 0, -50)
                painter.drawText(int(-metrics.width(self._pointText[i]) / 2), -52,
                                 self._pointText[i])
            else:
                painter.drawLine(0, -45, 0, -50)
            painter.rotate(15)
            i += 15
        painter.restore()

    def drawNeedle(self, painter):
        if self._angle < -9999:
            return
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)

        painter.setPen(QPen(Qt.NoPen))
#         painter.setBrush(self.palette().brush(QPalette.Shadow))
#
#         painter.drawPolygon(
#             QPolygon([QPoint(-10, 0), QPoint(0, -45), QPoint(10, 0),
#                       QPoint(0, 45), QPoint(-10, 0)])
#             )

        painter.setBrush(self.palette().brush(QPalette.Highlight))

        painter.drawPolygon(
            QPolygon([QPoint(-5, -25), QPoint(0, -45), QPoint(5, -25),
                      QPoint(0, -30), QPoint(-5, -25)])
            )

        painter.restore()

    def drawNeedle2(self, painter):
        if self._angle2 < -9999:
            return
        painter.save()
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._angle2)
        scale = min((self.width() - self._margins) / 120.0,
                    (self.height() - self._margins) / 120.0)
        painter.scale(scale, scale)

        painter.setPen(QPen(Qt.NoPen))
#         painter.setBrush(self.palette().brush(QPalette.Dark))
#
#         painter.drawPolygon(
#             QPolygon([QPoint(-7, 0), QPoint(0, -25), QPoint(7, 0),
#                       QPoint(0, 25), QPoint(-7, 0)])
#             )

        painter.setBrush(self.palette().brush(QPalette.Foreground))

        painter.drawPolygon(
            QPolygon([QPoint(-5, -10), QPoint(0, -25), QPoint(5, -10),
                      QPoint(0, -13), QPoint(-5, -10)])
            )

        painter.restore()

    def sizeHint(self):
        return QSize(150, 150)

    def angle(self):
        return self._angle

    def angle2(self):
        return self._angle2

    @pyqtSlot(float)
    def setAngle(self, angle):
        if angle != self._angle:
            self._angle = angle
            self.angleChanged.emit(angle)
            self.update()
    angle = pyqtProperty(float, angle, setAngle)

    @pyqtSlot(float)
    def setAngle2(self, angle):
        if angle != self._angle2:
            self._angle2 = angle
            self.angle2Changed.emit(angle)
            self.update()
    angle2 = pyqtProperty(float, angle2, setAngle2)

    def reset(self, no=None):
        if no == 1:
            self._angle = -9999.9
        elif no == 2:
            self._angle2 = -9999.9
        else:
            self._angle = -9999.9
            self._angle2 = -9999.9
        self.update()


if __name__ == "__main__":
    from qgis.PyQt.Qt import QApplication

    app = QApplication(sys.argv)

    window = QWidget()
    compass = CompassWidget()
    spinBox = QSpinBox()
    spinBox.setRange(0, 719)
    spinBox.valueChanged.connect(compass.setAngle)
    spinBox2 = QSpinBox()
    spinBox2.setRange(0, 719)
    spinBox2.valueChanged.connect(compass.setAngle2)

    layout = QVBoxLayout()
    layout.addWidget(compass)
    layout.addWidget(spinBox)
    layout.addWidget(spinBox2)
    window.setLayout(layout)

    window.show()
    sys.exit(app.exec_())
