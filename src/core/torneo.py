class Torneo:
    def __init__(self, nombre: str, fecha: str, lugar: str):
        self.nombre = nombre
        self.fecha = fecha
        self.lugar = lugar
        self.categorias = []
        self.jueces = []

    def agregar_categoria(self, categoria):
        self.categorias.append(categoria)
        print(f"Categoría '{categoria.nombre_categoria}' agregada al torneo '{self.nombre}'.")

    def agregar_juez(self, juez):
        self.jueces.append(juez)
        print(f"Juez '{juez.nombre}' agregado al torneo '{self.nombre}'.")

    def __str__(self):
        return f"Torneo: {self.nombre}, Fecha: {self.fecha}, Lugar: {self.lugar}"

# Implementación del patrón Factory para Torneo
class TorneoFactory:
    @staticmethod
    def crear_torneo(tipo: str, fecha: str, lugar: str):
        if tipo.lower() == "regional":
            return Torneo("Torneo Regional", fecha, lugar)
        elif tipo.lower() == "nacional":
            return Torneo("Torneo Nacional", fecha, lugar)
        elif tipo.lower() == "internacional":
            return Torneo("Torneo Internacional", fecha, lugar)
        else:
            raise ValueError("Tipo de torneo desconocido")