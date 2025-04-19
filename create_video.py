import re
import cv2
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

# Поддерживаемые расширения изображений
SUPPORTED_EXTS = {'.png', '.jpg', '.jpeg'}
# Доступные кодеки для VideoWriter
AVAILABLE_CODECS = ['mp4v', 'H264', 'XVID']

MAX_MP4_SIZE = (4096, 4096)


def read_image(path: Path):
    try:
        img = Image.open(path)
        img = img.convert('RGB')
        arr = np.array(img)
        return arr[..., ::-1]  # RGB -> BGR
    except Exception as e:
        print(f"Ошибка чтения изображения {path}: {e}")
        return None


def parse_key_from_path(p: Path):
    pattern = re.compile(r'=(-?\d+(?:\.\d+)?)')
    nums = pattern.findall(str(p))
    if len(nums) >= 6:
        return tuple(float(x) for x in nums[:6])
    else:
        print(f"Ошибка в пути {p}: не найдено достаточно ключевых значений")
        return None


def collect_by_axes(files):
    data = {}
    for p in files:
        key = parse_key_from_path(p)
        if key:
            t, z, *rest = key  # первые две координаты
            data.setdefault(t, {}).setdefault(z, []).append(p)
    return data


def make_canvas_from_grid(grid, img_shape, img_size):
    h_img, w_img = img_size
    tile_h, tile_w = img_shape
    canvas = np.ones((tile_h * h_img, tile_w * w_img, 3), dtype=np.uint8) * 255

    for i, row in enumerate(grid):
        for j, img in enumerate(row):
            if img is not None:
                resized = cv2.resize(img, (w_img, h_img))
                canvas[i * h_img:(i + 1) * h_img, j * w_img:(j + 1) * w_img] = resized
            else:
                print(f"Пустое изображение в позиции ({i}, {j})")
    
    return canvas


def downscale_if_needed(canvas, codec):
    h, w = canvas.shape[:2]
    if codec == 'mp4v' and (w > MAX_MP4_SIZE[0] or h > MAX_MP4_SIZE[1]):
        scale_w = MAX_MP4_SIZE[0] / w
        scale_h = MAX_MP4_SIZE[1] / h
        scale = min(scale_w, scale_h)
        new_size = (int(w * scale), int(h * scale))
        print(f"[INFO] Холст превышает допустимый размер для mp4v. Масштабирование до {new_size}")
        return cv2.resize(canvas, new_size)
    print(f"[INFO] Размер канвы: {h}x{w}")
    return canvas


def collect_and_write_video(root_dir: str, output_path: str, fps: int, codec: str, use_canvas: bool):
    root = Path(root_dir)
    files = [p for p in root.rglob('*') if p.suffix.lower() in SUPPORTED_EXTS]
    if not files:
        raise RuntimeError(f"В папке {root_dir} не найдено файлов {SUPPORTED_EXTS}")

    first_img = read_image(files[0])
    if first_img is None:
        raise RuntimeError(f"Не удалось загрузить изображение: {files[0]}")
    h, w = first_img.shape[:2]

    if use_canvas:
        data = collect_by_axes(files)
        ts = sorted(data.keys())
        zs = sorted({z for zsets in data.values() for z in zsets})

        # Если для какого-то t нет z, добавляем пустые группы
        for t in ts:
            for z in zs:
                if z not in data[t]:
                    data[t][z] = []

        # Получаем количество групп изображений
        group_count = max(len(v) for t in data.values() for v in t.values())
        if group_count == 0:
            raise RuntimeError("Нет допустимых изображений для холста")

        canvas_size = (len(zs) * w, group_count * h)
        dummy_frame = np.ones((canvas_size[1], canvas_size[0], 3), dtype=np.uint8) * 255
        dummy_frame = downscale_if_needed(dummy_frame, codec)
        final_size = (dummy_frame.shape[1], dummy_frame.shape[0])

        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, final_size)
        if not writer.isOpened():
            raise RuntimeError(f"Не удалось инициализировать VideoWriter с кодеком '{codec}'")

        for t in ts:
            row_imgs = []
            for z in zs:
                paths = sorted(data[t][z])
                print(f"Группа t={t}, z={z}, файлов: {len(paths)}")
                imgs = [read_image(p) for p in paths if read_image(p) is not None]
                while len(imgs) < group_count:
                    imgs.append(np.ones((h, w, 3), dtype=np.uint8) * 255)  # Добавляем пустые изображения, если их меньше
                row_imgs.append(imgs)

            grid = row_imgs
            canvas = make_canvas_from_grid(grid, (len(zs), group_count), (h, w))
            canvas = downscale_if_needed(canvas, codec)
            writer.write(canvas)

        writer.release()
    else:
        fourcc = cv2.VideoWriter_fourcc(*codec)
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))
        if not writer.isOpened():
            raise RuntimeError(f"Не удалось инициализировать VideoWriter с кодеком '{codec}'")

        for p in sorted(files):
            img = read_image(p)
            if img is not None:
                writer.write(img)

        writer.release()


