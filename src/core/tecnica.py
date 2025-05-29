# src/core/tecnica.py

class Tecnica:
    def __init__(self, nombre_tecnica: str, puntaje_base: float = 10.0):
        self.nombre_tecnica = nombre_tecnica
        self.puntaje_base = puntaje_base
        self.errores_por_juez = {}

    def registrar_evaluacion_juez(self, id_juez: str, errores: dict, compensacion: float):
        """
        Registra la evaluación de un juez para esta técnica.
        errores = {'pequeno': int, 'mediano': int, 'grande': int, 'olvidada': bool}
        compensacion = float
        """
        self.errores_por_juez[id_juez] = {
            'pequeno': errores.get('pequeno', 0),
            'mediano': errores.get('mediano', 0),
            'grande': errores.get('grande', 0),
            'olvidada': errores.get('olvidada', False),
            'compensacion': compensacion
        }

    def calcular_puntaje_juez(self, id_juez: str) -> float:
        if id_juez not in self.errores_por_juez:
            return 0.0 # O manejar como error

        evaluacion = self.errores_por_juez[id_juez]
        puntaje = self.puntaje_base

        if evaluacion['olvidada']:
            return 0.0

        puntaje -= evaluacion['pequeno'] * 1
        puntaje -= evaluacion['mediano'] * 3
        puntaje -= evaluacion['grande'] * 5
        puntaje += evaluacion['compensacion']

        return max(0, puntaje) # El puntaje no puede ser negativo

    def __str__(self):
        return f"Técnica: {self.nombre_tecnica}, Puntaje Base: {self.puntaje_base}"