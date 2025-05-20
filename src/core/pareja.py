# src/core/pareja.py
import uuid

class Pareja:
    def __init__(self, id_pareja: str, nombre_participante1: str, nombre_participante2: str, club: str):
        self.id_pareja = id_pareja  # Asignar ID proporcionado
        self.nombre_participante1 = nombre_participante1
        self.nombre_participante2 = nombre_participante2
        self.club = club
        self.puntaje_total = 0
        self.errores_tecnicas = {}

    def __str__(self):
        return f"Pareja ID: {self.id_pareja}, Participantes: {self.nombre_participante1} y {self.nombre_participante2}, Club: {self.club}"