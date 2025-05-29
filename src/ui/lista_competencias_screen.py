import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
from src.ui.torneo_screen import TorneoScreen # Importar la pantalla de torneo

DATA_STORAGE_PATH = "c:/Users/pc/Documents/2.Universidad/2025-1/PRG-IV/Proyecto_Final/data_storage/"

class ListaCompetenciasScreen:
    def __init__(self, root, admin_menu_instance):
        self.admin_menu_instance = admin_menu_instance
        self.top_level = tk.Toplevel(root)
        self.top_level.title("Abrir Competencia Existente")
        self.top_level.state('zoomed') # Maximizar la ventana
        self.top_level.grab_set()
        self.top_level.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        style = ttk.Style(self.top_level)
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

        # Frame principal que se expande con la ventana
        main_frame_expansible = ttk.Frame(self.top_level, style="Dark.TFrame") # Aplicar estilo para el fondo
        main_frame_expansible.pack(fill=tk.BOTH, expand=True)

        # Estilo para el frame principal oscuro
        # Similar a crear_competencia_screen, asegurar que el estilo se aplique.
        style = ttk.Style(self.top_level) # Asegurarse que el estilo se aplica a esta ventana
        style.configure("Dark.TFrame", background="#dadada") # Gris oscuro
        
        # Configurar el grid del frame expansible para centrar el content_container
        main_frame_expansible.columnconfigure(0, weight=1)
        main_frame_expansible.rowconfigure(0, weight=1)
        
        # Contenedor para el contenido real, con un ancho máximo
        content_container = ttk.Frame(main_frame_expansible, padding="20", width=800) # Ancho deseado
        content_container.grid(row=0, column=0, sticky="") # Centrado

        titulo_label = ttk.Label(content_container, text="Seleccionar Competencia", style="Header.TLabel")
        titulo_label.pack(pady=(0, 20))

        # Treeview para mostrar las competencias - ahora dentro de content_container
        tree_frame = ttk.Frame(content_container)
        tree_frame.pack(expand=True, fill=tk.BOTH, pady=(0,10))

        self.tree = ttk.Treeview(tree_frame, columns=("nombre", "fecha_modificacion"), show="headings")
        self.tree.heading("nombre", text="Nombre de la Competencia")
        self.tree.heading("fecha_modificacion", text="Última Modificación")
        self.tree.column("nombre", width=350)
        self.tree.column("fecha_modificacion", width=150)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.cargar_competencias()

        # Botones - ahora dentro de content_container
        botones_frame = ttk.Frame(content_container)
        botones_frame.pack(fill=tk.X, pady=(10,0))

        # Configurar para que el tree_frame (y por ende el treeview) se expanda dentro del content_container
        content_container.rowconfigure(1, weight=1) # Para que tree_frame se expanda verticalmente
        content_container.columnconfigure(0, weight=1) # Para que tree_frame se expanda horizontalmente

        btn_abrir = ttk.Button(botones_frame, text="Abrir Seleccionada", command=self.abrir_competencia)
        btn_abrir.pack(side=tk.RIGHT, padx=(10,0))

        btn_cancelar = ttk.Button(botones_frame, text="Cancelar", command=self.cerrar_ventana)
        btn_cancelar.pack(side=tk.RIGHT)

        self.tree.bind("<Double-1>", lambda e: self.abrir_competencia())

    def cargar_competencias(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        if not os.path.exists(DATA_STORAGE_PATH):
            os.makedirs(DATA_STORAGE_PATH, exist_ok=True)
            messagebox.showinfo("Información", f"Directorio de datos '{DATA_STORAGE_PATH}' no encontrado. Se ha creado.", parent=self.top_level)
            return

        try:
            archivos = [f for f in os.listdir(DATA_STORAGE_PATH) if os.path.isfile(os.path.join(DATA_STORAGE_PATH, f))]
            if not archivos:
                self.tree.insert("", tk.END, values=("No hay competencias guardadas.", ""))
                return

            for archivo in archivos:
                ruta_completa = os.path.join(DATA_STORAGE_PATH, archivo)
                try:
                    timestamp = os.path.getmtime(ruta_completa)
                    fecha_mod = tk.StringVar()
                    fecha_mod.set(str(os.path.getmtime(ruta_completa))) 
                    from datetime import datetime
                    fecha_mod_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    self.tree.insert("", tk.END, values=(archivo, fecha_mod_str))
                except Exception as e:
                    print(f"Error al obtener info de {archivo}: {e}")
                    self.tree.insert("", tk.END, values=(archivo, "Error al leer fecha"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo acceder al directorio de competencias: {e}", parent=self.top_level)

    def abrir_competencia(self):
        seleccionado = self.tree.focus()
        if not seleccionado:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione una competencia de la lista.", parent=self.top_level)
            return

        item = self.tree.item(seleccionado)
        nombre_competencia = item['values'][0]

        if nombre_competencia == "No hay competencias guardadas.":
             messagebox.showinfo("Información", "No hay competencias para abrir.", parent=self.top_level)
             return

        ruta_competencia_seleccionada = os.path.join(DATA_STORAGE_PATH, nombre_competencia)

        if not os.path.exists(ruta_competencia_seleccionada):
            messagebox.showerror("Error", f"El archivo de la competencia '{nombre_competencia}' no fue encontrado.", parent=self.top_level)
            return

        # Ocultar esta ventana y abrir la pantalla del torneo
        self.top_level.withdraw()
        TorneoScreen(self.admin_menu_instance.root if self.admin_menu_instance else self.top_level.master, 
                     self.admin_menu_instance, 
                     ruta_competencia_seleccionada)
        # La ventana ListaCompetenciasScreen ya no necesita llamar a cerrar_ventana explícitamente aquí,
        # ya que TorneoScreen manejará el flujo y el retorno al menú principal si es necesario.

    def cerrar_ventana(self):
        self.top_level.destroy()
        if self.admin_menu_instance and hasattr(self.admin_menu_instance, 'root') and self.admin_menu_instance.root.winfo_exists():
            self.admin_menu_instance.root.state('zoomed') # Set main window to maximized state
            self.admin_menu_instance.root.deiconify()

if __name__ == "__main__":
    root_test = tk.Tk()
    root_test.withdraw() # Ocultar la ventana raíz principal de prueba
    app = ListaCompetenciasScreen(root_test, None)
    root_test.mainloop()