import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from src.core.torneo import Torneo  # Importar la clase Torneo
from src.ui.torneo_screen import TorneoScreen # Importar la pantalla de torneo

DATA_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data_storage")

class CrearCompetenciaScreen:
    def __init__(self, root, admin_menu_instance):
        self.admin_menu_instance = admin_menu_instance # Guardar referencia al menú principal
        self.top_level = tk.Toplevel(root)
        self.top_level.title("Crear Nueva Competencia")
        self.top_level.geometry("600x400")
        self.top_level.grab_set() # Hacer esta ventana modal
        self.top_level.protocol("WM_DELETE_WINDOW", self.cerrar_ventana) # Manejar cierre

        # Configurar el estilo
        style = ttk.Style(self.top_level)
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))

        main_frame = ttk.Frame(self.top_level, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        titulo_label = ttk.Label(main_frame, text="Formulario de Nueva Competencia", style="Header.TLabel")
        titulo_label.pack(pady=(0, 20))

        # Aquí irían los campos del formulario (nombre, fecha, etc.)
        # Ejemplo:
        ttk.Label(main_frame, text="Nombre de la Competencia:").pack(anchor=tk.W, pady=(5,0))
        self.nombre_entry = ttk.Entry(main_frame, width=40)
        self.nombre_entry.pack(fill=tk.X, pady=(0,10))

        ttk.Label(main_frame, text="Fecha (YYYY-MM-DD):").pack(anchor=tk.W, pady=(5,0))
        self.fecha_entry = ttk.Entry(main_frame, width=40)
        self.fecha_entry.pack(fill=tk.X, pady=(0,10))

        ttk.Label(main_frame, text="Lugar de la Competencia:").pack(anchor=tk.W, pady=(5,0))
        self.lugar_entry = ttk.Entry(main_frame, width=40)
        self.lugar_entry.pack(fill=tk.X, pady=(0,10))

        # Botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill=tk.X, pady=(20,0))

        btn_guardar = ttk.Button(botones_frame, text="Guardar Competencia", command=self.guardar_competencia)
        btn_guardar.pack(side=tk.RIGHT, padx=(10,0))

        btn_cancelar = ttk.Button(botones_frame, text="Cancelar", command=self.cerrar_ventana)
        btn_cancelar.pack(side=tk.RIGHT)

    def guardar_competencia(self):
        nombre = self.nombre_entry.get().strip()
        fecha = self.fecha_entry.get().strip()
        lugar = self.lugar_entry.get().strip()

        if not nombre or not fecha or not lugar:
            messagebox.showwarning("Campos Vacíos", "Por favor, complete todos los campos (Nombre, Fecha y Lugar).", parent=self.top_level)
            return

        # Crear instancia de Torneo
        try:
            nueva_competencia = Torneo(nombre=nombre, fecha=fecha, lugar=lugar)
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e), parent=self.top_level)
            return

        # Guardar en archivo JSON
        if not os.path.exists(DATA_STORAGE_PATH):
            try:
                os.makedirs(DATA_STORAGE_PATH)
            except OSError as e:
                messagebox.showerror("Error de Directorio", f"No se pudo crear el directorio de datos: {e}", parent=self.top_level)
                return

        # Usar el nombre de la competencia como nombre de archivo (sanitizado)
        nombre_archivo = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in nombre).rstrip()
        if not nombre_archivo:
            nombre_archivo = "competencia_sin_nombre"
        nombre_archivo = f"{nombre_archivo}.json"
        ruta_archivo = os.path.join(DATA_STORAGE_PATH, nombre_archivo)

        # Verificar si el archivo ya existe
        if os.path.exists(ruta_archivo):
            respuesta = messagebox.askyesno("Archivo Existente", 
                                            f"Ya existe una competencia con el nombre '{nombre}'.\n¿Desea sobrescribirla?", 
                                            parent=self.top_level)
            if not respuesta:
                return # No sobrescribir, el usuario canceló

        competencia_data = {
            "nombre": nueva_competencia.nombre,
            "fecha": nueva_competencia.fecha,
            "lugar": nueva_competencia.lugar,
            "categorias": [], # Inicialmente vacío
            "jueces": []      # Inicialmente vacío
        }

        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(competencia_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Éxito", f"Competencia '{nombre}' guardada correctamente en {ruta_archivo}.", parent=self.top_level)
            # Abrir la pantalla del torneo recién creado
            self.top_level.withdraw() # Ocultar esta ventana
            TorneoScreen(self.admin_menu_instance.root if self.admin_menu_instance else self.top_level.master, self.admin_menu_instance, ruta_archivo)
            # No llamar a self.cerrar_ventana() aquí, ya que TorneoScreen manejará el flujo
        except IOError as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo de la competencia: {e}", parent=self.top_level)
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error inesperado: {e}", parent=self.top_level)

    def cerrar_ventana(self, abrir_torneo_screen=False, ruta_archivo=None):
        if not abrir_torneo_screen:
            self.top_level.destroy()
            if self.admin_menu_instance and hasattr(self.admin_menu_instance, 'root') and self.admin_menu_instance.root.winfo_exists():
                self.admin_menu_instance.root.deiconify() # Mostrar ventana principal de nuevo
        else:
            # Este caso es manejado directamente en guardar_competencia para pasar la ruta_archivo
            pass

if __name__ == "__main__":
    # Esto es solo para probar esta pantalla de forma aislada
    # En la aplicación real, se llamaría desde admin_menu.py
    root_test = tk.Tk()
    root_test.withdraw() # Ocultar la ventana raíz principal de prueba
    app = CrearCompetenciaScreen(root_test, None) # Pasar None como admin_menu_instance para prueba
    root_test.mainloop()