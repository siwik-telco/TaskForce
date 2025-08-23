import sys
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QGridLayout,
    QDateEdit, QTimeEdit, QGroupBox, QVBoxLayout, QHBoxLayout
)


class TaskForceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Merituum's TaskForce")
        self.setFixedSize(500, 320)         
        self.setStyleSheet("font-family: Segoe UI, Arial; font-size: 10.5pt;")

        self._build_ui()

   
    def _build_ui(self):
        
        outer = QGridLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        
        self._add_top_buttons(outer)

        
        self._add_time_picker(outer)

        
        self._add_cheat_button(outer)

   
    def _add_top_buttons(self, layout):
        start_btn = QPushButton("Start")
        stop_btn = QPushButton("Stop")
        plan_btn = QPushButton("Zaplanuj do przodu")

        
        start_btn.clicked.connect(lambda: print("Start → TODO"))
        stop_btn.clicked.connect(lambda: print("Stop → TODO"))
        plan_btn.clicked.connect(lambda: print("Plan → TODO"))

        for b in (start_btn, stop_btn, plan_btn):
            b.setFixedSize(120, 36)

        
        top_row = QHBoxLayout()
        top_row.addStretch(1)
        top_row.addWidget(start_btn)
        top_row.addWidget(stop_btn)
        top_row.addWidget(plan_btn)
        top_row.addStretch(1)

        layout.addLayout(top_row, 0, 0)

    
    def _add_time_picker(self, layout):
        box = QGroupBox("Wyznacz czas")
        grid = QGridLayout()
        box.setLayout(grid)

       
        od_label = QLabel("Od:")
        od_date = QDateEdit(calendarPopup=True)
        od_date.setDate(QDate.currentDate())
        od_time = QTimeEdit()
        od_time.setTime(QTime.currentTime())

        
        do_label = QLabel("Do:")
        do_date = QDateEdit(calendarPopup=True)
        do_date.setDate(QDate.currentDate())
        do_time = QTimeEdit()
        do_time.setTime(QTime.currentTime().addSecs(3600))  

        
        br_label = QLabel("Po jakim czasie przerwa?")
        br_time = QTimeEdit()
        br_time.setDisplayFormat("HH:mm")  
        br_time.setTime(QTime(0, 25))

       
        grid.addWidget(od_label,   0, 0)
        grid.addWidget(od_date,    0, 1)
        grid.addWidget(od_time,    0, 2)

        grid.addWidget(do_label,   1, 0)
        grid.addWidget(do_date,    1, 1)
        grid.addWidget(do_time,    1, 2)

        grid.addWidget(br_label,   2, 0)
        grid.addWidget(br_time,    2, 1)

        layout.addWidget(box, 1, 0, alignment=Qt.AlignLeft | Qt.AlignTop)

    def _add_cheat_button(self, layout):
        cheat_btn = QPushButton("Cheat?\n1 raz na tydzień")
        cheat_btn.setFixedSize(180, 50)
        cheat_btn.clicked.connect(lambda: print("Cheat → TODO"))

       
        cheat_box = QVBoxLayout()
        cheat_box.addStretch(1)
        cheat_box.addWidget(cheat_btn, alignment=Qt.AlignLeft | Qt.AlignBottom)
        layout.addLayout(cheat_box, 2, 0)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TaskForceWidget()
    w.show()
    sys.exit(app.exec_())