def browse_directory(entry):
    dir_path = filedialog.askdirectory()
    if dir_path:
        entry.delete(0, tk.END)
        entry.insert(0, dir_path)


def browse_savefile(entry):
    file = filedialog.asksaveasfilename(
        defaultextension='.mp4',
        filetypes=[('MP4 files', '*.mp4'), ('AVI files', '*.avi')]
    )
    if file:
        entry.delete(0, tk.END)
        entry.insert(0, file)


def start_process(inp_entry, out_entry, fps_entry, codec_combo, canvas_var):
    inp = inp_entry.get().strip()
    out = out_entry.get().strip()
    try:
        fps = int(fps_entry.get())
    except ValueError:
        messagebox.showerror("Ошибка", "FPS должен быть целым числом")
        return
    codec = codec_combo.get()
    if codec not in AVAILABLE_CODECS:
        messagebox.showerror("Ошибка", f"Выберите корректный кодек ({', '.join(AVAILABLE_CODECS)})")
        return
    if not inp or not out:
        messagebox.showerror("Ошибка", "Укажите папку и имя выходного файла")
        return
    try:
        collect_and_write_video(inp, out, fps, codec, canvas_var.get())
        messagebox.showinfo("Готово", f"Видео сохранено: {out}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def build_gui():
    root = tk.Tk()
    root.title("Сборщик изображений в видео")
    root.geometry('600x260')
    root.resizable(False, False)

    tk.Label(root, text="Папка с изображениями:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
    inp_entry = tk.Entry(root, width=50)
    inp_entry.grid(row=0, column=1)
    tk.Button(root, text="Обзор...", command=lambda: browse_directory(inp_entry)).grid(row=0, column=2, padx=5)

    tk.Label(root, text="Выходной файл:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
    out_entry = tk.Entry(root, width=50)
    out_entry.grid(row=1, column=1)
    tk.Button(root, text="Сохранить как...", command=lambda: browse_savefile(out_entry)).grid(row=1, column=2, padx=5)

    tk.Label(root, text="FPS:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
    fps_entry = tk.Entry(root, width=10)
    fps_entry.insert(0, '10')
    fps_entry.grid(row=2, column=1, sticky='w')

    tk.Label(root, text="Кодек:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
    codec_combo = ttk.Combobox(root, values=AVAILABLE_CODECS, state='readonly', width=10)
    codec_combo.grid(row=3, column=1, sticky='w')
    codec_combo.current(0)

    canvas_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Преобразование в холст (группировка по t/z)", variable=canvas_var).grid(row=4, column=1, sticky='w')

    tk.Button(
        root,
        text="Начать",
        width=20,
        bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
        command=lambda: start_process(inp_entry, out_entry, fps_entry, codec_combo, canvas_var)
    ).grid(row=5, column=1, pady=20)

    root.mainloop()


if __name__ == '__main__':
    build_gui()
