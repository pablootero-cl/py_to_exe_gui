import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
from analysis import detect_gui
from utils import add_tooltip
from converter import convertir
from languages import IDIOMAS

# 🔧 Leer idioma desde archivo externo en la carpeta del ejecutable
def obtener_idioma_actual():
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    idioma_path = os.path.join(exe_dir, "idioma.py")

    try:
        with open(idioma_path, "r", encoding="utf-8") as f:
            contenido = f.read()
            if 'IDIOMA_ACTUAL' in contenido:
                idioma = contenido.split('=')[1].strip().strip('"').strip("'")
                return idioma
    except Exception:
        pass

    return "es"  # fallback a español si hay error

IDIOMA_ACTUAL = obtener_idioma_actual()
TEXTOS = IDIOMAS.get(IDIOMA_ACTUAL, IDIOMAS["es"])

IDIOMAS_DISPONIBLES = {
    "Español": "es",
    "English": "en",
    "中文": "zh",
    "Українська": "uk",
    "Français": "fr",
    "Deutsch": "de"
}

def cambiar_idioma(nuevo_idioma):
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    idioma_path = os.path.join(exe_dir, "idioma.py")

    try:
        with open(idioma_path, "w", encoding="utf-8") as f:
            f.write(f'IDIOMA_ACTUAL = "{nuevo_idioma}"\n')
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el idioma:\n{e}")
        return

    if getattr(sys, 'frozen', False):  # Modo .exe
        respuesta = messagebox.askyesno(
            "Reiniciar aplicación",
            "El idioma ha sido cambiado.\n¿Deseas reiniciar la aplicación ahora?"
        )
        if respuesta:
            exe_path = os.path.join(exe_dir, os.path.basename(sys.argv[0]))
            try:
                subprocess.Popen([exe_path], close_fds=True)
                sys.exit()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reiniciar la aplicación:\n{e}")
    else:  # Modo Python
        # Recargar idioma dinámicamente
        global TEXTOS
        TEXTOS = IDIOMAS.get(nuevo_idioma, IDIOMAS["es"])

        root = tk._default_root
        root.title(TEXTOS["titulo"])

        # 🔁 Destruir todo y reconstruir interfaz completa
        for widget in root.winfo_children():
            widget.destroy()

        # 🔁 Crear menú actualizado
        menubar = tk.Menu(root)
        menubar.add_cascade(label=TEXTOS["idioma"], menu=crear_menu_idioma(root))
        root.config(menu=menubar)

        # 🔁 Crear widgets de la app
        PyToExeApp(root)

def crear_menu_idioma(root):
    menu_idioma = tk.Menu(root, tearoff=0)
    for nombre, codigo in IDIOMAS_DISPONIBLES.items():
        menu_idioma.add_command(label=nombre, command=lambda c=codigo: cambiar_idioma(c))
    return menu_idioma

def launch_gui():
    root = tk.Tk()
    root.geometry("560x360")
    root.resizable(False, False)
    root.iconbitmap("piton.ico")
    root.title(TEXTOS["titulo"])

    menubar = tk.Menu(root)
    menubar.add_cascade(label=TEXTOS["idioma"], menu=crear_menu_idioma(root))
    root.config(menu=menubar)

    app = PyToExeApp(root)
    root.mainloop()

class PyToExeApp:
    def __init__(self, root):
        self.root = root

        self.file_path = tk.StringVar()
        self.icon_path = tk.StringVar()
        self.console_option = tk.BooleanVar(value=True)
        self.gui_detected = False
        self.running_as_exe = getattr(sys, 'frozen', False)

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self.root, text=TEXTOS["seleccionar_archivo"], font=("Segoe UI", 11)).pack(pady=10)

        frame = ttk.Frame(self.root)
        frame.pack(pady=5)
        ttk.Entry(frame, textvariable=self.file_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text=TEXTOS["buscar"], command=self.browse_file).pack(side=tk.LEFT)

        ttk.Label(self.root, text=TEXTOS["seleccionar_icono"], font=("Segoe UI", 10)).pack(pady=10)
        icon_frame = ttk.Frame(self.root)
        icon_frame.pack(pady=5)
        ttk.Entry(icon_frame, textvariable=self.icon_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(icon_frame, text=TEXTOS["buscar"], command=self.browse_icon).pack(side=tk.LEFT)

        onefile_check = ttk.Checkbutton(self.root, text=TEXTOS["modo_onefile"])
        onefile_check.pack(pady=5)
        if self.running_as_exe:
            onefile_check.state(['disabled'])
            add_tooltip(onefile_check, TEXTOS["tooltip_exe"])
        else:
            self.onefile_option = tk.BooleanVar(value=True)
            onefile_check.config(variable=self.onefile_option)

        ttk.Checkbutton(self.root, text=TEXTOS["mostrar_consola"], variable=self.console_option).pack(pady=5)

        ttk.Button(self.root, text=TEXTOS["boton_convertir"], command=self.convert).pack(pady=10)

        # ✅ Créditos discretos al pie de la interfaz
        creditos = ttk.Label(
            self.root,
            text=TEXTOS["creditos"],
            font=("Segoe UI", 8),
            foreground="gray"
        )
        creditos.pack(side=tk.BOTTOM, pady=5)



    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file:
            if os.path.abspath(file) == os.path.abspath(sys.argv[0]):
                messagebox.showerror(TEXTOS["error"], TEXTOS["error_convertidor"])
                return

            self.file_path.set(file)
            self.gui_detected = detect_gui(file)

            if not self.gui_detected:
                self.console_option.set(True)

    def browse_icon(self):
        icon = filedialog.askopenfilename(filetypes=[("Icon Files", "*.ico")])
        if icon:
            self.icon_path.set(icon)

    def convert(self):
        convertir(
            script_path=self.file_path.get(),
            icon_path=self.icon_path.get(),
            console=self.console_option.get(),
            onefile=self.onefile_option.get() if hasattr(self, 'onefile_option') else False,
            gui_detected=self.gui_detected,
            running_as_exe=self.running_as_exe
        )