import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from src.core.torneo import Torneo  
from src.ui.torneo_screen import TorneoScreen 

DATA_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data_storage")

class CrearCompetenciaScreen:
    def __init__(self, root, admin_menu_instance):
        self.admin_menu_instance = admin_menu_instance 
        self.top_level = tk.Toplevel(root)
        self.top_level.title("Crear Nueva Competencia")
        self.top_level.state('zoomed') # Maximizar la ventana
        self.top_level.grab_set() # Hacer esta ventana modal
        self.top_level.protocol("WM_DELETE_WINDOW", self.cerrar_ventana) # Manejar cierre

        # Configurar el estilo
        style = ttk.Style(self.top_level)
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))

        # Frame principal que se expande con la ventana
        main_frame_expansible = ttk.Frame(self.top_level, style="Dark.TFrame") # Aplicar estilo para el fondo
        main_frame_expansible.pack(fill=tk.BOTH, expand=True)

        
        style = ttk.Style(self.top_level)
        style.configure("Dark.TFrame", background="#dadada") # Gris oscuro
        
        
        main_frame_expansible.columnconfigure(0, weight=1)
        main_frame_expansible.rowconfigure(0, weight=1)
        
        
        content_container = ttk.Frame(main_frame_expansible, padding="20", width=700) # Ancho deseado
        content_container.grid(row=0, column=0, sticky="") # Centrado

        titulo_label = ttk.Label(content_container, text="Formulario de Nueva Competencia", style="Header.TLabel")
        titulo_label.pack(pady=(0, 20))

        # Aquí irían los campos del formulario (nombre, fecha, etc.) - ahora dentro de content_container
        ttk.Label(content_container, text="Nombre de la Competencia:").pack(anchor=tk.W, pady=(5,0))
        self.nombre_entry = ttk.Entry(content_container, width=40)
        self.nombre_entry.pack(fill=tk.X, pady=(0,10))

        ttk.Label(content_container, text="Fecha (YYYY-MM-DD):").pack(anchor=tk.W, pady=(5,0))
        self.fecha_entry = ttk.Entry(content_container, width=40)
        self.fecha_entry.pack(fill=tk.X, pady=(0,10))

        ttk.Label(content_container, text="Lugar de la Competencia:").pack(anchor=tk.W, pady=(5,0))
        self.lugar_entry = ttk.Entry(content_container, width=40)
        self.lugar_entry.pack(fill=tk.X, pady=(0,10))

        # Botones - ahora dentro de content_container
        botones_frame = ttk.Frame(content_container)
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
            self.top_level.withdraw() # Ocultar esta ventana
            TorneoScreen(self.admin_menu_instance.root if self.admin_menu_instance else self.top_level.master, self.admin_menu_instance, ruta_archivo)
        except IOError as e:
            messagebox.showerror("Error al Guardar", f"No se pudo guardar el archivo de la competencia: {e}", parent=self.top_level)
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error inesperado: {e}", parent=self.top_level)

    def cerrar_ventana(self, abrir_torneo_screen=False, ruta_archivo=None):
        if not abrir_torneo_screen:
            self.top_level.destroy()
            if self.admin_menu_instance and hasattr(self.admin_menu_instance, 'root') and self.admin_menu_instance.root.winfo_exists():
                self.admin_menu_instance.root.state('zoomed') # Set main window to maximized state
                self.admin_menu_instance.root.deiconify() # Mostrar ventana principal de nuevo
        else:
            # Este caso es manejado directamente en guardar_competencia para pasar la ruta_archivo
            pass
