import multiprocessing
import queue as pyqueue
import time
import sys
import tkinter as tk

# --- Команды для очереди ---
CMD_ADD = 'add'
CMD_REMOVE = 'remove'
CMD_CLEAR = 'clear'

def console_window(queue, width, height, title, font_size):
    root = tk.Tk()
    root.title(title)
    root.geometry(f"{width}x{height}")
    root.resizable(False, False)

    text_widget = tk.Text(root, font=("Courier", font_size), state="disabled", wrap="word")
    text_widget.pack(fill="both", expand=True)

    message_stack = []

    def refresh():
        """Обновляет содержимое текстового поля на основе message_stack."""
        text_widget.config(state="normal")
        text_widget.delete("1.0", tk.END)
        for line in message_stack:
            text_widget.insert(tk.END, line + "\n")
        text_widget.config(state="disabled")

    def handle_queue():
        try:
            while True:
                cmd, data = queue.get_nowait()
                if cmd == CMD_ADD:
                    message_stack.append(data)
                elif cmd == CMD_REMOVE and isinstance(data, int):
                    if 0 <= data < len(message_stack):
                        del message_stack[data]
                elif cmd == CMD_CLEAR:
                    message_stack.clear()
        except pyqueue.Empty:
            pass
        refresh()
        root.after(100, handle_queue)

    root.after(100, handle_queue)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()

class Console:
    """
    Класс консоли с отдельным окном.

    Аргументы конструктора:
      width (int): ширина окна.
      height (int): высота окна.
      title (str): заголовок окна.
      font_size (int): размер шрифта (по умолчанию 24).

    Методы:
      print_(*args, **kwargs) – вывод сообщения в консоль.
      remov_(index) – удаляет сообщение по индексу.
      remarr() – очищает весь стек сообщений.
      remcon() – закрывает окно консоли.
    """
    def __init__(self, width=100, height=400, title='console', font_size=24):
        self.width = width
        self.height = height
        self.title = title
        self.font_size = font_size

        self.queue = multiprocessing.Queue()

        self.process = multiprocessing.Process(
            target=console_window,
            args=(self.queue, self.width, self.height, self.title, self.font_size)
        )
        self.process.start()

    def print_(self, *args, **kwargs):
        """Выводит сообщение в консоль, аналогично стандартной функции print()."""
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        text = sep.join(str(arg) for arg in args) + end
        self.queue.put((CMD_ADD, text.strip()))

    def remov_(self, index):
        """Удаляет сообщение с указанным индексом (начиная с 0)."""
        self.queue.put((CMD_REMOVE, index))

    def remarr(self):
        """Очищает весь стек сообщений консоли."""
        self.queue.put((CMD_CLEAR, None))

    def remcon(self):
        """Закрывает окно консоли, завершая процесс."""
        if self.process.is_alive():
            self.process.terminate()
            self.process.join()

    def join(self):
        """Ожидает завершения работы процесса консоли (если нужно)."""
        self.process.join()