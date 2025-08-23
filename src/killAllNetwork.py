import os
import subprocess
import time

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"  
REDIRECT_IPv4 = "127.0.0.1"
REDIRECT_IPv6 = "::1"


ALLOWED = {
    
    "google.com", "www.google.com", "google.pl",
    "googleapis.com", "gstatic.com", "accounts.google.com",
    "drive.google.com", "docs.google.com", "sheets.google.com",
    "slides.google.com", "forms.google.com",

    
    "wikipedia.org", "www.wikipedia.org", "en.wikipedia.org",
    "pl.wikipedia.org", "wikimedia.org",

    
    "miro.com", "www.miro.com", "realtimeboard.com",

    
    "spotify.com", "www.spotify.com", "open.spotify.com",
    "accounts.spotify.com", "api.spotify.com",
}


BLOCKLIST = {
    "facebook.com", "instagram.com", "twitter.com", "x.com", "tiktok.com",
    "youtube.com", "netflix.com", "reddit.com", "linkedin.com",
    "twitch.tv", "pinterest.com", "discord.com",
    "whatsapp.com", "telegram.org",
    "amazon.com", "allegro.pl", "olx.pl",
    "onet.pl", "wp.pl", "gazeta.pl"
}


class WindowsSiteBlocker:
    def __init__(self):
        self.backup = None
        self.active = False

   
    def start(self):
        
        if self.active:
            return
        self._backup_hosts()
        self._append_block_entries()
        self._flush_dns()
        self.active = True
        print(f"Blocking activated, {len(BLOCKLIST)} domains forwarded.")

    def stop(self):
        
        if not self.active or self.backup is None:
            return
        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            f.write(self.backup)
        self._flush_dns()
        self.active = False
        print("Blocking domains has been shut down.")

    
    def _backup_hosts(self):
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            self.backup = f.read()

    def _append_block_entries(self):
        entries = ["\n# ===== TaskForce DOMAINblock START ====="]
        for domain in BLOCKLIST:
            if domain in ALLOWED:
                continue          
            entries += [
                f"{REDIRECT_IPv4} {domain}",
                f"{REDIRECT_IPv4} www.{domain}",
                f"{REDIRECT_IPv6} {domain}",
                f"{REDIRECT_IPv6} www.{domain}",
            ]
        entries.append("# ===== TaskForce DOMAINblock END =====\n")

        with open(HOSTS_PATH, "a", encoding="utf-8") as f:
            f.write("\n".join(entries))

    @staticmethod
    def _flush_dns():
        
        subprocess.run("ipconfig /flushdns",
                       shell=True, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    blocker = WindowsSiteBlocker()
    try:
        blocker.start()
        print("Only approved domains can be obtained from DNS...")
        print("ctr+c = cancel")
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nRestoring...")
        blocker.stop()
