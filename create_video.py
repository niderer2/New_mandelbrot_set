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

def read_image(path: Path):
    """Читает изображение через Pillow и возвращает BGR numpy array"""
    try:
        img = Image.open(path)
        img = img.convert('RGB')
        arr = np.array(img)
        return arr[..., ::-1]  # RGB -> BGR
    except Exception as e:
        print(f"Ошибка чтения {path}: {e}")
        return None

def group_by_canvas_keys(items, canvas_dims=3):
    grouped = {}
    for key, path in items:
        canvas_key = key[:canvas_dims]  # первые N измерений формируют холст
        grouped.setdefault(canvas_key, []).append((key, path))
    return grouped

def make_canvas(images, tile_shape, img_shape):
    tile_h, tile_w = tile_shape
    img_h, img_w = img_shape
    canvas = np.ones((tile_h * img_h, tile_w * img_w, 3), dtype=np.uint8) * 255  # белый фон

    for idx, img in enumerate(images):
        row = idx // tile_w
        col = idx % tile_w
        if row < tile_h:
            canvas[row * img_h:(row + 1) * img_h, col * img_w:(col + 1) * img_w] = img
    return canvas

def collect_and_write_video(
    root_dir: str,
    output_path: str,
    fps: int,
    codec: str,
    use_canvas: bool
):
    root = Path(root_dir)
    files = [p for p in root.rglob('*') if p.suffix.lower() in SUPPORTED_EXTS]
    if not files:
        raise RuntimeError(f"В папке {root_dir} не найдено файлов {SUPPORTED_EXTS}")

    pattern = re.compile(r'=(-?\d+(?:\.\d+)?)')
    items = []
    for p in files:
        nums = pattern.findall(p.name)
        if len(nums) < 6:
            nums = pattern.findall(str(p))
        if len(nums) >= 6:
            vals = tuple(float(x) for x in nums[:6])
            items.append((vals, p))
    if not items:
        raise RuntimeError("Не удалось извлечь 6 численных параметров из названий.")
    items.sort(key=lambda x: x[0])

    first_img = read_image(items[0][1])
    if first_img is None:
        raise RuntimeError(f"Не удалось загрузить изображение: {items[0][1]}")
    h, w = first_img.shape[:2]

    if use_canvas:
        total = int(np.ceil(np.sqrt(len(items)))) ** 2
        side = int(np.sqrt(total))
        tile_shape = (side, side)
        canvas_size = (h * tile_shape[0], w * tile_shape[1])
        grouped = group_by_canvas_keys(items)
    else:
        canvas_size = (w, h)
        grouped = {(): items}  # все кадры в одной группе

    fourcc = cv2.VideoWriter_fourcc(*codec)
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (canvas_size[1], canvas_size[0]))
    if not writer.isOpened():
        raise RuntimeError(f"Не удалось инициализировать VideoWriter с кодеком '{codec}'")

    for key in sorted(grouped):
        group = grouped[key]
        if use_canvas:
            frame_paths = [p for _, p in sorted(group)]
            imgs = [read_image(p) for p in frame_paths]
            imgs = [img for img in imgs if img is not None]
            total = tile_shape[0] * tile_shape[1]
            if len(imgs) < total:
                raise RuntimeError(f"Недостаточно изображений для формирования полного холста: {len(imgs)} из {total}")
            canvas = make_canvas(imgs[:total], tile_shape, (h, w))
            writer.write(canvas)
        else:
            for _, p in group:
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
    tk.Checkbutton(root, text="Преобразование в холст (все кадры в таблице)", variable=canvas_var).grid(row=4, column=1, sticky='w')

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
