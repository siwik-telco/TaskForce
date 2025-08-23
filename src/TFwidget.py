# -*- coding: utf-8 -*-
"""
Mini-widget (PyQt5) przypięty w **lewym górnym rogu** pulpitu Windows.
Pokazuje odliczanie i przycisk „Cheat”.

• Brak logiki blokowania – sam front-end.
• Zawsze na wierzchu, bez ramki, nie pojawia się na pasku zadań.
"""

import sys
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QMessageBox
)


class DesktopCountdown(QWidget):
    def __init__(self, seconds_left=3600):
        super().__init__()
        self.seconds_left = seconds_left
        self.cheat_used = False

        self._build_ui()
        self._start_timer()

    # ---------- UI ----------
    def _build_ui(self):
        self.setFixedSize(200, 110)
        self.setWindowTitle("TaskForce")
        self.setWindowFlags(
            Qt.FramelessWindowHint      |  # bez ramki
            Qt.WindowStaysOnTopHint     |  # zawsze na wierzchu
            Qt.Tool                     |  # brak na pasku zadań
            Qt.X11BypassWindowManagerHint   # minimalne dekoracje
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Odliczanie
        self.time_lbl = QLabel(self._fmt(self.seconds_left))
        self.time_lbl.setAlignment(Qt.AlignCenter)
        self.time_lbl.setStyleSheet("font: 700 24px 'Segoe UI'; color:#FFFFFF;")

        # Cheat
        cheat_btn = QPushButton("Cheat\n1 raz / tydzień")
        cheat_btn.clicked.connect(self._cheat)
        cheat_btn.setStyleSheet(
            "QPushButton{background:#ffaa00;font-weight:600;border:none;border-radius:6px;}"
            "QPushButton:pressed{background:#ff8800;}"
        )

        # Layout
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.time_lbl, alignment=Qt.AlignCenter)
        vbox.addWidget(cheat_btn, alignment=Qt.AlignCenter)
        vbox.setContentsMargins(8, 8, 8, 8)

        # Tło z lekkim gradientem
        self.setStyleSheet("""
            QWidget{
                background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                            stop:0 #3b3b3b, stop:1 #1e1e1e);
                border:2px solid #000; border-radius:12px;
            }""")

    # ---------- Timer ----------
    def _start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def _tick(self):
        if self.seconds_left <= 0:
            self.timer.stop()
            self.time_lbl.setText("00:00")
            return
        self.seconds_left -= 1
        self.time_lbl.setText(self._fmt(self.seconds_left))

    # ---------- Cheat ----------
    def _cheat(self):
        if self.cheat_used:
            QMessageBox.information(self, "Cheat",
                                    "Cheat już wykorzystany w tym tygodniu!")
            return
        # tu podłącz odblokowanie
        QMessageBox.information(self, "Cheat", "Cheat aktywowany!")
        self.cheat_used = True

    # ---------- Pozycjonowanie ----------
    def showEvent(self, event):
        super().showEvent(event)
        # Lewy górny róg dostępnej przestrzeni ekranu[75]
        screen_geo = QApplication.primaryScreen().availableGeometry()
        margin = 6
        self.move(screen_geo.left() + margin, screen_geo.top() + margin)

    # ---------- Util ----------
    @staticmethod
    def _fmt(sec):
        return QTime(0, 0).addSecs(sec).toString("hh:mm:ss")


# ----------------- demo -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DesktopCountdown(seconds_left=5400)     # 90 minut demo
    w.show()
    sys.exit(app.exec_())
