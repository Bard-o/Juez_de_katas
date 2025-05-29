import tkinter as tk
from tkinter import ttk, messagebox
import os
import json

DATA_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data_storage")

class JuezLoginScreen:
    def __init__(self, root):
        self.root = root
        self.top_level = tk.Toplevel(root)
        self.top_level.title("Login de Juez - Seleccionar Juez")
        self.top_level.state('zoomed')
        self.top_level.grab_set()
        self.top_level.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)

        self.selected_juez_info = None

        # Estilos
        style = ttk.Style(self.top_level)
        style.configure("Header.TLabel", font=('Helvetica', 16, 'bold'), background="#ffffff")
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        style.configure("TButton", padding=10, font=('Helvetica', 10))
        style.configure("Background.TFrame", background="#dadada") # Fondo general de la ventana
        style.configure("Content.TFrame", background="#ffffff") # Fondo del cuadro de contenido

        # Frame principal expansible con fondo #dadada
        main_frame_expansible = ttk.Frame(self.top_level, style="Background.TFrame")
        main_frame_expansible.pack(fill=tk.BOTH, expand=True)
        main_frame_expansible.grid_rowconfigure(0, weight=1)
        main_frame_expansible.grid_columnconfigure(0, weight=1)

        # Contenedor para el contenido real, centrado y con fondo blanco
        content_width = 800 
        content_height = 550 # Ajustado para mejor visualización del treeview y botón

        content_container = ttk.Frame(main_frame_expansible, style="Content.TFrame", padding="20", width=content_width, height=content_height)
        content_container.grid(row=0, column=0, sticky="") # Centrado por defecto
        content_container.grid_propagate(False) # Evitar que el frame cambie de tamaño con el contenido
        
        content_container.columnconfigure(0, weight=1)
        content_container.rowconfigure(0, weight=0) # Título
        content_container.rowconfigure(1, weight=1) # Treeview
        content_container.rowconfigure(2, weight=0) # Botones

        # Título dentro del content_container
        titulo_label = ttk.Label(content_container, text="Bienvenido al Sistema de Juzgamiento", style="Header.TLabel")
        titulo_label.grid(row=0, column=0, pady=(20, 30), sticky="n")

        # Treeview para competencias y jueces, dentro del content_container
        tree_frame = ttk.Frame(content_container, style="Content.TFrame") 
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0,10))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=("id_juez", "club_juez"), show="headings") # Modificado
        self.tree.heading("#0", text="Competencia / Juez") # Columna implícita para el texto del item
        self.tree.heading("id_juez", text="ID Juez")
        # self.tree.heading("nombre_juez", text="Nombre Juez") # Eliminado
        self.tree.heading("club_juez", text="Club Juez")

        # Configurar la primera columna (jerárquica) para que use el espacio restante
        self.tree.column("#0", width=350, stretch=tk.YES) # Ajustado ancho
        self.tree.column("id_juez", width=100, stretch=tk.NO)
        # self.tree.column("nombre_juez", width=200, stretch=tk.NO) # Eliminado
        self.tree.column("club_juez", width=150, stretch=tk.NO)
        
        # Cambiar show a 'tree headings' para mostrar la columna jerárquica y las otras
        self.tree.config(show='tree headings')

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.cargar_competencias_y_jueces()

        # Botones, dentro del content_container
        botones_frame = ttk.Frame(content_container, style="Content.TFrame")
        botones_frame.grid(row=2, column=0, sticky="s", pady=(10,20))

        btn_seleccionar = ttk.Button(botones_frame, text="Seleccionar Juez e Ingresar", command=self.seleccionar_juez)
        btn_seleccionar.pack(pady=5)

        self.tree.bind("<Double-1>", lambda event: self.seleccionar_juez()) 

    def cargar_competencias_y_jueces(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        if not os.path.exists(DATA_STORAGE_PATH):
            messagebox.showwarning("Directorio no encontrado", f"El directorio {DATA_STORAGE_PATH} no existe.", parent=self.top_level)
            return

        archivos_json = [f for f in os.listdir(DATA_STORAGE_PATH) if f.endswith('.json')]

        if not archivos_json:
            self.tree.insert("", tk.END, text="No hay competencias disponibles.", values=("", "")) # Modificado
            return

        for nombre_archivo in archivos_json:
            ruta_archivo = os.path.join(DATA_STORAGE_PATH, nombre_archivo)
            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    data_competencia = json.load(f)
                
                nombre_competencia = data_competencia.get("nombre", "Competencia sin nombre")
                comp_id = self.tree.insert("", tk.END, text=f"📁 {nombre_competencia}", open=False, values=("-", "-")) # Modificado

                jueces = data_competencia.get("jueces", [])
                if jueces:
                    for juez in jueces:
                        id_juez = juez.get("id_juez", "N/A")
                        nombre_juez = juez.get("nombre", "N/A") # Se mantiene para el texto del item y datos
                        club_juez = juez.get("club", "N/A")
                        # Guardar ruta del archivo y datos del juez para fácil acceso
                        self.tree.insert(comp_id, tk.END, text=f"    👤 {nombre_juez}", 
                                         values=(id_juez, club_juez), # Modificado
                                         tags=(ruta_archivo, id_juez, nombre_juez)) # Añadido nombre_juez a tags para recuperarlo
                else:
                    self.tree.insert(comp_id, tk.END, text="    (No hay jueces en esta competencia)", values=("", "")) # Modificado

            except json.JSONDecodeError:
                print(f"Error al decodificar JSON en: {nombre_archivo}")
                self.tree.insert("", tk.END, text=f"Error al leer {nombre_archivo}", values=("", "")) # Modificado
            except Exception as e:
                print(f"Error al procesar {nombre_archivo}: {e}")
                self.tree.insert("", tk.END, text=f"Error con {nombre_archivo}", values=("", "")) # Modificado

    def seleccionar_juez(self):
        seleccion = self.tree.focus() # Obtiene el item seleccionado
        if not seleccion:
            messagebox.showwarning("Sin selección", "Por favor, seleccione un juez de la lista.", parent=self.top_level)
            return

        item_data = self.tree.item(seleccion)
        item_tags = item_data.get('tags')
        item_values = item_data.get('values')

        # Un juez es un hijo de una competencia, y tendrá tags
        # Ahora tags tiene (ruta_competencia, id_juez_seleccionado, nombre_juez_seleccionado)
        if item_tags and len(item_tags) == 3 and item_values and item_values[0] != "-":
            ruta_competencia, id_juez_seleccionado, nombre_juez_seleccionado = item_tags
            # club_juez_seleccionado se obtiene de item_values
            club_juez_seleccionado = item_values[1] # Ajustado índice
            
            self.selected_juez_info = {
                "ruta_competencia": ruta_competencia,
                "id_juez": id_juez_seleccionado,
                "nombre_juez": nombre_juez_seleccionado,
                "club_juez": club_juez_seleccionado
            }
            messagebox.showinfo("Juez Seleccionado", 
                                f"Juez: {nombre_juez_seleccionado}\nID: {id_juez_seleccionado}\nClub: {club_juez_seleccionado}\nCompetencia: {os.path.basename(ruta_competencia)}", 
                                parent=self.top_level)
            # Aquí se abriría la siguiente pantalla para el juez
            # Por ahora, cerramos esta y podríamos pasar self.selected_juez_info
            self.abrir_menu_principal_juez()
        else:
            messagebox.showwarning("Selección Inválida", "Por favor, seleccione un juez específico, no una competencia.", parent=self.top_level)

    def abrir_menu_principal_juez(self):
        if self.selected_juez_info:
            # Importar JuezMainScreen aquí para evitar dependencia circular a nivel de módulo si fuera el caso
            # y porque solo se necesita en este punto.
            from .juez_main_screen import JuezMainScreen 
            self.top_level.withdraw() # Ocultar la pantalla de login
            JuezMainScreen(self.root, self.selected_juez_info, self) # Pasar self como login_screen_instance
        else:
            messagebox.showerror("Error", "No se ha seleccionado ningún juez para continuar.", parent=self.top_level)

    def cerrar_ventana(self):
        self.top_level.destroy()
        # Si esta pantalla fue llamada desde otra, se podría reactivar la anterior
        # if self.calling_instance:
        #     self.calling_instance.reactivate()
        # Si esta ventana se cierra (ej. por la 'X'), y es la que maneja la app principal, cerrar todo.
        if self.root.winfo_exists(): # Asegurarse que la raíz existe
             self.root.destroy() 

    def reactivate_login_screen(self):
        """Método para ser llamado por JuezMainScreen al cerrar sesión."""
        self.top_level.deiconify()
        self.top_level.state('zoomed')
        self.top_level.grab_set()
        self.selected_juez_info = None # Resetear selección
        # Opcional: recargar jueces si pudieran haber cambiado, aunque no es común desde el menú de juez.
        # self.cargar_competencias_y_jueces()

if __name__ == '__main__':
    # Crear el directorio data_storage si no existe para pruebas
    if not os.path.exists(DATA_STORAGE_PATH):
        os.makedirs(DATA_STORAGE_PATH)
        print(f"Directorio '{DATA_STORAGE_PATH}' creado para pruebas.")
        # Crear algunos archivos JSON de ejemplo para probar
        ejemplo_comp1 = {
            "nombre": "Torneo de Primavera",
            "fecha": "2024-05-10",
            "lugar": "Gimnasio Central",
            "jueces": [
                {"id_juez": "J001", "nombre": "Ana Pérez", "club": "Club Sol Naciente"},
                {"id_juez": "J002", "nombre": "Luis García", "club": "Dojo Imperial"}
            ],
            "categorias": []
        }
        ejemplo_comp2 = {
            "nombre": "Copa Invierno",
            "fecha": "2024-11-20",
            "lugar": "Estadio Norte",
            "jueces": [
                {"id_juez": "J003", "nombre": "Sofia Torres", "club": "Academia Bushido"}
            ],
            "categorias": []
        }
        with open(os.path.join(DATA_STORAGE_PATH, "torneo_primavera.json"), 'w', encoding='utf-8') as f:
            json.dump(ejemplo_comp1, f, indent=4)
        with open(os.path.join(DATA_STORAGE_PATH, "copa_invierno.json"), 'w', encoding='utf-8') as f:
            json.dump(ejemplo_comp2, f, indent=4)
        with open(os.path.join(DATA_STORAGE_PATH, "torneo_sin_jueces.json"), 'w', encoding='utf-8') as f:
            json.dump({"nombre": "Torneo Vacío", "jueces": []}, f, indent=4)

    root_test = tk.Tk()
    root_test.withdraw()  # Ocultar la ventana raíz principal de Tkinter
    app = JuezLoginScreen(root_test)
    root_test.mainloop()