import os
import sys
import shutil
import threading
import subprocess
from tkinter import messagebox
from analysis import detectar_librerias, detectar_archivos_relacionados
import PyInstaller.__main__
from languages import IDIOMAS

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
    return "es"

def convertir(script_path, icon_path, console, onefile, gui_detected, running_as_exe):
    def run_conversion():
        idioma = obtener_idioma_actual()
        TEXTOS = IDIOMAS.get(idioma, IDIOMAS["es"])

        if not script_path or not os.path.exists(script_path):
            messagebox.showerror(TEXTOS["error"], TEXTOS["seleccionar_archivo"])
            return

        if os.path.abspath(script_path) == os.path.abspath(sys.argv[0]):
            messagebox.showerror(TEXTOS["error"], TEXTOS["error_convertidor"])
            return

        librerias_faltantes = detectar_librerias(script_path)
        if librerias_faltantes:
            messagebox.showwarning(TEXTOS["error"], f"Instala manualmente: {', '.join(librerias_faltantes)}")

        # ✅ Mostrar mensaje de espera antes de iniciar
        messagebox.showinfo("Información", TEXTOS["mensaje_espera"])

        cmd = [
            "--hidden-import=platform",
            "--windowed" if gui_detected or not console else "--console",
        ]

        if not running_as_exe and onefile:
            cmd.append("--onefile")

        if icon_path:
            cmd.append(f"--icon={icon_path}")

        for origen, destino in detectar_archivos_relacionados(script_path):
            if origen and destino:
                cmd += ["--add-data", f"{origen};{destino}"]
            else:
                print(f"Advertencia: archivo relacionado inválido → origen: {origen}, destino: {destino}")

        cmd.append(script_path)

        nombre_script = os.path.splitext(os.path.basename(script_path))[0]
        carpeta_dist = os.path.join(os.getcwd(), "dist", nombre_script)

        if os.path.exists(carpeta_dist):
            respuesta = messagebox.askyesno(
                "Carpeta existente",
                f"La carpeta de salida '{carpeta_dist}' ya existe.\n¿Deseas eliminarla antes de continuar?"
            )
            if respuesta:
                try:
                    shutil.rmtree(carpeta_dist)
                except Exception as e:
                    messagebox.showerror(TEXTOS["error"], f"No se pudo eliminar la carpeta:\n{e}")
                    return
            else:
                messagebox.showinfo("Cancelado", "Conversión cancelada por el usuario.")
                return

        try:
            if running_as_exe:
                base_dir = os.path.dirname(sys.executable)
                portable_dir = os.path.join(base_dir, "pyinstaller_portable")
                python_exe = os.path.join(portable_dir, "Scripts", "python.exe")

                if not os.path.exists(python_exe):
                    messagebox.showerror(
                        "PyInstaller no disponible",
                        f"No se encontró python.exe en:\n{python_exe}"
                    )
                    return

                result = subprocess.run(
                    [python_exe, "-m", "PyInstaller"] + cmd,
                    capture_output=True,
                    text=True
                )

                if result.returncode != 0:
                    messagebox.showerror(TEXTOS["error"], f"PyInstaller falló:\n{result.stderr}")
                    return
            else:
                PyInstaller.__main__.run(cmd)

            messagebox.showinfo("Éxito", "¡Archivo .exe generado en la carpeta 'dist'!")
        except Exception as e:
            messagebox.showerror(TEXTOS["error"], f"Hubo un problema inesperado:\n{e}")

    threading.Thread(target=run_conversion).start()