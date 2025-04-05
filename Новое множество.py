import tkinter as tk
from tkinter import ttk, colorchooser, messagebox

def choose_color(entry):
    """Открывает окно выбора цвета для поля."""
    color = colorchooser.askcolor()[1]
    if color:
        entry.delete(0, tk.END)
        entry.insert(0, color)

def toggle_log_scale_option():
    """Показывает или скрывает дополнительные параметры логарифмического выбора в зависимости от выбранного типа масштаба."""
    if scale_var.get() == "logarithmic":
        log_option_frame.grid(row=11, column=0, columnspan=4, pady=10)
    else:
        log_option_frame.grid_forget()

def submit():
    """Обрабатывает значения из полей и проверяет их на корректность."""
    try:
        # Получаем значения из полей
        name = name_entry.get().strip()
        if not name:
            raise ValueError("Название не может быть пустым.")
        
        min_x = int(min_x_entry.get())
        max_x = int(max_x_entry.get())
        min_y = int(min_y_entry.get())
        max_y = int(max_y_entry.get())
        min_h = int(min_h_entry.get())
        max_h = int(max_h_entry.get())
        
        if min_x <= 0 or max_x <= 0 or min_y <= 0 or max_y <= 0 or min_h <= 0 or max_h <= 0:
            raise ValueError("Все значения должны быть положительными.")

        use_complex_x = bool(x_complex_var.get())
        use_complex_y = bool(y_complex_var.get())
        use_complex_z = bool(z_complex_var.get())
        
        z_function = z_func_entry.get("1.0", tk.END).strip()
        
        max_iterations = int(max_iter_entry.get())
        escape_radius = float(escape_radius_entry.get())
        
        color1 = color1_entry.get()
        color2 = color2_entry.get()
        color3 = color3_entry.get()

        # Получаем выбранный тип масштаба цветов
        scale_type = scale_var.get()

        # Если выбрано логарифмическое распределение, получаем дополнительный параметр
        if scale_type == "logarithmic":
            log_type = log_scale_var.get()
        else:
            log_type = None

        # Проверка, нужно ли создавать GIF
        create_gif = bool(create_gif_var.get())

        # Выводим полученные значения (или здесь можно добавить логику обработки)
        print(f"Название: {name}")
        print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}, min_h: {min_h}, max_h: {max_h}")
        print(f"Complex x: {use_complex_x}, y: {use_complex_y}, z: {use_complex_z}")
        print(f"Функция z = {z_function}")
        print(f"Макс. итераций: {max_iterations}, Радиус выхода: {escape_radius}")
        print(f"Цвета: {color1}, {color2}, {color3}")
        print(f"Тип масштаба цветов: {scale_type}")
        if scale_type == "logarithmic":
            print(f"Тип логарифмического масштаба: {log_type}")
        print(f"Создать GIF: {'Да' if create_gif else 'Нет'}")

    except ValueError as e:
        messagebox.showerror("Ошибка", str(e))

# Создание окна
root = tk.Tk()
root.title("Настройки множества")

frame = ttk.Frame(root, padding=10)
frame.grid()

# Название (выравнивание по правому краю)
ttk.Label(frame, text="Название").grid(row=0, column=0)
name_entry = ttk.Entry(frame)
name_entry.grid(row=0, column=1, columnspan=3, sticky="e")

# Координаты
ttk.Label(frame, text="min X").grid(row=1, column=0)
min_x_entry = ttk.Entry(frame)
min_x_entry.grid(row=1, column=1)

ttk.Label(frame, text="max X").grid(row=1, column=2)
max_x_entry = ttk.Entry(frame)
max_x_entry.grid(row=1, column=3)

ttk.Label(frame, text="min Y").grid(row=2, column=0)
min_y_entry = ttk.Entry(frame)
min_y_entry.grid(row=2, column=1)

ttk.Label(frame, text="max Y").grid(row=2, column=2)
max_y_entry = ttk.Entry(frame)
max_y_entry.grid(row=2, column=3)

ttk.Label(frame, text="min H").grid(row=3, column=0)
min_h_entry = ttk.Entry(frame)
min_h_entry.grid(row=3, column=1)

ttk.Label(frame, text="max H").grid(row=3, column=2)
max_h_entry = ttk.Entry(frame)
max_h_entry.grid(row=3, column=3)

# Чекбоксы для комплексности
x_complex_var = tk.IntVar()
y_complex_var = tk.IntVar()
z_complex_var = tk.IntVar()

ttk.Checkbutton(frame, text="X комплексный", variable=x_complex_var).grid(row=4, column=0)
ttk.Checkbutton(frame, text="Y комплексный", variable=y_complex_var).grid(row=4, column=1)
ttk.Checkbutton(frame, text="Z комплексный", variable=z_complex_var).grid(row=4, column=2)

# Функция Z
ttk.Label(frame, text="Функция Z =").grid(row=5, column=0, sticky="nw")
z_func_entry = tk.Text(frame, width=40, height=4)
z_func_entry.grid(row=5, column=1, columnspan=3, sticky="w")

# Итерации и выход
ttk.Label(frame, text="Макс. итераций").grid(row=6, column=0)
max_iter_entry = ttk.Entry(frame)
max_iter_entry.grid(row=6, column=1)

ttk.Label(frame, text="Радиус выхода").grid(row=6, column=2)
escape_radius_entry = ttk.Entry(frame)
escape_radius_entry.grid(row=6, column=3)

# Цвета
color1_entry = ttk.Entry(frame)
color1_entry.grid(row=7, column=1)
ttk.Button(frame, text="Цвет 1", command=lambda: choose_color(color1_entry)).grid(row=7, column=0)

color2_entry = ttk.Entry(frame)
color2_entry.grid(row=7, column=3)
ttk.Button(frame, text="Цвет 2", command=lambda: choose_color(color2_entry)).grid(row=7, column=2)

color3_entry = ttk.Entry(frame)
color3_entry.grid(row=8, column=1)
ttk.Button(frame, text="Цвет 3", command=lambda: choose_color(color3_entry)).grid(row=8, column=0)

# Выбор типа масштаба для цветов (линейно / логарифмически)
ttk.Label(frame, text="Выбор масштаба цветов:").grid(row=9, column=0, columnspan=4)

scale_var = tk.StringVar(value="linear")  # по умолчанию линейно
ttk.Radiobutton(frame, text="Линейно", variable=scale_var, value="linear", command=toggle_log_scale_option).grid(row=10, column=0)
ttk.Radiobutton(frame, text="Логарифмически", variable=scale_var, value="logarithmic", command=toggle_log_scale_option).grid(row=10, column=1)

# Опции для логарифмического масштаба (с промежутком между "красиво" и "правильно")
log_option_frame = ttk.Frame(frame)
log_scale_var = tk.StringVar(value="beautiful")
ttk.Radiobutton(log_option_frame, text="Красиво", variable=log_scale_var, value="beautiful").grid(row=0, column=0)  # добавлен промежуток
ttk.Radiobutton(log_option_frame, text="Правильно", variable=log_scale_var, value="correct").grid(row=0, column=1)

# Выбор, создавать ли GIF
create_gif_var = tk.IntVar()
ttk.Checkbutton(frame, text="Создать GIF", variable=create_gif_var).grid(row=12, column=0, columnspan=4)

# Кнопка отправки
ttk.Button(frame, text="Применить", command=submit).grid(row=13, column=0, columnspan=4, pady=10)

root.mainloop()
