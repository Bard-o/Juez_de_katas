import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# Asumimos que DATA_STORAGE_PATH se define de manera similar a otros screens
# o se pasa la ruta del archivo de la competencia directamente.
DATA_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data_storage")

class TorneoScreen:
    def __init__(self, root, admin_menu_instance, competencia_path):
        self.root = root
        self.admin_menu_instance = admin_menu_instance
        self.competencia_path = competencia_path
        self.competencia_data = None

        self.top_level = tk.Toplevel(root)
        self.top_level.title("Gestión de Torneo")
        self.top_level.state('zoomed') # Maximizar la ventana
        self.top_level.grab_set()
        self.top_level.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        self._cargar_datos_competencia()
        self._crear_interfaz()

    def _cargar_datos_competencia(self):
        if not self.competencia_path or not os.path.exists(self.competencia_path):
            messagebox.showerror("Error", f"No se pudo encontrar el archivo de la competencia: {self.competencia_path}", parent=self.top_level)
            self.cerrar_ventana()
            return
        try:
            with open(self.competencia_path, 'r', encoding='utf-8') as f:
                self.competencia_data = json.load(f)
            self.top_level.title(f"Torneo: {self.competencia_data.get('nombre', 'Sin Nombre')}")
        except Exception as e:
            messagebox.showerror("Error al Cargar", f"No se pudo cargar los datos de la competencia: {e}", parent=self.top_level)
            self.cerrar_ventana()

    def _crear_interfaz(self):
        if not self.competencia_data:
            return # No crear interfaz si no hay datos

        style = ttk.Style(self.top_level)
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

        # Frame principal que se expande con la ventana
        main_frame_expansible = ttk.Frame(self.top_level, style="Dark.TFrame") # Aplicar estilo para el fondo
        main_frame_expansible.pack(fill=tk.BOTH, expand=True)

        # Estilo para el frame principal oscuro
        # Asegurar que el estilo se aplique a esta ventana Toplevel.
        style.configure("Dark.TFrame", background="#dadada") # Gris oscuro
        
        # Configurar el grid del frame expansible para centrar el content_container
        main_frame_expansible.columnconfigure(0, weight=1)
        main_frame_expansible.rowconfigure(0, weight=1)
        
        # Contenedor para el contenido real, con un ancho máximo
        content_container = ttk.Frame(main_frame_expansible, padding="20", width=900) # Ancho deseado
        content_container.grid(row=0, column=0, sticky="") # Centrado

        # Título del Torneo - ahora dentro de content_container
        titulo_label = ttk.Label(content_container, text=f"Torneo: {self.competencia_data.get('nombre', 'Desconocido')}", style="Header.TLabel")
        titulo_label.pack(pady=(0, 20))

        # Botones de acción - ahora dentro de content_container
        botones_frame = ttk.Frame(content_container)
        botones_frame.pack(fill=tk.X, pady=(0, 10))

        btn_add_categoria = ttk.Button(botones_frame, text="Añadir Categoría", command=self.abrir_pantalla_añadir_categoria)
        btn_add_categoria.pack(side=tk.LEFT, padx=(0, 10))

        btn_add_juez = ttk.Button(botones_frame, text="Añadir Juez", command=self.abrir_pantalla_añadir_juez)
        btn_add_juez.pack(side=tk.LEFT)

        # PanedWindow para dividir Jueces y Categorías - ahora dentro de content_container
        paned_window = ttk.PanedWindow(content_container, orient=tk.HORIZONTAL)
        # El paned_window se expandirá gracias a la configuración de row/columnconfigure en content_container
        paned_window.pack(expand=True, fill=tk.BOTH, pady=(10,0)) # Quitado padding inferior, se maneja con el frame de botones

        # Frame para el botón de volver - ahora dentro de content_container
        bottom_frame = ttk.Frame(content_container)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        btn_volver = ttk.Button(bottom_frame, text="Volver al Menú Principal", command=self.cerrar_ventana)
        btn_volver.pack(side=tk.LEFT)

        # Configurar para que el paned_window se expanda dentro del content_container
        content_container.rowconfigure(2, weight=1) # Asumiendo que el título es fila 0, botones_frame fila 1, paned_window fila 2
        content_container.columnconfigure(0, weight=1) # Para que los elementos internos se expandan horizontalmente


        # Frame para Jueces
        jueces_frame_container = ttk.LabelFrame(paned_window, text="Jueces del Torneo", padding="10")
        paned_window.add(jueces_frame_container, weight=1)

        self.tree_jueces = ttk.Treeview(jueces_frame_container, columns=("id_juez", "nombre", "club"), show="headings", height=10)
        self.tree_jueces.heading("id_juez", text="ID")
        self.tree_jueces.heading("nombre", text="Nombre")
        self.tree_jueces.heading("club", text="Club")
        self.tree_jueces.column("id_juez", width=80, anchor=tk.W)
        self.tree_jueces.column("nombre", width=150, anchor=tk.W)
        self.tree_jueces.column("club", width=150, anchor=tk.W)
        self.tree_jueces.pack(expand=True, fill=tk.BOTH)
        self._cargar_jueces()

        # Frame para Categorías
        categorias_frame_container = ttk.LabelFrame(paned_window, text="Categorías y Parejas", padding="10")
        paned_window.add(categorias_frame_container, weight=2)

        self.tree_categorias = ttk.Treeview(categorias_frame_container, columns=("tipo_kata", "num_parejas"), height=15)
        self.tree_categorias.heading("#0", text="Nombre Categoría / Pareja", anchor=tk.W)
        self.tree_categorias.heading("tipo_kata", text="Tipo de Kata / Club", anchor=tk.W)
        self.tree_categorias.heading("num_parejas", text="Nº Parejas / ID", anchor=tk.W)
        self.tree_categorias.column("#0", width=250, minwidth=200)
        self.tree_categorias.column("tipo_kata", width=150, minwidth=100)
        self.tree_categorias.column("num_parejas", width=100, minwidth=80)
        self.tree_categorias.pack(expand=True, fill=tk.BOTH)
        self._cargar_categorias_y_parejas()

    def _cargar_jueces(self):
        for i in self.tree_jueces.get_children():
            self.tree_jueces.delete(i)
        
        jueces = self.competencia_data.get("jueces", [])
        if not jueces:
            self.tree_jueces.insert("", tk.END, values=("", "No hay jueces registrados", ""))
        else:
            for juez in jueces:
                self.tree_jueces.insert("", tk.END, values=(juez.get("id_juez", "N/A"), 
                                                            juez.get("nombre", "N/A"), 
                                                            juez.get("club", "N/A")))

    def _cargar_categorias_y_parejas(self):
        for i in self.tree_categorias.get_children():
            self.tree_categorias.delete(i)

        categorias = self.competencia_data.get("categorias", [])
        if not categorias:
            self.tree_categorias.insert("", tk.END, text="No hay categorías registradas")
        else:
            for cat_data in categorias:
                nombre_cat = cat_data.get("nombre_categoria", "Categoría sin nombre")
                tipo_kata = cat_data.get("tipo_kata", "N/A")
                parejas = cat_data.get("parejas", [])
                num_parejas_str = f"{len(parejas)} pareja(s)"

                cat_id = self.tree_categorias.insert("", tk.END, text=f"📁 {nombre_cat}", 
                                                     values=(tipo_kata, num_parejas_str), open=False)
                
                for pareja_data in parejas:
                    p1 = pareja_data.get("nombre_participante1", "N/A")
                    p2 = pareja_data.get("nombre_participante2", "N/A")
                    nombre_pareja = f"{p1} y {p2}"
                    club_pareja = pareja_data.get("club", "N/A")
                    id_pareja = pareja_data.get("id_pareja", "N/A")
                    self.tree_categorias.insert(cat_id, tk.END, text=f"    👤 {nombre_pareja}", 
                                                values=(club_pareja, id_pareja))

    def abrir_pantalla_añadir_categoria(self):
        # Aquí se llamaría a la pantalla para añadir/editar categoría
        messagebox.showinfo("Próximamente", "Pantalla para añadir categoría aún no implementada.", parent=self.top_level)
        # Ejemplo: CrearCategoriaScreen(self.top_level, self, self.competencia_path)
        # Y luego se necesitaría un método para recargar los datos y la UI: self.recargar_datos_y_ui()

    def abrir_pantalla_añadir_juez(self):
        # Aquí se llamaría a la pantalla para añadir/editar juez
        messagebox.showinfo("Próximamente", "Pantalla para añadir juez aún no implementada.", parent=self.top_level)
        # Ejemplo: CrearJuezScreen(self.top_level, self, self.competencia_path)
        # Y luego: self.recargar_datos_y_ui()

    def recargar_datos_y_ui(self):
        self._cargar_datos_competencia() # Recarga los datos del JSON
        if self.competencia_data:
            self.top_level.title(f"Torneo: {self.competencia_data.get('nombre', 'Sin Nombre')}")
            # Actualizar título en el Label si existe
            for widget in self.top_level.winfo_children(): # Buscar el main_frame
                if isinstance(widget, ttk.Frame):
                    for sub_widget in widget.winfo_children(): # Buscar el titulo_label
                        if isinstance(sub_widget, ttk.Label) and hasattr(sub_widget, 'style') and sub_widget.cget('style') == "Header.TLabel":
                            sub_widget.config(text=f"Torneo: {self.competencia_data.get('nombre', 'Desconocido')}")
                            break
                    break
            self._cargar_jueces()
            self._cargar_categorias_y_parejas()
        else:
            # Si falla la recarga, podría ser mejor cerrar o mostrar un error persistente
            messagebox.showerror("Error", "No se pudieron recargar los datos de la competencia.", parent=self.top_level)

    def cerrar_ventana(self):
        self.top_level.destroy()
        if self.admin_menu_instance and hasattr(self.admin_menu_instance, 'root') and self.admin_menu_instance.root.winfo_exists():
            self.admin_menu_instance.root.state('zoomed') # Set main window to maximized state
            self.admin_menu_instance.root.deiconify()
        elif self.root and self.root.winfo_exists(): # Fallback si admin_menu_instance no es el esperado
             self.root.deiconify()

