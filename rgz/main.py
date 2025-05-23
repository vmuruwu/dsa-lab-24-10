import subprocess
import sys


def run_services():
    # Запускаем service.py
    service_process = subprocess.Popen([sys.executable, "service.py"])

    # Запускаем bot.py
    bot_process = subprocess.Popen([sys.executable, "bot.py"])

    try:
        service_process.wait()
        bot_process.wait()
    except KeyboardInterrupt:
        service_process.terminate()
        bot_process.terminate()


if __name__ == "__main__":
    run_services()
