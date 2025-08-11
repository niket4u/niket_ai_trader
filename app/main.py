
import threading
from .bot import main_loop
from .dashboard import run

if __name__ == "__main__":
    t1 = threading.Thread(target=main_loop, daemon=True)
    t1.start()
    run()