if __name__ == "__main__":
    # Para probar esta pantalla de forma aislada
    # Crear un archivo JSON de prueba en data_storage
    test_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data_storage")
    if not os.path.exists(test_data_dir):
        os.makedirs(test_data_dir)
    
    test_competencia_file = os.path.join(test_data_dir, "competencia_prueba_torneo_screen.json")
    test_data = {
        "nombre": "Torneo de Prueba para Pantalla",
        "fecha": "2024-07-30",
        "lugar": "Gimnasio Virtual",
        "jueces": [
            {"id_juez": "J001", "nombre": "Ana Pérez", "club": "Club Sol"},
            {"id_juez": "J002", "nombre": "Luis Gómez", "club": "Club Luna"}
        ],
        "categorias": [
            {
                "nombre_categoria": "Kata Infantil", 
                "tipo_kata": "Kihon Kata", 
                "parejas": [
                    {"id_pareja": "P001", "p1_nombre": "Carlos", "p2_nombre": "Laura", "club": "Club Sol"},
                    {"id_pareja": "P002", "p1_nombre": "Pedro", "p2_nombre": "Sofía", "club": "Club Luna"}
                ]
            },
            {
                "nombre_categoria": "Kata Adultos", 
                "tipo_kata": "Nage No Kata", 
                "parejas": [
                    {"id_pareja": "P003", "p1_nombre": "Miguel", "p2_nombre": "Elena", "club": "Club Estrella"}
                ]
            }
        ]
    }
    with open(test_competencia_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=4, ensure_ascii=False)

    root_test = tk.Tk()
    # root_test.withdraw() # Ocultar la ventana raíz si se va a mostrar solo el Toplevel
    # Para que el Toplevel funcione correctamente, la raíz no debe estar oculta inmediatamente si es la única ventana.
    # O, si se oculta, asegurarse de que el mainloop se maneje correctamente.
    
    # Simular que admin_menu_instance es la ventana raíz para el deiconify
    class MockAdminMenu:
        def __init__(self, r):
            self.root = r

    mock_admin = MockAdminMenu(root_test)
    app = TorneoScreen(root_test, mock_admin, test_competencia_file)
    root_test.mainloop()