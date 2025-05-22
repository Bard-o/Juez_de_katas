import tkinter as tk
from tkinter import ttk
from .crear_competencia_screen import CrearCompetenciaScreen
from .lista_competencias_screen import ListaCompetenciasScreen

class AdminMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal - Administrador")
        self.root.geometry("800x600")

        # Configurar el estilo para los botones
        style = ttk.Style()
        style.configure("TButton", padding=10, font=('Helvetica', 12))
        style.configure("Title.TLabel", font=('Helvetica', 18, 'bold'))

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Título centrado
        titulo_label = ttk.Label(main_frame, text="Bienvenido al Sistema de Juzgamiento", style="Title.TLabel")
        titulo_label.pack(pady=(20, 40))

        # Frame para los botones, para centrarlos
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(expand=True)

        # Botón "Crear competencia nuevo"
        btn_crear = ttk.Button(botones_frame, text="Crear Competencia Nueva", 
                               command=self.abrir_crear_competencia, style="TButton", width=30)
        btn_crear.pack(pady=20)

        # Botón "Abrir Competencia existente"
        btn_abrir = ttk.Button(botones_frame, text="Abrir Competencia Existente", 
                               command=self.abrir_lista_competencias, style="TButton", width=30)
        btn_abrir.pack(pady=20)

    def abrir_crear_competencia(self):
        self.root.withdraw() # Ocultar la ventana principal
        CrearCompetenciaScreen(self.root, self) # Pasar self.root y la instancia actual
        # La ventana CrearCompetenciaScreen se encargará de volver a mostrar el menú principal al cerrarse.

    def abrir_lista_competencias(self):
        self.root.withdraw() # Ocultar la ventana principal
        ListaCompetenciasScreen(self.root, self) # Pasar self.root y la instancia actual
        # La ventana ListaCompetenciasScreen se encargará de volver a mostrar el menú principal al cerrarse.

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminMenu(root)
    root.mainloop()