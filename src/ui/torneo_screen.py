import tkinter as tk
from tkinter import ttk, messagebox
from .crear_juez_screen import CrearJuezScreen
from .crear_pareja_screen import CrearParejaScreen # Nueva importación # Importar la nueva pantalla
from .crear_categoria_screen import CrearCategoriaScreen # Importar la pantalla de crear categoría
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

        style.configure("Dark.TFrame", background="#dadada") # Gris oscuro
        
        
        main_frame_expansible.columnconfigure(0, weight=1)
        main_frame_expansible.rowconfigure(0, weight=1)
        
        
        content_container = ttk.Frame(main_frame_expansible, padding="20", width=900) # Ancho deseado
        content_container.grid(row=0, column=0, sticky="") # Centrado

       
        titulo_label = ttk.Label(content_container, text=f"Torneo: {self.competencia_data.get('nombre', 'Desconocido')}", style="Header.TLabel")
        titulo_label.pack(pady=(0, 20))

       
        botones_frame = ttk.Frame(content_container)
        botones_frame.pack(fill=tk.X, pady=(0, 10))

        btn_add_pareja = ttk.Button(botones_frame, text="Añadir Pareja", command=self.abrir_pantalla_añadir_pareja)
        btn_add_pareja.pack(side=tk.LEFT, padx=(0, 10))

        btn_add_categoria = ttk.Button(botones_frame, text="Añadir Categoría", command=self.abrir_pantalla_añadir_categoria)
        btn_add_categoria.pack(side=tk.LEFT, padx=(0, 10))

        btn_add_juez = ttk.Button(botones_frame, text="Añadir Juez", command=self.abrir_pantalla_añadir_juez)
        btn_add_juez.pack(side=tk.LEFT)



        self.btn_ver_resultados = ttk.Button(botones_frame, text="Ver Resultados de Categoría", command=self.abrir_pantalla_resultados_categoria, state=tk.DISABLED)
        self.btn_ver_resultados.pack(side=tk.RIGHT)

        # PanedWindow para dividir Jueces y Categorías - ahora dentro de content_container
        paned_window = ttk.PanedWindow(content_container, orient=tk.HORIZONTAL)
        # El paned_window se expandirá gracias a la configuración de row/columnconfigure en content_container
        paned_window.pack(expand=True, fill=tk.BOTH, pady=(10,0)) # Quitado padding inferior, se maneja con el frame de botones

        # Frame para el botón de volver - ahora dentro de content_container
        bottom_frame = ttk.Frame(content_container)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        btn_volver = ttk.Button(bottom_frame, text="Volver al Menú Principal", command=self.cerrar_ventana)
        btn_volver.pack(side=tk.LEFT)

        
        content_container.rowconfigure(2, weight=1) 
        content_container.columnconfigure(0, weight=1) 


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

        # Bind selection event to enable/disable the results button
        self.tree_categorias.bind("<<TreeviewSelect>>", self._on_categoria_select)



    def _cargar_jueces(self):
        for i in self.tree_jueces.get_children():
            self.tree_jueces.delete(i)
        
        jueces = self.competencia_data["jueces"] if self.competencia_data else []
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

        categorias = self.competencia_data["categorias"] if self.competencia_data else []
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
                                                values=(club_pareja, id_pareja), tags=('pareja',))

    def abrir_pantalla_añadir_categoria(self):
        # Llama a la pantalla para añadir categoría
        CrearCategoriaScreen(self.top_level, self, self.competencia_path)
        # La recarga de datos y UI se maneja desde CrearCategoriaScreen al guardar exitosamente.

    def abrir_pantalla_añadir_pareja(self):
        # Llama a la pantalla para añadir pareja
        CrearParejaScreen(self.top_level, self, self.competencia_path)
        # La recarga de datos y UI se maneja desde CrearParejaScreen al guardar exitosamente.

    def abrir_pantalla_añadir_juez(self):
        # Llama a la pantalla para añadir/editar juez
        CrearJuezScreen(self.top_level, self, self.competencia_path)
        # La recarga de datos y UI se maneja desde CrearJuezScreen al guardar exitosamente.

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

    def _on_categoria_select(self, event):
        selected_item = self.tree_categorias.focus()
        if selected_item:
            # Check if the selected item is a category (not a pair)
            item_tags = self.tree_categorias.item(selected_item, "tags")
            if 'pareja' not in item_tags:
                self.btn_ver_resultados.config(state=tk.NORMAL)
            else:
                self.btn_ver_resultados.config(state=tk.DISABLED)
        else:
            self.btn_ver_resultados.config(state=tk.DISABLED)

    def abrir_pantalla_resultados_categoria(self):
        selected_item = self.tree_categorias.focus()
        if not selected_item:
            messagebox.showwarning("Selección Requerida", "Por favor, seleccione una categoría para ver sus resultados.", parent=self.top_level)
            return

        # Get the category data
        category_id = selected_item
        category_name = self.tree_categorias.item(category_id, "text").replace("📁 ", "")
        category_type_kata = self.tree_categorias.item(category_id, "values")[0]

        selected_category_data = None
        for cat_data in self.competencia_data["categorias"] if self.competencia_data else []:
            if cat_data.get("nombre_categoria") == category_name and cat_data.get("tipo_kata") == category_type_kata:
                selected_category_data = cat_data
                break

        if selected_category_data:
            # Import and open the new results screen
            from .resultados_categoria_screen import ResultadosCategoriaScreen
            ResultadosCategoriaScreen(self.top_level, self.admin_menu_instance, self.competencia_path, selected_category_data)
            self.top_level.withdraw() # Hide current window
        else:
            messagebox.showerror("Error", "No se pudo encontrar los datos de la categoría seleccionada.", parent=self.top_level)

