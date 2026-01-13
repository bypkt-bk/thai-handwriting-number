import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from send2trash import send2trash

class NeuButton(tk.Canvas):
    def __init__(self, parent, text, command, width=120, height=50, radius=20,
                 bg="#E6E6E6", fg="#000000", font=("Helvetica Neue", 13, "bold")):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)

        self.command = command
        self.radius = radius
        self.bg_color = bg
        self.fg = fg
        self.font = font
        self.text = text
        self.width = width
        self.height = height

        self.draw_raised()
        self.create_text(width//2, height//2, text=text, fill=fg, font=font)

        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

    def round_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2,
            x1+r, y2, x1, y2, x1, y2-r,
            x1, y1+r, x1, y1, x1+r, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def draw_raised(self):
        self.delete("all")
        self.round_rect(6, 6, self.width, self.height, self.radius, fill="#BEBEBE", outline="")
        self.round_rect(0, 0, self.width-6, self.height-6, self.radius, fill="#FFFFFF", outline="")
        self.round_rect(3, 3, self.width-3, self.height-3, self.radius, fill=self.bg_color, outline="")
        self.create_text(self.width//2, self.height//2, text=self.text, fill=self.fg, font=self.font)

    def draw_pressed(self):
        self.delete("all")
        self.round_rect(0, 0, self.width-3, self.height-3, self.radius, fill="#BEBEBE", outline="")
        self.round_rect(3, 3, self.width, self.height, self.radius, fill="#FFFFFF", outline="")
        self.round_rect(3, 3, self.width-3, self.height-3, self.radius, fill=self.bg_color, outline="")
        self.create_text(self.width//2, self.height//2, text=self.text, fill=self.fg, font=self.font)

    def on_press(self, event):
        self.draw_pressed()

    def on_release(self, event):
        self.draw_raised()
        if self.command:
            self.command()

class MacDatasetCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Dataset Cleaner")
        self.root.geometry("1000x800")
        self.root.configure(bg="#E6E6E6")

        self.bg = "#E6E6E6"
        self.panel = "#E6E6E6"
        self.text = "#333333"

        self.image_list = []
        self.current_index = 0
        self.current_image_path = None

        self.dataset_base_path = "/Users/bypkt/clicknext/thai-handwriting-number/data/raw/thai-handwriting-number.appspot.com"

        header = tk.Frame(root, bg=self.bg)
        header.pack(fill="x", padx=30, pady=20)

        self.folder_label = tk.Label(header, text="Waiting...", font=("Helvetica Neue", 28, "bold"), bg=self.bg, fg=self.text)
        self.folder_label.pack(side="left")

        self.count_label = tk.Label(header, text="0 / 0", font=("Helvetica Neue", 18), bg=self.bg, fg="#888888")
        self.count_label.pack(side="right")

        panel_container = tk.Frame(root, bg=self.bg)
        panel_container.pack(expand=True, fill="both", padx=30, pady=10)

        self.image_frame = tk.Frame(panel_container, bg=self.panel)
        self.image_frame.pack(expand=True, fill="both")

        self.image_label = tk.Label(self.image_frame, text="Open folder to start", bg=self.panel, fg="#999999", font=("Helvetica Neue", 16))
        self.image_label.pack(expand=True)

        self.filename_label = tk.Label(root, text="", bg=self.bg, fg="#888888", font=("Menlo", 12))
        self.filename_label.pack(pady=10)

        controls = tk.Frame(root, bg=self.bg)
        controls.pack(fill="x", pady=20)

        top_controls = tk.Frame(controls, bg=self.bg)
        top_controls.pack(fill="x")

        dataset_center_frame = tk.Frame(top_controls, bg=self.bg)
        dataset_center_frame.pack(expand=True)

        for i in range(10):
            NeuButton(
                dataset_center_frame,
                f"⚡ {i}",
                lambda i=i: self.open_quick_path(os.path.join(self.dataset_base_path, str(i))),
                width=70
            ).pack(side="left", padx=6)

        bottom_controls = tk.Frame(controls, bg=self.bg)
        bottom_controls.pack(fill="x", pady=15)

        NeuButton(bottom_controls, "📂 Open Folder", self.select_folder, width=180).pack(side="left", padx=10)
        NeuButton(bottom_controls, "⬅ Back", self.prev_image, width=140).pack(side="right", padx=10)
        NeuButton(bottom_controls, "✔ Keep", self.next_image, width=160).pack(side="right", padx=10)
        NeuButton(bottom_controls, "🗑 Delete", self.delete_image, width=160).pack(side="right", padx=10)

        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Down>', lambda e: self.delete_image())

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.load_folder(folder)

    def open_quick_path(self, path):
        if not os.path.exists(path):
            messagebox.showerror("Path not found", f"Folder not found:\n{path}")
            return
        self.load_folder(path)

    def load_folder(self, folder):
        self.image_list = []
        valid = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

        for r, d, f in os.walk(folder):
            for file in f:
                if file.lower().endswith(valid):
                    self.image_list.append(os.path.join(r, file))

        self.image_list.sort()
        if not self.image_list:
            messagebox.showinfo("Info", "No images found.")
            return

        self.current_index = 0
        self.load_image()

    def load_image(self):
        if not self.image_list:
            self.image_label.config(image="", text="Done!")
            return

        self.current_index %= len(self.image_list)
        self.current_image_path = self.image_list[self.current_index]

        parent = os.path.basename(os.path.dirname(self.current_image_path))
        self.folder_label.config(text=f"Class: {parent}")
        self.count_label.config(text=f"{self.current_index+1} / {len(self.image_list)}")
        self.filename_label.config(text=os.path.basename(self.current_image_path))

        try:
            img = Image.open(self.current_image_path)
            w = self.image_frame.winfo_width()
            h = self.image_frame.winfo_height()
            if w < 100: w = 800
            if h < 100: h = 500

            img.thumbnail((w, h))
            self.tk_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_image, text="")
        except:
            self.next_image()

    def next_image(self):
        if self.image_list:
            self.current_index += 1
            self.load_image()

    def prev_image(self):
        if self.image_list:
            self.current_index -= 1
            self.load_image()

    def delete_image(self):
        if self.current_image_path:
            try:
                send2trash(self.current_image_path)
                del self.image_list[self.current_index]
                self.load_image()
            except:
                pass

if __name__ == "__main__":
    root = tk.Tk()
    app = MacDatasetCleaner(root)
    root.mainloop()