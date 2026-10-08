import subprocess
import sys

print("Устанавливаю библиотеки, подождите...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip", "gTTS"])
print("Успешно! Библиотеки установлены. Теперь можно запускать основной скрипт.")

# Окно не закроется, пока пользователь не нажмет Enter
input("\nНажмите Enter, чтобы закрыть это окно...")
