import sys
import time
import subprocess
import threading

class Loader:
    def __init__(self, interval=0.2):
        self.GRAY = "\033[90m"
        self.BLUE = "\033[94m"
        self.GREEN = "\033[92m"
        self.BOLD = "\033[1m"
        self.RESET = "\033[0m"

        self.bullets = ["‣", "‣", "‣"]
        self.interval = interval
        self.step = 0
        self.running = False

    def start(self, message="Loading"):
        self.running = True
        self.thread = threading.Thread(target=self._animate, args=(message,), daemon=True)
        self.thread.start()

    def _animate(self, message):
        while self.running:
            line = f"{message}\t"
            for i, bullet in enumerate(self.bullets):
                if i == self.step % len(self.bullets):
                    line += f"{self.BOLD}{self.BLUE}{bullet}{self.RESET} "
                else:
                    line += f"{self.GRAY}{bullet}{self.RESET} "
            sys.stdout.write("\r" + line)
            # sys.stdout.flush()
            self.step += 1
            time.sleep(self.interval)

    def stop(self, message="Done!\n", completed_symbol="[✓]"):
        self.running = False
        self.thread.join()
        # Clear the line
        #sys.stdout.write("\r" + " " * 80 + "\r")
        # sys.stdout.flush()
        # Print completed message with symbol
        print(f"\n{completed_symbol} {message}")