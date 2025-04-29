import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import time
import json
import os
import multiprocessing
import the_set
from func_defef import hex_to_rgb

if __name__ == '__main__':

    def choose_color(entry):
        color = colorchooser.askcolor()[1]
        if color:
            entry.delete(0, tk.END)
            entry.insert(0, color)

    def toggle_log_scale_option():
        if scale_var.get() == "logarithmic":
            log_option_frame.grid()
        else:
            log_option_frame.grid_forget()

    def submit():
        try:
            if not agreement_var.get():
                raise ValueError("Вы должны согласиться с условиями пользования.")

            name = name_entry.get().strip()
            if not name:
                raise ValueError("Название не может быть пустым.")
            # Вызов рендера
            d = [name_entry.get(), #имя
                int(image_width_entry.get()), int(image_height_entry.get()), # ширена и высота
                #параметры осей
                float(min_x_entry.get()), float(max_x_entry.get()),
                float(min_y_entry.get()), float(max_y_entry.get()),
                float(min_h_entry.get()), float(max_h_entry.get()),
                float(min_z_entry.get()), float(max_z_entry.get()),
                float(min_t_entry.get()), float(max_t_entry.get()),
                float(min_u_entry.get()), float(max_u_entry.get()),
                float(min_v_entry.get()), float(max_v_entry.get()),
                float(min_w_entry.get()), float(max_w_entry.get()), 
                
                #функции
                z_func_entry.get("1.0", "end")[:-1],
                custom_func_entry.get("1.0", "end")[:-1],
                escape_condition_entry.get("1.0", "end")[:-1],
                
                funct_once.get("1.0", "end")[:-1], #фукция выполняемая единожды
                int(max_iter_entry.get()), #макс итерации
                hex_to_rgb(color1_entry.get()), hex_to_rgb(color2_entry.get()), hex_to_rgb(color3_entry.get()), hex_to_rgb(color4_entry.get()), #цвета
                scale_var.get(), #градиет линейно или логарифмически
                log_scale_var.get(), #красивый или правильный
                scale_var_w.get(), #цикличный или ровный градиент
                len_colors.get(), #длинна градиента котороткий или длинный
                ]
            print(d)
            the_set.render(*d)

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    root = tk.Tk()
    root.title("Настройки множества")
    root.geometry("500x500")  # уже более компактно по вертикали

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Скроллинг
    canvas = tk.Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    main_frame = ttk.Frame(scrollable_frame, padding=10)
    main_frame.grid(sticky="nsew")

    # Основные настройки
    ttk.Label(main_frame, text="Основные настройки", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=4, sticky="w")
    ttk.Label(main_frame, text="Название:").grid(row=1, column=0, sticky="w")
    name_entry = ttk.Entry(main_frame)
    name_entry.grid(row=1, column=1, columnspan=3, sticky="ew")
    name_entry.insert(0, "name")

    ttk.Label(main_frame, text="Ширина изображения:").grid(row=2, column=0, sticky="w")
    image_width_entry = ttk.Entry(main_frame)
    image_width_entry.grid(row=2, column=1, sticky="ew")
    image_width_entry.insert(0, "300")
    ttk.Label(main_frame, text="Высота изображения:").grid(row=2, column=2, sticky="w")
    image_height_entry = ttk.Entry(main_frame)
    image_height_entry.grid(row=2, column=3, sticky="ew")
    image_height_entry.insert(0, "300")

    # Координаты и переменные
    ttk.Label(main_frame, text="Координаты и переменные", font=("Arial", 14, "bold")).grid(row=3, column=0, columnspan=4, pady=(10,5), sticky="w")
    # X
    ttk.Label(main_frame, text="min X").grid(row=4, column=0, sticky="w")
    min_x_entry = ttk.Entry(main_frame)
    min_x_entry.grid(row=4, column=1, sticky="ew"); min_x_entry.insert(0, "-2.0")
    ttk.Label(main_frame, text="max X").grid(row=4, column=2, sticky="w")
    max_x_entry = ttk.Entry(main_frame)
    max_x_entry.grid(row=4, column=3, sticky="ew"); max_x_entry.insert(0, "2.0")
    # Y
    ttk.Label(main_frame, text="min Y").grid(row=5, column=0, sticky="w")
    min_y_entry = ttk.Entry(main_frame)
    min_y_entry.grid(row=5, column=1, sticky="ew"); min_y_entry.insert(0, "-2.0")
    ttk.Label(main_frame, text="max Y").grid(row=5, column=2, sticky="w")
    max_y_entry = ttk.Entry(main_frame)
    max_y_entry.grid(row=5, column=3, sticky="ew"); max_y_entry.insert(0, "2.0")
    # H
    ttk.Label(main_frame, text="min H").grid(row=6, column=0, sticky="w")
    min_h_entry = ttk.Entry(main_frame)
    min_h_entry.grid(row=6, column=1, sticky="ew"); min_h_entry.insert(0, "0.0")
    ttk.Label(main_frame, text="max H").grid(row=6, column=2, sticky="w")
    max_h_entry = ttk.Entry(main_frame)
    max_h_entry.grid(row=6, column=3, sticky="ew"); max_h_entry.insert(0, "0.0")
    # Z
    ttk.Label(main_frame, text="min Z").grid(row=7, column=0, sticky="w")
    min_z_entry = ttk.Entry(main_frame) 
    min_z_entry.grid(row=7, column=1, sticky="ew"); min_z_entry.insert(0, "0.0")
    ttk.Label(main_frame, text="max Z").grid(row=7, column=2, sticky="w")
    max_z_entry = ttk.Entry(main_frame) 
    max_z_entry.grid(row=7, column=3, sticky="ew"); max_z_entry.insert(0, "0.0")
    # T
    ttk.Label(main_frame, text="min T").grid(row=8, column=0, sticky="w")
    min_t_entry = ttk.Entry(main_frame) 
    min_t_entry.grid(row=8, column=1, sticky="ew"); min_t_entry.insert(0, "0.0")
    ttk.Label(main_frame, text="max T").grid(row=8, column=2, sticky="w")
    max_t_entry = ttk.Entry(main_frame) 
    max_t_entry.grid(row=8, column=3, sticky="ew"); max_t_entry.insert(0, "0.0")
    # U
    ttk.Label(main_frame, text="min U").grid(row=9, column=0, sticky="w")
    min_u_entry = ttk.Entry(main_frame) 
    min_u_entry.grid(row=9, column=1, sticky="ew"); min_u_entry.insert(0, "0.0")
    ttk.Label(main_frame, text="max U").grid(row=9, column=2, sticky="w")
    max_u_entry = ttk.Entry(main_frame) 
    max_u_entry.grid(row=9, column=3, sticky="ew"); max_u_entry.insert(0, "0.0")
    # V
    ttk.Label(main_frame, text="min V").grid(row=10, column=0, sticky="w")
    min_v_entry = ttk.Entry(main_frame) 
    min_v_entry.grid(row=10, column=1, sticky="ew"); min_v_entry.insert(0, "0.0")
    ttk.Label(main_frame, text="max V").grid(row=10, column=2, sticky="w")
    max_v_entry = ttk.Entry(main_frame)
    max_v_entry.grid(row=10, column=3, sticky="ew"); max_v_entry.insert(0, "0.0")
    # W
    ttk.Label(main_frame, text="min W").grid(row=11, column=0, sticky="w")
    min_w_entry = ttk.Entry(main_frame)
    min_w_entry.grid(row=11, column=1, sticky="ew")
    min_w_entry.insert(0, "0.0")
    
    ttk.Label(main_frame, text="max W").grid(row=11, column=2, sticky="w")
    max_w_entry = ttk.Entry(main_frame)
    max_w_entry.grid(row=11, column=3, sticky="ew")
    max_w_entry.insert(0, "0.0")

    current_row = 12

    # Функции
    ttk.Label(main_frame, text="Функция Z =", font=("Arial", 14, "bold")).grid(row=current_row, column=0, sticky="w", pady=(10,5))
    current_row += 1
    z_func_entry = tk.Text(main_frame, width=60, height=5)
    z_func_entry.grid(row=current_row, column=0, columnspan=4, sticky="ew")
    z_func_entry.insert("1.0", "pow(z, oct(2)) + c")

    current_row += 1
    ttk.Label(main_frame, text="Кастомная функция:").grid(row=current_row, column=0, sticky="w")
    current_row += 1
    custom_func_entry = tk.Text(main_frame, width=60, height=3)
    custom_func_entry.grid(row=current_row, column=0, columnspan=4, sticky="ew")

    current_row += 1
    ttk.Label(main_frame, text="Условие выхода (if):").grid(row=current_row, column=0, sticky="w")
    current_row += 1
    escape_condition_entry = tk.Text(main_frame, width=60, height=2)
    escape_condition_entry.grid(row=current_row, column=0, columnspan=4, sticky="ew")
    escape_condition_entry.insert("1.0", "norm(z) > 2")

    current_row += 1
    ttk.Label(main_frame, text="Начальная функция:").grid(row=current_row, column=0, sticky="w")
    current_row += 1
    funct_once = tk.Text(main_frame, width=60, height=2)
    funct_once.grid(row=current_row, column=0, columnspan=4, sticky="ew")
    funct_once.insert("1.0", '''c = np.array([xi, yi, hi, zi, ti, ui, vi, wi])
z = np.array([xi, yi, hi, zi, ti, ui, vi, wi])''')

    current_row += 1
    ttk.Label(main_frame, text="Максимальное количество итераций:").grid(row=current_row, column=0, sticky="w")
    max_iter_entry = ttk.Entry(main_frame)
    max_iter_entry.grid(row=current_row, column=1, sticky="ew")
    max_iter_entry.insert(0, "1000")

    current_row += 1

    # Цвета
    ttk.Label(main_frame, text="Цвета", font=("Arial", 14, "bold")).grid(row=current_row, column=0, sticky="w", pady=(10,5))
    current_row += 1

    # Цвет убегания
    ttk.Button(main_frame, text="Цвет убегания", command=lambda: choose_color(color1_entry)) \
        .grid(row=current_row, column=0, sticky="w")
    color1_var = tk.StringVar(value='#000b6c')
    color1_entry = ttk.Entry(main_frame, textvariable=color1_var)
    color1_entry.grid(row=current_row, column=1, columnspan=3, sticky="ew")
    current_row += 1
    
    # Цвет близости
    ttk.Button(main_frame, text="Цвет близости", command=lambda: choose_color(color2_entry)) \
        .grid(row=current_row, column=0, sticky="w")
    color2_var = tk.StringVar(value='#dd0000')
    color2_entry = ttk.Entry(main_frame, textvariable=color2_var)
    color2_entry.grid(row=current_row, column=1, columnspan=3, sticky="ew")
    current_row += 1
    
    # Цвет множества
    ttk.Button(main_frame, text="Цвет множества", command=lambda: choose_color(color3_entry)) \
        .grid(row=current_row, column=0, sticky="w")
    color3_var = tk.StringVar(value='#000000')
    color3_entry = ttk.Entry(main_frame, textvariable=color3_var)
    color3_entry.grid(row=current_row, column=1, columnspan=3, sticky="ew")
    current_row += 1
    
    # Ерор-цвет
    ttk.Button(main_frame, text="Ерор-цвет", command=lambda: choose_color(color4_entry)) \
        .grid(row=current_row, column=0, sticky="w")
    color4_var = tk.StringVar(value='#ffffff')
    color4_entry = ttk.Entry(main_frame, textvariable=color4_var)
    color4_entry.grid(row=current_row, column=1, columnspan=3, sticky="ew")
    current_row += 1

    current_row += 10

    # Масштабирование цветов
    ttk.Label(main_frame, text="Масштабирование цветов", font=("Arial", 14, "bold")) \
        .grid(row=current_row, column=0, sticky="w", pady=(10,5))
    current_row += 1
    
    # Тип масштаба (линейно / логарифмически)
    scale_var = tk.StringVar(value="linear")
    ttk.Radiobutton(main_frame, text="Линейно", variable=scale_var, value="linear",
                    command=toggle_log_scale_option) \
        .grid(row=current_row, column=0, sticky="w")
    ttk.Radiobutton(main_frame, text="Логарифмически", variable=scale_var, value="logarithmic",
                    command=toggle_log_scale_option) \
        .grid(row=current_row, column=1, sticky="w")
    current_row += 2
    
    # Опции для логарифмического масштаба (появляются только при выборе «Логарифмически»)
    log_option_frame = ttk.Frame(main_frame)
    log_scale_var = tk.StringVar(value="beautiful")
    ttk.Radiobutton(log_option_frame, text="Красиво",   variable=log_scale_var, value="beautiful") \
        .grid(row=current_row, column=0, sticky="w")
    ttk.Radiobutton(log_option_frame, text="Правильно", variable=log_scale_var, value="correct") \
        .grid(row=current_row, column=1, sticky="w")
    current_row += 2   
    
    # Тип градиента (цикличный / линейный)
    scale_var_w = tk.StringVar(value="while")
    ttk.Radiobutton(main_frame, text="Цикличный градиент", variable=scale_var_w, value="while") \
        .grid(row=current_row, column=0, sticky="w")
    ttk.Radiobutton(main_frame, text="Линейный градиент", variable=scale_var_w, value="liner") \
        .grid(row=current_row, column=1, sticky="w")
    current_row += 1
    
    # Длина градиента (короткий / растянутый)
    len_colors = tk.StringVar(value="short")
    ttk.Radiobutton(main_frame, text="Короткий градиент", variable=len_colors, value="short") \
        .grid(row=current_row, column=0, sticky="w")
    ttk.Radiobutton(main_frame, text="Растянутый градиент", variable=len_colors, value="long") \
        .grid(row=current_row, column=1, sticky="w")
    current_row += 1
    
    def toggle_log_scale_option():
        if scale_var.get() == "logarithmic":
            log_option_frame.grid(row=current_row, column=0, columnspan=2, sticky="w", pady=(5,0))
        else:
            log_option_frame.grid_forget()


    current_row += 1

    # Чекбокс согласия
    agreement_var = tk.BooleanVar()
    agreement_check = ttk.Checkbutton(main_frame, text="Я ознакомился с условиями пользования и полностью согласен с ними", variable=agreement_var)
    agreement_check.grid(row=current_row, column=0, columnspan=4, pady=10)

    current_row += 1

    # Кнопка
    apply_btn = ttk.Button(main_frame, text="Применить", command=submit)
    apply_btn.grid(row=current_row, column=0, columnspan=4, pady=10)

    for i in range(4):
        main_frame.columnconfigure(i, weight=1)

    root.mainloop()
