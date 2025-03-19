from PyQt6.QtCore import QRect
from PyQt6.QtWidgets import QApplication


def get_centered_geometry(width: int, height: int) -> QRect:
    screen = QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()

    center_x = screen_geometry.x() + (screen_geometry.width() // 2)
    center_y = screen_geometry.y() + (screen_geometry.height() // 2)

    x = center_x - (width // 2)
    y = center_y - (height // 2)

    return QRect(x, y, width, height)

