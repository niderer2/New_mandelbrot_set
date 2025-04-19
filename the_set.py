from tqdm import tqdm
from interpretation_code import compiledExpression, functions
import numpy as np
import matplotlib.pyplot as plt
import os
from numba import njit
import gc


@njit
def rgb_to_hsv(rgb):
    """
    Преобразует цвет из RGB (0-255) в HSV (h в градусах, s и v от 0 до 1).
    """
    r = rgb[0] / 255.0
    g = rgb[1] / 255.0
    b = rgb[2] / 255.0

    cmax = r
    if g > cmax:
        cmax = g
    if b > cmax:
        cmax = b

    cmin = r
    if g < cmin:
        cmin = g
    if b < cmin:
        cmin = b

    delta = cmax - cmin

    if delta == 0:
        h = 0.0
    elif cmax == r:
        # Чтобы избежать отрицательного значения используем остаток от деления
        h = 60.0 * (((g - b) / delta) % 6)
    elif cmax == g:
        h = 60.0 * (((b - r) / delta) + 2)
    else:  # cmax == b
        h = 60.0 * (((r - g) / delta) + 4)

    s = 0.0 if cmax == 0 else delta / cmax
    v = cmax
    return h, s, v

@njit
def hsv_to_rgb(h, s, v):
    """
    Преобразует цвет из HSV (h в градусах, s и v от 0 до 1) в RGB (0-255).
    """
    C = v * s
    X = C * (1 - abs((h / 60.0) % 2 - 1))
    m = v - C

    if h < 60:
        r1, g1, b1 = C, X, 0.0
    elif h < 120:
        r1, g1, b1 = X, C, 0.0
    elif h < 180:
        r1, g1, b1 = 0.0, C, X
    elif h < 240:
        r1, g1, b1 = 0.0, X, C
    elif h < 300:
        r1, g1, b1 = X, 0.0, C
    else:
        r1, g1, b1 = C, 0.0, X

    r = int(round((r1 + m) * 255))
    g = int(round((g1 + m) * 255))
    b = int(round((b1 + m) * 255))

    if r < 0:
        r = 0
    if r > 255:
        r = 255
    if g < 0:
        g = 0
    if g > 255:
        g = 255
    if b < 0:
        b = 0
    if b > 255:
        b = 255

    return r, g, b

@njit
def create_gradient(color1, color2, m, if_color):
    """
    Создает градиент из m точек между color1 и color2 с выбором пути интерполяции
    по цветовому кругу.
    
    Параметры:
      color1, color2: входные цвета в формате [R, G, B] (0–255)
      m: число точек градиента
      if_color: строка, принимающая "short" для кратчайшего пути или "long" для длинного.
      
    Возвращает:
      Массив градиента размера (m, 3) с цветами типа uint8.
    """
    # Преобразование исходных цветов в HSV (h в градусах)
    h1, s1, v1 = rgb_to_hsv(color1)
    h2, s2, v2 = rgb_to_hsv(color2)

    gradient = np.zeros((m, 3), dtype=np.uint8)
    
    # Если выбран длинный путь, корректируем h2
    if if_color == "long":
        delta = (h2 - h1) % 360.0
        if delta <= 180.0:
            h2_adjusted = h2 - 360.0
        else:
            h2_adjusted = h2
        for i in range(m):
            t = i / (m - 1)
            h = h1 + (h2_adjusted - h1) * t
            h = h % 360.0  # нормализация в диапазоне [0, 360)
            s = s1 + (s2 - s1) * t
            v = v1 + (v2 - v1) * t
            r, g, b = hsv_to_rgb(h, s, v)
            gradient[i, 0] = r
            gradient[i, 1] = g
            gradient[i, 2] = b
    else:  # "short" или любое иное значение – используем кратчайший путь
        diff = h2 - h1
        # Корректируем разницу для кратчайшего пути
        if diff > 180.0:
            diff -= 360.0
        elif diff < -180.0:
            diff += 360.0
        for i in range(m):
            t = i / (m - 1)
            h = h1 + diff * t
            h = h % 360.0
            s = s1 + (s2 - s1) * t
            v = v1 + (v2 - v1) * t
            r, g, b = hsv_to_rgb(h, s, v)
            gradient[i, 0] = r
            gradient[i, 1] = g
            gradient[i, 2] = b

    return gradient


