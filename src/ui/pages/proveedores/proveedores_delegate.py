from PySide6.QtWidgets import QStyledItemDelegate, QPushButton
from PySide6.QtCore import Signal, Qt, QEvent

class ProveedorPerfilButtonDelegate(QStyledItemDelegate):
    clicked = Signal(int)  # row

    def createEditor(self, parent, option, index):
        # No esperamos usar editor porque la vista tiene NoEditTriggers,
        # pero dejamos el método por compatibilidad.
        btn = QPushButton("Perfil", parent)
        btn.setObjectName("Primary")
        btn.clicked.connect(lambda: self.clicked.emit(index.row()))
        return btn

    def paint(self, painter, option, index):
        # Pintamos una “píldora” simple con el texto Perfil
        if option.state & QStyledItemDelegate.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        painter.drawText(option.rect, Qt.AlignCenter, "Perfil")

    def editorEvent(self, event, model, option, index):
        # Emitir SOLO cuando se suelta el botón izquierdo del mouse
        if event.type() == QEvent.MouseButtonRelease and getattr(event, "button", lambda: None)() == Qt.LeftButton:
            self.clicked.emit(index.row())
            return True
        return False
