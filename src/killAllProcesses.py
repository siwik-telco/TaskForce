import psutil 
import subproces

def kill_unwanted_processes():
    allowed = ['chrome.exe', 'firefox.exe', 'brave.exe', 'excel.exe', 'word.exe', 'powerpoint.exe', 'notepad.exe']
    
    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        if proc.info['name'] not in allowed:
            if proc.info['create_time'] > focus_start_time:
                proc.kill()