import os
import re
import importlib.util
import sysconfig

def detect_gui(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            gui_keywords = ['tkinter', 'pyqt', 'wxpython', 'kivy']
            return any(keyword in content for keyword in gui_keywords)
    except Exception:
        return False

def es_libreria_estandar(nombre):
    std_lib_path = sysconfig.get_paths()["stdlib"]
    try:
        spec = importlib.util.find_spec(nombre)
        return spec and spec.origin and spec.origin.startswith(std_lib_path)
    except Exception:
        return False

def detectar_librerias(script_path):
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        matches = re.findall(r'^\s*(?:import|from)\s+([a-zA-Z0-9_]+)', contenido, re.MULTILINE)
        librerias = set(matches)
        externas = []
        for lib in librerias:
            if not es_libreria_estandar(lib):
                try:
                    importlib.import_module(lib)
                except ImportError:
                    externas.append(lib)
        return externas
    except Exception:
        return []

def detectar_archivos_relacionados(script_path):
    base_dir = os.path.dirname(script_path)
    archivos_encontrados = []
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        posibles_rutas = re.findall(r'["\']([\w./\\-]+\.(?:png|jpg|jpeg|gif|ico|json|txt|csv|py))["\']', contenido)
        for ruta in posibles_rutas:
            ruta_absoluta = os.path.normpath(os.path.join(base_dir, ruta))
            if os.path.exists(ruta_absoluta):
                destino = os.path.dirname(ruta)
                archivos_encontrados.append((ruta_absoluta, destino))
    except Exception:
        pass
    return archivos_encontrados