# src/core/juez.py

class Juez:
    def __init__(self, id_juez: str, nombre: str, club: str):
        self.id_juez = id_juez
        self.nombre = nombre
        self.club = club

    def __str__(self):
        return f"Juez ID: {self.id_juez}, Nombre: {self.nombre}, Club: {self.club}"