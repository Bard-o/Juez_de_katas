import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class JuezMainScreen:
    def __init__(self, root, juez_info, login_screen_instance):
        self.root = root
        self.juez_info = juez_info  
        self.login_screen_instance = login_screen_instance
        self.competencia_data = None
        self.selected_pareja_info = None

        self.top_level = tk.Toplevel(root)
        self.top_level.title(f"Juez: {self.juez_info['nombre_juez']} - Menú Principal")
        self.top_level.state('zoomed')
        self.top_level.grab_set()
        self.top_level.protocol("WM_DELETE_WINDOW", self.cerrar_y_volver_a_login)

        self._cargar_datos_competencia()
        self._crear_interfaz()

    def _cargar_datos_competencia(self):
        try:
            with open(self.juez_info['ruta_competencia'], 'r', encoding='utf-8') as f:
                self.competencia_data = json.load(f)
            if not self.competencia_data:
                messagebox.showerror("Error", "No se pudieron cargar los datos de la competencia.", parent=self.top_level)
                self.cerrar_y_volver_a_login()
        except Exception as e:
            messagebox.showerror("Error al Cargar Competencia", f"No se pudo cargar el archivo: {e}", parent=self.top_level)
            self.cerrar_y_volver_a_login()

    def _crear_interfaz(self):
        if not self.competencia_data:
            return

        style = ttk.Style(self.top_level)
        style.configure("Header.TLabel", font=('Helvetica', 16, 'bold'))
        style.configure("SubHeader.TLabel", font=('Helvetica', 12, 'italic'))
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Dark.TFrame", background="#dadada") # Fondo gris oscuro
        style.configure("Content.TFrame", background="#ffffff") # Fondo gris claro para el contenido

        # Frame principal expansible con fondo oscuro
        main_frame_expansible = ttk.Frame(self.top_level, style="Dark.TFrame")
        main_frame_expansible.pack(fill=tk.BOTH, expand=True)
        main_frame_expansible.columnconfigure(0, weight=1)
        main_frame_expansible.rowconfigure(0, weight=1)

        # Contenedor para el contenido real, centrado y con fondo claro
        content_container = ttk.Frame(main_frame_expansible, style="Content.TFrame", padding="20", width=900, height=600)
        content_container.grid(row=0, column=0, sticky="") # Centrado
        content_container.columnconfigure(0, weight=1)
        content_container.rowconfigure(2, weight=1) # Para que el treeview se expanda

        # Información del Juez y Torneo
        info_frame = ttk.Frame(content_container, style="Content.TFrame")
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        info_frame.columnconfigure(0, weight=1)

        titulo_label = ttk.Label(info_frame, text=f"Juez: {self.juez_info['nombre_juez']} ({self.juez_info['id_juez']}) - Club: {self.juez_info['club_juez']}", style="Header.TLabel", background="#ffffff")
        titulo_label.pack()
        subtitulo_label = ttk.Label(info_frame, text=f"Torneo: {self.competencia_data.get('nombre', 'N/A')}", style="SubHeader.TLabel", background="#ffffff")
        subtitulo_label.pack()

        # Treeview para categorías y parejas
        tree_label = ttk.Label(content_container, text="Seleccione una pareja para evaluar:", font=('Helvetica', 11), background="#ffffff")
        tree_label.grid(row=1, column=0, sticky="w", pady=(0,5))

        tree_frame = ttk.Frame(content_container) # No necesita estilo Content.TFrame si el content_container ya lo tiene
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("id_pareja", "participantes", "club_pareja"), show="headings")
        # Configuración de las columnas del Treeview
        # La primera columna (#0) es implícita y se usa para el texto del item (nombre de categoría o pareja)
        self.tree.heading("id_pareja", text="ID Pareja")
        self.tree.heading("participantes", text="Participantes")
        self.tree.heading("club_pareja", text="Club")

        self.tree.column("#0", width=250, stretch=tk.YES, anchor="w") # Para Categoría/Pareja (texto principal)
        self.tree.column("id_pareja", width=100, stretch=tk.NO, anchor="center")
        self.tree.column("participantes", width=250, stretch=tk.YES, anchor="w")
        self.tree.column("club_pareja", width=150, stretch=tk.NO, anchor="w")
        self.tree.config(show='tree headings') # Muestra el árbol y las cabeceras

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._cargar_categorias_y_parejas_tree()

        # Botones
        botones_frame = ttk.Frame(content_container, style="Content.TFrame")
        botones_frame.grid(row=3, column=0, sticky="ew", pady=(20,0))
        botones_frame.columnconfigure(0, weight=1) # Para centrar botones o expandirlos

        btn_seleccionar = ttk.Button(botones_frame, text="Evaluar Pareja Seleccionada", command=self.confirmar_seleccion_pareja)
        btn_seleccionar.pack(side=tk.RIGHT, padx=(0,5))
        btn_logout = ttk.Button(botones_frame, text="Cerrar Sesión", command=self.cerrar_y_volver_a_login)
        btn_logout.pack(side=tk.RIGHT, padx=(5,0))

        self.tree.bind("<Double-1>", lambda event: self.confirmar_seleccion_pareja())

    def _cargar_categorias_y_parejas_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        categorias = self.competencia_data["categorias"] if self.competencia_data else []
        if not categorias:
            self.tree.insert("", tk.END, text="No hay categorías en este torneo.", values=("", "", ""))
            return

        for cat_data in categorias:
            nombre_cat = cat_data.get("nombre_categoria", "Categoría sin nombre")
            tipo_kata_cat = cat_data.get("tipo_kata", "N/A") # Tipo de kata de la categoría
            # Insertar categoría como nodo padre. El texto principal es el nombre de la categoría.
            # Las 'values' para la categoría pueden ser informativas o dejarse vacías si no aplican a las columnas de pareja.
            cat_id_tree = self.tree.insert("", tk.END, text=f"📁 {nombre_cat} ({tipo_kata_cat})", open=True, values=("-", "-", "-"))

            parejas = cat_data.get("parejas", [])
            if parejas:
                for pareja_data in parejas:
                    p1 = pareja_data.get("nombre_participante1", "N/A")
                    p2 = pareja_data.get("nombre_participante2", "N/A")
                    id_pareja = pareja_data.get("id_pareja", "N/A")
                    club_pareja = pareja_data.get("club", "N/A")
                    participantes_str = f"{p1} y {p2}"
                    
                    # Insertar pareja como hijo de la categoría.
                    # El texto principal del item de pareja puede ser su ID o los nombres.
                    # Las 'values' corresponden a las columnas definidas: ID Pareja, Participantes, Club.
                    self.tree.insert(cat_id_tree, tk.END, 
                                     text=f"    👤 Pareja ID: {id_pareja}", # Texto principal del item de pareja
                                     values=(id_pareja, participantes_str, club_pareja),
                                     tags=(nombre_cat, tipo_kata_cat, id_pareja, p1, p2, club_pareja, self.juez_info['ruta_competencia'])) # Añadir ruta_competencia a tags
            else:
                self.tree.insert(cat_id_tree, tk.END, text="    (No hay parejas en esta categoría)", values=("-", "-", "-"), tags=("no_pareja"))

    def confirmar_seleccion_pareja(self):
        seleccion = self.tree.focus()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Por favor, seleccione una pareja para evaluar.", parent=self.top_level)
            return

        item_data = self.tree.item(seleccion)
        item_tags = item_data.get('tags')
        # item_values ahora son (id_pareja, participantes_str, club_pareja)

        # Verificar que se seleccionó una pareja (no una categoría o un item de 'no hay parejas')
        if item_tags and "no_pareja" not in item_tags and len(item_tags) == 7:
            nombre_cat, tipo_kata_cat, id_pareja, p1, p2, club_pareja, ruta_competencia = item_tags
            
            self.selected_pareja_info = {
                "nombre_categoria": nombre_cat,
                "tipo_kata_categoria": tipo_kata_cat, # Tipo de kata de la categoría
                "id_pareja": id_pareja,
                "nombre_participante1": p1,
                "nombre_participante2": p2,
                "club": club_pareja,
                "juez_info": self.juez_info, # Información del juez logueado
                "ruta_competencia": ruta_competencia
            }

            msg = (f"¿Desea proceder a evaluar a la pareja?\n\n"
                   f"Categoría: {nombre_cat} ({tipo_kata_cat})\n"
                   f"Pareja ID: {id_pareja}\n"
                   f"Participantes: {p1} y {p2}\n"
                   f"Club: {club_pareja}")
            
            respuesta = messagebox.askyesno("Confirmar Selección", msg, parent=self.top_level)
            if respuesta:
                self.abrir_pantalla_evaluacion()
        else:
            messagebox.showwarning("Selección Inválida", "Por favor, seleccione una pareja específica, no una categoría o un placeholder.", parent=self.top_level)

    def abrir_pantalla_evaluacion(self):
        if self.selected_pareja_info:
            # Importar EvaluacionKataScreen aquí para evitar dependencias circulares a nivel de módulo
            # y porque solo se necesita en este punto.
            from .evaluacion_kata_screen import EvaluacionKataScreen
            self.top_level.withdraw() # Ocultar la pantalla principal del juez
            EvaluacionKataScreen(self.root, self.selected_pareja_info, self) # Pasar self como juez_main_screen_instance
        else:
            messagebox.showerror("Error", "No hay información de pareja seleccionada para continuar.", parent=self.top_level)

    def cerrar_y_volver_a_login(self):
        self.top_level.destroy()
        if self.login_screen_instance and hasattr(self.login_screen_instance, 'top_level') and self.login_screen_instance.top_level.winfo_exists():
            self.login_screen_instance.top_level.deiconify()
            self.login_screen_instance.top_level.state('zoomed')
        else: # Si la pantalla de login ya no existe, cerrar la app
            self.root.destroy()

    def reactivate(self):
        """Método para ser llamado por la pantalla de evaluación al cerrarse."""
        self.top_level.deiconify()
        self.top_level.state('zoomed')
        self.top_level.grab_set()
        self.selected_pareja_info = None # Resetear selección
        self._cargar_categorias_y_parejas_tree() # Recargar por si hubo cambios


