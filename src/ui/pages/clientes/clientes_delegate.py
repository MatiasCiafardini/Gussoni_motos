from PySide6.QtWidgets import QStyledItemDelegate, QPushButton
from PySide6.QtCore import Signal, Qt

class PerfilButtonDelegate(QStyledItemDelegate):
    clicked = Signal(int)  # row

    def createEditor(self, parent, option, index):
        btn = QPushButton("Perfil", parent)
        btn.setObjectName("Primary")
        btn.clicked.connect(lambda: self.clicked.emit(index.row()))
        return btn

    def paint(self, painter, option, index):
        if option.state & QStyledItemDelegate.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        painter.drawText(option.rect, Qt.AlignCenter, "Perfil")

    def editorEvent(self, event, model, option, index):
        self.clicked.emit(index.row())
        return True