def render(name, min_x, max_x, min_y, max_y, min_h, max_h, min_z, max_z, min_t, max_t, min_u, max_u, min_v, max_v, min_w, max_w, z_funct, max_iterations, escape_radius, color1, color2, color3, scale_type, log_type, if_while, len_colors):
    # Обрабатываем текст в функцию
    z_function = compiledExpression(z_funct, functions)
    
    # Начальные параметры
    total_x, total_y = 100, 100  # Общий размер итогового изображения
    chunk_size = 50             # Размер сектора: 100x100
    len_gradient = 100
    k1, k10 = 1, 10 #коофиценты генерации если ранж равен и не равен друг другу
    range_h = k1 if min_h == max_h else k10
    range_z = k1 if min_z == max_z else k10
    range_t = k1 if min_t == max_t else k10
    range_u = k1 if min_u == max_u else k10
    range_v = k1 if min_v == max_v else k10
    range_w = k1 if min_w == max_w else k10

    # Создаём оси
    x_all = np.linspace(min_x, max_x, total_x)
    y_all = np.linspace(min_y, max_y, total_y)
    h_vals = np.linspace(min_h, max_h, range_h)
    z_vals = np.linspace(min_z, max_z, range_z)
    t_vals = np.linspace(min_t, max_t, range_t)
    u_vals = np.linspace(min_u, max_u, range_u)
    v_vals = np.linspace(min_v, max_v, range_v)
    w_vals = np.linspace(min_w, max_w, range_w)
    
    # Градиент
    gradient = create_gradient(color1, color2, len_gradient, len_colors)
    
    # Создаём главную папку для сохранения
    main_folder = f'{name}'
    os.makedirs(main_folder, exist_ok=True)
    
    # Итерируем по всем осям, создавая вложенные папки
    for wi in w_vals:
        folder_w = os.path.join(main_folder, f"{name}_w={wi:.3f}")
        os.makedirs(folder_w, exist_ok=True)
        
        for vi in v_vals:
            folder_v = os.path.join(folder_w, f"{name}_v={vi:.3f}")
            os.makedirs(folder_v, exist_ok=True)
            
            for ui in u_vals:
                folder_u = os.path.join(folder_v, f"{name}_u={ui:.3f}")
                os.makedirs(folder_u, exist_ok=True)
                
                for ti in t_vals:
                    folder_t = os.path.join(folder_u, f"{name}_t={ti:.3f}")
                    os.makedirs(folder_t, exist_ok=True)
                    
                    for zi in z_vals:
                        folder_z = os.path.join(folder_t, f"{name}_z={zi:.3f}")
                        os.makedirs(folder_z, exist_ok=True)
                        
                        for hi in h_vals:
                            # Создаём пустое итоговое изображение для сборки блоков
                            full_image = np.zeros((total_y, total_x, 3), dtype=np.uint8)
                            
                            # Создаём окно для визуализации в реальном времени
                            fig, ax = plt.subplots(figsize=(10, 10))
                            plt.ion()  # Режим интерактивного отображения
                            im_plot = ax.imshow(full_image, origin='upper')
                            
                            # Добавляем текстовое поле для отображения прогресса
                            progress_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='white', fontsize=12,
                                                      bbox=dict(facecolor='black', alpha=0.5))
                            
                            ax.set_title(f"Срез h = {hi:.3f}")
                            plt.show()
                            
                            # Перебор по блокам (секции) по оси y
                            for y_start in range(0, total_y, chunk_size):
                                y_end = min(y_start + chunk_size, total_y)
                                y_chunk = y_all[y_start:y_end]
                                
                                # Перебор по блокам (секции) по оси x
                                for x_start in range(0, total_x, chunk_size):
                                    x_end = min(x_start + chunk_size, total_x)
                                    x_chunk = x_all[x_start:x_end]
                                    
                                    # Массив для хранения текущего блока
                                    block_height = len(y_chunk)
                                    block_width = len(x_chunk)
                                    block_image = np.zeros((block_height, block_width, 3), dtype=np.uint8)
                                    
                                    # Обработка каждого ряда в блоке
                                    for yi_idx, yi in enumerate(tqdm(y_chunk, desc=f"h={hi:.3f}, сектор y[{y_start}:{y_end}]")):
                                        # Вычисляем цвета для текущей строки сектора
                                        colors = z_function(wi, vi, ui, ti, zi, hi, yi, np.array(x_chunk),
                                                              max_iterations, escape_radius,
                                                              np.array(gradient), color3, scale_type, log_type, if_while, len_colors)
                                        block_image[yi_idx, :, :] = colors
                                        
                                        # Обновляем информационный текст: текущий сектор и процент выполнения строки в секторе
                                        percentage = (yi_idx + 1) / block_height * 100
                                        progress_text.set_text(f"Сектор (x: {x_start}-{x_end}, y: {y_start}-{y_end})\nСтрока {yi_idx+1}/{block_height} ({percentage:.1f}%)")
                                        
                                        # Обновляем визуализацию
                                        full_image[y_start + yi_idx, x_start:x_end, :] = colors
                                        im_plot.set_data(full_image)
                                        fig.canvas.draw_idle()
                                        plt.pause(0.001)
                                        gc.collect()
                                    
                                    # После завершения сектора, вставляем готовый блок в итоговое изображение
                                    full_image[y_start:y_end, x_start:x_end, :] = block_image
                                    
                                    # Обновляем изображение, чтобы отобразить вставку блока
                                    im_plot.set_data(full_image)
                                    fig.canvas.draw_idle()
                                    plt.pause(0.001)
                            
                            # Сохранение итогового изображения для текущего среза hi
                            filename = os.path.join(folder_z, f"{name}_h={hi:.3f}_image.png")
                            plt.imsave(filename, full_image)
                            print(f"Сохранено изображение: {filename}")
                            
                            # Закрываем окно визуализации для текущего среза
                            plt.ioff()
                            plt.close(fig)