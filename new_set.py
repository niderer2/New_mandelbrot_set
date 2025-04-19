import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from func_defef import hex_to_rgb
import time
import multiprocessing
import the_set   


if __name__ == '__main__':
    
    def choose_color(entry):
        """Открывает окно выбора цвета для поля."""
        color = colorchooser.askcolor()[1]
        if color:
            entry.delete(0, tk.END)
            entry.insert(0, color)
    
    def toggle_log_scale_option():
        """Показывает или скрывает дополнительные параметры логарифмического выбора в зависимости от выбранного типа масштаба."""
        if scale_var.get() == "logarithmic":
            log_option_frame.grid(row=16, column=0, columnspan=4, pady=10)
        else:
            log_option_frame.grid_forget()
    
    def submit():
        """Обрабатывает значения из полей и проверяет их на корректность."""
        try:
            # Получение значений
            name = name_entry.get().strip()
            if not name:
                raise ValueError("Название не может быть пустым.")
            
            # Координаты для x, y, h
            min_x = float(min_x_entry.get())
            max_x = float(max_x_entry.get())
            min_y = float(min_y_entry.get())
            max_y = float(max_y_entry.get())
            min_h = float(min_h_entry.get())
            max_h = float(max_h_entry.get())
            
            # Дополнительные переменные (по умолчанию от 0 до 0)
            min_z = float(min_z_entry.get())
            max_z = float(max_z_entry.get())
            min_t = float(min_t_entry.get())
            max_t = float(max_t_entry.get())
            min_u = float(min_u_entry.get())
            max_u = float(max_u_entry.get())
            min_v = float(min_v_entry.get())
            max_v = float(max_v_entry.get())
            min_w = float(min_w_entry.get())
            max_w = float(max_w_entry.get())
            
            z_function = z_func_entry.get("1.0", tk.END).strip()
            
            max_iterations = int(max_iter_entry.get())
            escape_radius = float(escape_radius_entry.get())
            
            color1 = color1_entry.get()
            color2 = color2_entry.get()
            color3 = color3_entry.get()
    
            # Получаем выбранный тип масштаба цветов и дополнительные опции
            scale_type = scale_var.get()
            if_while = scale_var_w.get()
            len_colors_val = len_colors.get()
    
            if scale_type == "logarithmic":
                log_type = log_scale_var.get()
            else:
                log_type = None
            
            # Вызов функции render с новыми параметрами
            the_set.render(name, min_x, max_x, min_y, max_y, min_h, max_h,
                           min_z, max_z, min_t, max_t, min_u, max_u, min_v, max_v, min_w, max_w,
                           z_function, max_iterations, escape_radius,
                           hex_to_rgb(color1), hex_to_rgb(color2), hex_to_rgb(color3),
                           scale_type, log_type, if_while, len_colors_val)
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    # Создание основного окна
    root = tk.Tk()
    root.title("Настройки множества")
    
    frame = ttk.Frame(root, padding=10)
    frame.grid()
    
    # Название
    name_var = tk.StringVar(value="name")
    ttk.Label(frame, text="Название").grid(row=0, column=0)
    name_entry = ttk.Entry(frame, textvariable=name_var)
    name_entry.grid(row=0, column=1, columnspan=3, sticky="e")
    
    # Координаты X (дефолт от -2 до 2)
    ttk.Label(frame, text="min X").grid(row=1, column=0)
    min_x_var = tk.StringVar(value='-2.0')
    min_x_entry = ttk.Entry(frame, textvariable=min_x_var)
    min_x_entry.grid(row=1, column=1)
    
    ttk.Label(frame, text="max X").grid(row=1, column=2)
    max_x_var = tk.StringVar(value='2.0')
    max_x_entry = ttk.Entry(frame, textvariable=max_x_var)
    max_x_entry.grid(row=1, column=3)
    
    # Координаты Y (дефолт от -2 до 2)
    ttk.Label(frame, text="min Y").grid(row=2, column=0)
    min_y_var = tk.StringVar(value='-2.0')
    min_y_entry = ttk.Entry(frame, textvariable=min_y_var)
    min_y_entry.grid(row=2, column=1)
    
    ttk.Label(frame, text="max Y").grid(row=2, column=2)
    max_y_var = tk.StringVar(value='2.0')
    max_y_entry = ttk.Entry(frame, textvariable=max_y_var)
    max_y_entry.grid(row=2, column=3)
    
    # Координаты H (дефолт от -2 до 2)
    ttk.Label(frame, text="min H").grid(row=3, column=0)
    min_h_var = tk.StringVar(value='-2.0')
    min_h_entry = ttk.Entry(frame, textvariable=min_h_var)
    min_h_entry.grid(row=3, column=1)
    
    ttk.Label(frame, text="max H").grid(row=3, column=2)
    max_h_var = tk.StringVar(value='2.0')
    max_h_entry = ttk.Entry(frame, textvariable=max_h_var)
    max_h_entry.grid(row=3, column=3)
    
    # Дополнительные переменные (дефолт от 0 до 0)
    # Переменная Z
    ttk.Label(frame, text="min Z").grid(row=4, column=0)
    min_z_var = tk.StringVar(value='0.0')
    min_z_entry = ttk.Entry(frame, textvariable=min_z_var)
    min_z_entry.grid(row=4, column=1)
    
    ttk.Label(frame, text="max Z").grid(row=4, column=2)
    max_z_var = tk.StringVar(value='0.0')
    max_z_entry = ttk.Entry(frame, textvariable=max_z_var)
    max_z_entry.grid(row=4, column=3)
    
    # Переменная T
    ttk.Label(frame, text="min T").grid(row=5, column=0)
    min_t_var = tk.StringVar(value='0.0')
    min_t_entry = ttk.Entry(frame, textvariable=min_t_var)
    min_t_entry.grid(row=5, column=1)
    
    ttk.Label(frame, text="max T").grid(row=5, column=2)
    max_t_var = tk.StringVar(value='0.0')
    max_t_entry = ttk.Entry(frame, textvariable=max_t_var)
    max_t_entry.grid(row=5, column=3)
    
    # Переменная U
    ttk.Label(frame, text="min U").grid(row=6, column=0)
    min_u_var = tk.StringVar(value='0.0')
    min_u_entry = ttk.Entry(frame, textvariable=min_u_var)
    min_u_entry.grid(row=6, column=1)
    
    ttk.Label(frame, text="max U").grid(row=6, column=2)
    max_u_var = tk.StringVar(value='0.0')
    max_u_entry = ttk.Entry(frame, textvariable=max_u_var)
    max_u_entry.grid(row=6, column=3)
    
    # Переменная V
    ttk.Label(frame, text="min V").grid(row=7, column=0)
    min_v_var = tk.StringVar(value='0.0')
    min_v_entry = ttk.Entry(frame, textvariable=min_v_var)
    min_v_entry.grid(row=7, column=1)
    
    ttk.Label(frame, text="max V").grid(row=7, column=2)
    max_v_var = tk.StringVar(value='0.0')
    max_v_entry = ttk.Entry(frame, textvariable=max_v_var)
    max_v_entry.grid(row=7, column=3)
    
    # Переменная W
    ttk.Label(frame, text="min W").grid(row=8, column=0)
    min_w_var = tk.StringVar(value='0.0')
    min_w_entry = ttk.Entry(frame, textvariable=min_w_var)
    min_w_entry.grid(row=8, column=1)
    
    ttk.Label(frame, text="max W").grid(row=8, column=2)
    max_w_var = tk.StringVar(value='0.0')
    max_w_entry = ttk.Entry(frame, textvariable=max_w_var)
    max_w_entry.grid(row=8, column=3)
    
    # Функция Z
    ttk.Label(frame, text="Функция Z =").grid(row=10, column=0, sticky="nw")
    z_func_entry = tk.Text(frame, width=40, height=4)
    z_func_entry.grid(row=10, column=1, columnspan=3, sticky="w")
    z_func_entry.insert("1.0", "pow(z, oct(2)) + c")
    
    # Итерации и радиус выхода
    ttk.Label(frame, text="Макс. итераций").grid(row=11, column=0)
    max_iter_var = tk.StringVar(value='1000')
    max_iter_entry = ttk.Entry(frame, textvariable=max_iter_var)
    max_iter_entry.grid(row=11, column=1)
    
    ttk.Label(frame, text="Радиус выхода").grid(row=11, column=2)
    escape_radius_var = tk.StringVar(value='2.0')
    escape_radius_entry = ttk.Entry(frame, textvariable=escape_radius_var)
    escape_radius_entry.grid(row=11, column=3)
    
    # Цвета
    # Цвет убегания
    color1_var = tk.StringVar(value='#000b6c')
    color1_entry = ttk.Entry(frame, textvariable=color1_var)
    color1_entry.grid(row=12, column=1)
    ttk.Button(frame, text="Цвет убегания", command=lambda: choose_color(color1_entry)).grid(row=12, column=0)
    
    # Цвет близости
    color2_var = tk.StringVar(value='#dd0000')
    color2_entry = ttk.Entry(frame, textvariable=color2_var)
    color2_entry.grid(row=12, column=3)
    ttk.Button(frame, text="Цвет близости", command=lambda: choose_color(color2_entry)).grid(row=12, column=2)
    
    # Цвет множества
    color3_var = tk.StringVar(value='#000000')
    color3_entry = ttk.Entry(frame, textvariable=color3_var)
    color3_entry.grid(row=13, column=1)
    ttk.Button(frame, text="Цвет множества", command=lambda: choose_color(color3_entry)).grid(row=13, column=0)
    
    # Выбор типа масштаба цветов
    ttk.Label(frame, text="Выбор масштаба цветов:").grid(row=14, column=0, columnspan=4)
    
    scale_var = tk.StringVar(value="linear")  # линейно по умолчанию
    ttk.Radiobutton(frame, text="Линейно", variable=scale_var, value="linear", command=toggle_log_scale_option).grid(row=15, column=0)
    ttk.Radiobutton(frame, text="Логарифмически", variable=scale_var, value="logarithmic", command=toggle_log_scale_option).grid(row=15, column=1)
    
    # Опции для логарифмического масштаба
    log_option_frame = ttk.Frame(frame)
    log_scale_var = tk.StringVar(value="beautiful")
    ttk.Radiobutton(log_option_frame, text="Красиво", variable=log_scale_var, value="beautiful").grid(row=0, column=0)
    ttk.Radiobutton(log_option_frame, text="Правильно", variable=log_scale_var, value="correct").grid(row=0, column=1)
    
    # Выбор типа цикла для масштаба цветов
    scale_var_w = tk.StringVar(value="while")  # по умолчанию циклично
    ttk.Radiobutton(frame, text="Циклично", variable=scale_var_w, value="while").grid(row=17, column=0)
    ttk.Radiobutton(frame, text="Линейно", variable=scale_var_w, value="liner").grid(row=17, column=1)
    
    # Выбор длины градиента
    len_colors = tk.StringVar(value="short")  # по умолчанию коротко
    ttk.Radiobutton(frame, text="Короткий градиент", variable=len_colors, value="short").grid(row=18, column=0)
    ttk.Radiobutton(frame, text="Растянутый градиент", variable=len_colors, value="long").grid(row=18, column=1)

    
    # Кнопка отправки
    ttk.Button(frame, text="Применить", command=submit).grid(row=20, column=0, columnspan=4, pady=10)
    
    root.mainloop()