import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFilter
import numpy as np

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Лабораторная работа №9")
        self.pack(padx=10, pady=10)
        self.create_widgets()
        self.original_image = None
        self.low_pass_image = None
        self.high_pass_image = None

    def create_widgets(self):
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side="top", fill="x", pady=5)
        self.image_frame = tk.Frame(self)
        self.image_frame.pack(side="bottom", fill="both", expand=True, pady=10)

        button_width = 20

        self.open_button = tk.Button(self.button_frame, width=button_width, text="Открыть изображение", command=self.open_image)
        self.open_button.pack(side="left", padx=5)

        self.image_label_original = tk.Label(self.image_frame, text="Оригинал")
        self.image_label_original.grid(row=0, column=0, padx=10, pady=10)

        self.image_label_low_pass = tk.Label(self.image_frame, text="Результат ФНЧ")
        self.image_label_low_pass.grid(row=0, column=1, padx=10, pady=10)

        self.image_label_high_pass = tk.Label(self.image_frame, text="Результат ФВЧ")
        self.image_label_high_pass.grid(row=0, column=2, padx=10, pady=10)

    def open_image(self):
        path = filedialog.askopenfilename()
        if path:
            self.original_image = Image.open(path).convert("RGB")
            self.display_image(self.original_image, self.image_label_original)
            self.low_pass_transform()
            self.high_pass_transform()

    def low_pass_transform(self):
        if self.original_image:
            T = 100
            image_np = np.array(self.original_image)
            brightness = np.mean(image_np, axis=2)
            mask = brightness > T
            blurred_image = self.original_image.filter(ImageFilter.GaussianBlur(10))
            result_np = image_np.copy()
            blurred_np = np.array(blurred_image)
            result_np[mask] = blurred_np[mask]
            self.low_pass_image = Image.fromarray(result_np)
            self.display_image(self.low_pass_image, self.image_label_low_pass)

    def high_pass_transform(self):
        if self.original_image:
            width, height = self.original_image.size

            left_half = self.original_image.crop((0, 0, width // 2, height))
            left_np = np.array(left_half)
            brightness = np.mean(left_np, axis=2)
            saturation = np.max(left_np, axis=2) - np.min(left_np, axis=2)
            left_brightness = Image.fromarray(brightness.astype(np.uint8)).filter(ImageFilter.FIND_EDGES)
            left_saturation = Image.fromarray(saturation.astype(np.uint8)).filter(ImageFilter.FIND_EDGES)
            left_result = np.stack([np.array(left_brightness)] * 3, axis=-1)

            right_half = self.original_image.crop((width // 2, 0, width, height))
            right_np = np.array(right_half)
            saturation = np.max(right_np, axis=2) - np.min(right_np, axis=2)
            hue = np.angle(np.exp(1j * np.arctan2(right_np[:, :, 1] - right_np[:, :, 0], right_np[:, :, 2])))
            right_saturation = Image.fromarray(saturation.astype(np.uint8)).filter(ImageFilter.FIND_EDGES)
            right_result = np.stack([np.array(right_saturation)] * 3, axis=-1)

            result = Image.new("RGB", (width, height))
            result.paste(Image.fromarray(left_result.astype(np.uint8)), (0, 0))
            result.paste(Image.fromarray(right_result.astype(np.uint8)), (width // 2, 0))

            self.high_pass_image = result
            self.display_image(self.high_pass_image, self.image_label_high_pass)

    def display_image(self, image, label):
        image_tk = ImageTk.PhotoImage(image)
        label.config(image=image_tk)
        label.image = image_tk

root = tk.Tk()
app = Application(master=root)
app.mainloop()
