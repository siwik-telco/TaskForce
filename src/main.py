import sys
import os
import ctypes
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

        
        self.is_session_active = False
        self.session_start_time = None
        self.session_duration = 0
        self.break_interval = 30*60
        self.remaining_time = 0

        self._setup_timer()  
        self._create_gui()
        self._setup_tray_icon()

    def _setup_timer(self):
        self.session_timer.timeout.connect(self._on_session_end)
        self.break_timer.timeout.connect(self._show_break_notification)  

    def _create_gui(self):
        self.main_gui = TaskForceWidget()
        self._connect_main_gui_buttons()

    def _connect_main_gui_buttons(self):
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
                            stop_btn = widget  
                        elif widget.text() == "Zaplanuj do przodu": 
                            plan_btn = widget

        if start_btn:
            start_btn.clicked.disconnect()
            start_btn.clicked.connect(self.start_focus_session)

        if stop_btn:
            stop_btn.clicked.disconnect()  
            stop_btn.clicked.connect(self.stop_focus_session)

        if plan_btn:
            plan_btn.clicked.disconnect()  
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
            
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.setToolTip("TaskForce - Focus App")
            self.tray_icon.show()

    def start_focus_session(self):
        if self.is_session_active:
            QMessageBox.information(self.main_gui, "Info", "Session is already in progress!")
            return

        duration_seconds = self._get_session_duration_from_gui()
        break_interval = self._get_break_interval_from_gui()

        if duration_seconds <= 0:
            QMessageBox.warning(self.main_gui, "Error", "Incorrect duration of session!")
            return

        try:
            self.network_blocker.start()
            self.process_blocker.start_blocking() 
            
            self.is_session_active = True  
            self.session_start_time = datetime.now()
            self.session_duration = duration_seconds  # 
            self.break_interval = break_interval
            self.remaining_time = duration_seconds

            self._show_countdown_widget(duration_seconds)

            self.session_timer.start(duration_seconds * 1000)  
            self.break_timer.start(break_interval * 1000)

            self.main_gui.hide()

            QMessageBox.information(self.main_gui, "Success", 
                                  f"Focus session started - duration: {duration_seconds}s,\n break every: {break_interval}s.")
                                  
        except Exception as e:
            QMessageBox.critical(self.main_gui, "Error", f"Could not start session :( \n {str(e)}")

    def stop_focus_session(self):
        if not self.is_session_active:
            QMessageBox.information(self.main_gui, "Info", "No session is active")
            return
            
        try:
            self.network_blocker.stop()
            self.process_blocker.stop_blocking()

            self.session_timer.stop()
            self.break_timer.stop()

            if self.countdown_widget:
                self.countdown_widget.close()
                self.countdown_widget = None

            self.is_session_active = False
            self.session_start_time = None
            self.main_gui.show()
            self.main_gui.raise_()
            self.main_gui.activateWindow()
            
            QMessageBox.information(self.main_gui, "Finished!", "Focus session has been finished! Well done!")
            print("TaskForce: Session stopped by user.")
            
        except Exception as ee:
            QMessageBox.critical(self.main_gui, "Error", f"An error occurred while stopping session :( \n {str(ee)}")

    def schedule_session(self):
        start_time = self._get_scheduled_start_time_from_gui()

        if not start_time or start_time <= datetime.now():
            QMessageBox.warning(self.main_gui, "Error", "Incorrect time of beginning")
            return
            
        time_to_start = (start_time - datetime.now()).total_seconds()
        QTimer.singleShot(int(time_to_start * 1000), self.start_focus_session)
        QMessageBox.information(self.main_gui, "Scheduled!", 
                              f"Session will be started at {start_time.strftime('%H:%M')}")  
        print(f"TaskForce: Session has been scheduled at {start_time}")

    def _show_countdown_widget(self, seconds):
        self.countdown_widget = SlidingCountdown(seconds_left=seconds)
        self.countdown_widget.show()

    def _get_session_duration_from_gui(self):
        try:
            return 3600  
        except:
            return 3600

    def _get_break_interval_from_gui(self):
        try:
            return 25 * 60  
        except:
            return 25 * 60

    def _get_scheduled_start_time_from_gui(self):
        try:
            return datetime.now() + timedelta(minutes=1)
        except:
            return None

    def _on_session_end(self):
        self.session_timer.stop()
        self.stop_focus_session()
        QMessageBox.information(None, "Session finished!", 
                              "Your focus session has been finished. \n Time to rest ;)")

    def _show_break_notification(self):
        if self.is_session_active:
            QMessageBox.information(None, "Break time!", "Make a short break, stretch yourself!")
            
            self.break_timer.start(self.break_interval * 1000)

    def show_main_window(self):
        self.main_gui.show()
        self.main_gui.raise_()
        self.main_gui.activateWindow()

    def quit_application(self):
        if self.is_session_active:
            reply = QMessageBox.question(None, "Quit?", "Session is active, you sure you want to quit?", 
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
                
        if self.is_session_active:
            self.stop_focus_session()  
            
        if self.main_gui:
            self.main_gui.close()
        if self.countdown_widget:
            self.countdown_widget.close()

        QApplication.quit()


def _is_admin(): 
    try:
        return os.getuid() == 0
    except AttributeError:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False


def main():  
    app = QApplication(sys.argv)
    
    if not _is_admin():
        QMessageBox.critical(None, "Permission error!", 
                           "TaskForce requires administrator permission to run, since it blocks system processes.\n"
                           "Run the app with administrator permission.")
        sys.exit(1)

    controller = TaskForceController()  
    controller.show_main_window()
    app.aboutToQuit.connect(controller.quit_application)
    sys.exit(app.exec_())


if __name__ == "__main__": 
    main()
