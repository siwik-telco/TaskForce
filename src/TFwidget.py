import sys
from PyQt5.QtCore import Qt, QTimer, QTime, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox   
)



class SlidingCountdown(QWidget):
    HANDLE_W = 26           
    MARGIN   = 6            

    def __init__(self, seconds_left=3600):
        super().__init__()
        self.seconds_left = seconds_left
        self.cheat_used   = False
        self.is_visible   = False   
        self.anim         = None

        self._build_ui()
        self._start_timer()

    
    def _build_ui(self):
        self.setFixedSize(200, 110)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        
        self.time_lbl = QLabel(self._fmt(self.seconds_left))
        self.time_lbl.setAlignment(Qt.AlignCenter)
        self.time_lbl.setStyleSheet("font:700 24px 'Segoe UI'; color:#fff;")

        
        cheat_btn = QPushButton("Cheat\nonce a / week")
        cheat_btn.clicked.connect(self._cheat)
        cheat_btn.setStyleSheet(
            "QPushButton{background:#ffaa00;font-weight:600;border:none;"
            "border-radius:6px;}QPushButton:pressed{background:#ff8800;}")

       
        self.handle_btn = QPushButton("▶")
        self.handle_btn.setFixedWidth(self.HANDLE_W)
        self.handle_btn.clicked.connect(self._toggle_slide)
        self.handle_btn.setStyleSheet(
            "QPushButton{background:#333;color:#fff;border:none;font:700 16px;}"
            "QPushButton:hover{background:#555;}")

       
        panel_layout = QVBoxLayout()
        panel_layout.addWidget(self.time_lbl, alignment=Qt.AlignCenter)
        panel_layout.addWidget(cheat_btn, alignment=Qt.AlignCenter)
        panel_layout.setContentsMargins(8, 8, 0, 8)

        main = QWidget()
        main.setLayout(panel_layout)
        main.setStyleSheet("""
            QWidget{
                background:qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                           stop:0 #3b3b3b, stop:1 #1e1e1e);
                border:2px solid #000; border-top-left-radius:12px;
                border-bottom-left-radius:12px;
            }""")

     
        wrapper = QVBoxLayout(self)
        wrapper.setContentsMargins(0, 0, 0, 0)
        row = QHBoxLayout()
        row.setSpacing(0)
        row.addWidget(main)
        row.addWidget(self.handle_btn)
        wrapper.addLayout(row)

  
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

    def _cheat(self):
        if self.cheat_used:
            QMessageBox.information(self, "Cheat",
                                    "Cheat has been used this week!")
            return
        QMessageBox.information(self, "Cheat", "Cheat activated!")
        self.cheat_used = True

    
    def _toggle_slide(self):
        scr   = QApplication.primaryScreen().availableGeometry()
        full  = self.frameGeometry()
        shown_x  = scr.left() + self.MARGIN
        hidden_x = shown_x - (full.width() - self.HANDLE_W)

        end_x = shown_x if not self.is_visible else hidden_x
        self.is_visible = not self.is_visible

        
        self.handle_btn.setText("◀" if self.is_visible else "▶")

        
        self.anim = QPropertyAnimation(self, b"pos", self)
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setEndValue(QPoint(end_x, scr.top() + self.MARGIN))
        self.anim.start()

    
    def showEvent(self, ev):
        scr = QApplication.primaryScreen().availableGeometry()
        hidden_x = scr.left() + self.MARGIN - (self.width() - self.HANDLE_W)
        self.move(hidden_x, scr.top() + self.MARGIN)
        super().showEvent(ev)

    
    @staticmethod
    def _fmt(sec):
        return QTime(0, 0).addSecs(sec).toString("hh:mm:ss")


if __name__ == "__main__":
    from PyQt5.QtCore import QPoint  
    app = QApplication(sys.argv)
    w = SlidingCountdown(seconds_left=5400) 
    w.show()
    sys.exit(app.exec_())
