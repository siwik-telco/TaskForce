import sys
import os
from datetime import datetime, timedelta
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QDateTime
from PyQt5.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon

from killAllNetwork import WindowsSiteBlocker
from killAllProcesses import SecureProcessBlocker
from TFgui import TaskForceWidget
from TFwidget import SlidingCountdown

class TaskForceController:
    def __init__(self):
        self.network_blocker = WindowsSiteBlocker()
        self.process_blocker = SecureProcessBlocker()
        self.main_gui = None
        self.countdown_widget = None
        self.session_timer = QTimer()
        self.break_timer = QTimer()
        self.tray_icon = None

        """ States of application """
        self.is_session_active = False
        self.session_start_time = None
        self.session_duration = 0
        self.break_interval = 30*60
        self.remaining_time = 0

        self._session_timers()
        self._create_gui()
        self._setup_tray_icon()

    def _setup_timer(self):
        self.session_timer.timeout.connect(self._on_session_end)
        self.session_timer.timeout.connect(self._show_break_notification)
    
    def _create_gui(self):
        self.main_gui = TaskForceWidget()
        self._connect_main_gui_buttons()



    def _connect_main_gui_buttons():
        
        start_btn = None
        stop_btn = None
        plan_btn = None

        for i in range(self.main_gui.layout().count()):
            item = self.main_gui.layout().itemAt(i)
            if hasattr(item, 'layout') and item.layout():
                for j in range(item.layout().count()):
                    widget = item.layout().itemAt(j).widget()
                    if hasattr(widget, 'text'):
                        if widget.text() == "Start":
                            start_btn = widget
                        elif widget.text() == "Stop":
                            stop_btn == widget
                        elif widget.text() == "Plan in advance":
                            plan_btn = widget
        if start_btn:
            start_btn.clicked.disconnect()
            start_btn.clicked.connect(self.start_focus_session)

        if stop_btn:
            stop_btn.clicked.connect(self.stop_focus_session)

        if plan_btn:
            plan_btn.clicked.connect(self.schedule_session)

    def _setup_tray_icon(self):
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon()

            tray_menu = QMenu()
            show_action = tray_menu.addAction("Show main window")
            show_action.triggered.connect(self.show_main_window)

            stop_action = tray_menu.addAction("Stop session!")
            stop_action.triggered.connect(self.stop_focus_session)

            tray_menu.addSeparator()

            quit_action = tray_menu.addAction("Quit")        
            quit_action.triggered.connect(self.quit_application)
            self.tray_icon.show()
    
    
       
    
       