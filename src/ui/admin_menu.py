import tkinter as tk
from tkinter import ttk
from .crear_competencia_screen import CrearCompetenciaScreen
from .lista_competencias_screen import ListaCompetenciasScreen

class AdminMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal - Administrador")
        self.root.state('zoomed') # Maximizar la ventana

        # Configurar el estilo para los botones
        style = ttk.Style()
        style.configure("TButton", padding=10, font=('Helvetica', 12))
        style.configure("Title.TLabel", font=('Helvetica', 18, 'bold'))

        # Frame principal que se expande con la ventana
        main_frame_expansible = ttk.Frame(self.root, style="Dark.TFrame") # Aplicar estilo para el fondo
        main_frame_expansible.pack(fill=tk.BOTH, expand=True)

        # Estilo para el frame principal oscuro
        style.configure("Dark.TFrame", background="#dadada") # Gris oscuro
        
        # Configurar el grid del frame expansible para centrar el content_container
        main_frame_expansible.columnconfigure(0, weight=1)
        main_frame_expansible.rowconfigure(0, weight=1)
        
        # Contenedor para el contenido real, con un ancho máximo
        content_container = ttk.Frame(main_frame_expansible, padding="20 20 20 20", width=700) # Ancho deseado
        content_container.grid(row=0, column=0, sticky="") # Centrado

        # Título centrado - ahora dentro de content_container
        titulo_label = ttk.Label(content_container, text="Bienvenido al Sistema de Juzgamiento", style="Title.TLabel")
        titulo_label.pack(pady=(20, 40))

        # Frame para los botones, para centrarlos - ahora dentro de content_container
        botones_frame = ttk.Frame(content_container)
        botones_frame.pack(expand=True) # Se expandirá dentro del content_container

        # Botón "Crear competencia nuevo"
        btn_crear = ttk.Button(botones_frame, text="Crear Competencia Nueva", 
                               command=self.abrir_crear_competencia, style="TButton", width=30)
        btn_crear.pack(pady=20)

        # Botón "Abrir Competencia existente"
        btn_abrir = ttk.Button(botones_frame, text="Abrir Competencia Existente", 
                               command=self.abrir_lista_competencias, style="TButton", width=30)
        btn_abrir.pack(pady=20)


        content_container.columnconfigure(0, weight=1) 
        

    def abrir_crear_competencia(self):
        self.root.withdraw() # Ocultar la ventana principal
        CrearCompetenciaScreen(self.root, self) 

    def abrir_lista_competencias(self):
        self.root.withdraw() # Ocultar la ventana principal
        ListaCompetenciasScreen(self.root, self) 

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminMenu(root)
    root.mainloop()