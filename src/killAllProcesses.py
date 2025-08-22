import psutil
import threading
import time
import os

class SecureProcessBlocker:
    def __init__(self):
        self.blocking_active = False
        self.baseline_processes = set()
        self.focus_start_time = None
        self.monitor_thread = None
        
        
        self.allowed_apps = [
            'chrome.exe', 'firefox.exe', 'msedge.exe',
            'winword.exe', 'excel.exe', 'powerpnt.exe', 'outlook.exe',
            'code.exe', 'notepad.exe', 'notepad++.exe'
        ]
        
       
        self.critical_processes = {
        
            'csrss.exe', 'winlogon.exe', 'wininit.exe', 'services.exe', 
            'lsass.exe', 'smss.exe', 'dwm.exe', 'explorer.exe',
            'svchost.exe', 'System', 'Registry', 'fontdrvhost.exe',
            'conhost.exe', 'RuntimeBroker.exe', 'SearchIndexer.exe',
            'audiodg.exe', 'spoolsv.exe', 'taskhostw.exe',
        }
    
    def start_blocking(self):
        
        if self.blocking_active:
            return False
        
        print("Starting process blocking...")
        
        
        self.baseline_processes = {p.pid for p in psutil.process_iter()}
        self.focus_start_time = time.time()
        self.blocking_active = True
        
        
        self.monitor_thread = threading.Thread(target=self._process_monitor, daemon=True)
        self.monitor_thread.start()
        
        print(f"Process blocking started. Baseline: {len(self.baseline_processes)} processes")
        return True
    
    def stop_blocking(self):
        """Kończy blokowanie procesów"""
        if not self.blocking_active:
            return False
        
        print("Stopping process blocking...")
        self.blocking_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        
        print("Process blocking stopped")
        return True
    
    def _process_monitor(self):
      
        print("Process monitor started")
        
        while self.blocking_active:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'create_time', 'username', 'ppid']):
                    try:
                        
                        if (proc.info['pid'] not in self.baseline_processes and 
                            proc.info['create_time'] > self.focus_start_time):
                            
                            if self._should_terminate_process(proc):
                                self._terminate_process_safely(proc)
                                print(f"✗ Blocked: {proc.info['name']} (PID: {proc.info['pid']})")
                            else:
                                print(f"✓ Allowed: {proc.info['name']} (PID: {proc.info['pid']})")
                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                        continue
                    
            except Exception as e:
                print(f"Monitor error: {str(e)}")
            
            time.sleep(2) 
        
        print("Process monitor stopped")
    
    def _should_terminate_process(self, process):
        """Sprawdza czy proces powinien być zabity"""
        try:
            proc_info = process.info
            proc_name = proc_info['name'].lower()
            
            
            if any(critical.lower() in proc_name for critical in self.critical_processes):
                return False
            
            
            if proc_info['pid'] < 1000:
                return False
            
            
            username = proc_info.get('username', '').lower()
            if username in ['system', 'root', 'daemon', 'nt authority\\system']:
                return False
            
            
            if proc_info.get('ppid', 0) in [0, 1]:
                return False
            
            
            if 'python' in proc_name and proc_info['pid'] == os.getpid():
                return False
            
            
            if any(allowed.lower() in proc_name for allowed in self.allowed_apps):
                return False
            
            return True
            
        except Exception as e:
            print(f"Error checking process {process}: {e}")
            return False
    
    def _terminate_process_safely(self, process):
        
        try:
            proc_name = process.info['name']
            proc_pid = process.info['pid']
            
            
            process.terminate()
            
            
            try:
                process.wait(timeout=3)
                print(f"  → Gracefully terminated: {proc_name} (PID: {proc_pid})")
            except psutil.TimeoutExpired:
                
                process.kill()
                print(f"  → Force killed: {proc_name} (PID: {proc_pid})")
                
        except psutil.NoSuchProcess:
            
            pass
        except psutil.AccessDenied:
            print(f"  → Access denied for: {process.info['name']}")
        except Exception as e:
            print(f"  → Error terminating process: {e}")
    
    def add_allowed_app(self, app_name):
        
        if app_name not in self.allowed_apps:
            self.allowed_apps.append(app_name)
            print(f"Added to allowed apps: {app_name}")
    
    def remove_allowed_app(self, app_name):
        
        if app_name in self.allowed_apps:
            self.allowed_apps.remove(app_name)
            print(f"Removed from allowed apps: {app_name}")
    
    def get_status(self):
        
        return {
            'active': self.blocking_active,
            'baseline_processes': len(self.baseline_processes),
            'allowed_apps': len(self.allowed_apps),
            'uptime': time.time() - self.focus_start_time if self.focus_start_time else 0
        }


if __name__ == "__main__":
    blocker = SecureProcessBlocker()
    
    try:
        
        blocker.add_allowed_app('spotify.exe')
        
       
        blocker.start_blocking()
        
        print("Process blocking active. Press Ctrl+C to stop...")
        
        
        while True:
            time.sleep(10)
            status = blocker.get_status()
            print(f"Status: Active={status['active']}, Uptime={status['uptime']:.1f}s")
            
    except KeyboardInterrupt:
        print("\nStopping...")
        blocker.stop_blocking()
        print("Done.")
