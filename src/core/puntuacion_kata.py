# src/core/puntuacion_kata.py
from typing import List, Dict
from .tecnica import Tecnica
from .pareja import Pareja
from .juez import Juez

class PuntuacionKata:
    def __init__(self, pareja: Pareja, tecnicas_kata: List[Tecnica], evaluaciones_jueces: Dict[str, List[Dict]]):
        """
        Inicializa la puntuación de una kata para una pareja.
        pareja: Objeto Pareja que realiza la kata.
        tecnicas_kata: Lista de objetos Tecnica que componen la kata.
        evaluaciones_jueces: Un diccionario donde las claves son id_juez y los valores son listas de evaluaciones por técnica.
                             Cada evaluación es un diccionario {'errores': dict, 'compensacion': float}
                             Ejemplo: {'juez1': [{'errores': {'pequeno':1}, 'compensacion':0.5}, ...], ...}
        """
        self.pareja = pareja
        self.tecnicas_kata = tecnicas_kata # Lista de nombres o IDs de técnicas
        self.evaluaciones_jueces = evaluaciones_jueces # {id_juez: [{errores_tecnica_1}, {errores_tecnica_2}, ...]}
        self.puntajes_por_tecnica_final = [] # Almacenará los puntajes finales de cada técnica
        self.puntaje_total_kata = 0
        self.errores_totales_por_tecnica = [] # [{nombre_tecnica: '', errores: {'pequeno':0,...}},...]

    def calcular_puntajes_tecnicas(self):
        """
        Calcula el puntaje para cada técnica de la kata, descartando el más alto y el más bajo de los jueces.
        """
        self.puntajes_por_tecnica_final = []
        self.errores_totales_por_tecnica = []

        for i, tecnica_base in enumerate(self.tecnicas_kata):
            puntajes_jueces_tecnica = []
            errores_acumulados_tecnica = {'pequeno': 0, 'mediano': 0, 'grande': 0, 'olvidada': 0}

            for id_juez, evaluaciones_del_juez in self.evaluaciones_jueces.items():
                if i < len(evaluaciones_del_juez):
                    evaluacion_tecnica_actual = evaluaciones_del_juez[i]
                    # Usamos una instancia temporal de Tecnica para calcular el puntaje de este juez para esta técnica
                    temp_tecnica = Tecnica(tecnica_base.nombre_tecnica, tecnica_base.puntaje_base)
                    temp_tecnica.registrar_evaluacion_juez(id_juez, evaluacion_tecnica_actual['errores'], evaluacion_tecnica_actual['compensacion'])
                    puntaje_juez = temp_tecnica.calcular_puntaje_juez(id_juez)
                    puntajes_jueces_tecnica.append(puntaje_juez)

                    # Acumular errores
                    errores_eval = evaluacion_tecnica_actual['errores']
                    errores_acumulados_tecnica['pequeno'] += errores_eval.get('pequeno', 0)
                    errores_acumulados_tecnica['mediano'] += errores_eval.get('mediano', 0)
                    errores_acumulados_tecnica['grande'] += errores_eval.get('grande', 0)
                    if errores_eval.get('olvidada', False):
                        errores_acumulados_tecnica['olvidada'] += 1
                else:
                    # Si un juez no evaluó todas las técnicas, se podría manejar aquí (ej. puntaje 0 o error)
                    puntajes_jueces_tecnica.append(0) # Asumimos 0 si no hay evaluación

            # Descartar el puntaje más alto y el más bajo si hay suficientes jueces (ej. 5 jueces)
            # Para este ejemplo, asumimos que siempre hay 5 jueces según el requerimiento.
            # Si hay menos de 3 jueces después del descarte, la lógica podría necesitar ajuste.
            if len(puntajes_jueces_tecnica) >= 3:
                puntajes_jueces_tecnica.sort()
                puntajes_validos = puntajes_jueces_tecnica[1:-1] # Descarta el primero y el último
            else:
                puntajes_validos = puntajes_jueces_tecnica # No se descarta si hay menos de 3
            
            puntaje_final_tecnica = sum(puntajes_validos)
            self.puntajes_por_tecnica_final.append(puntaje_final_tecnica)
            self.errores_totales_por_tecnica.append({
                'nombre_tecnica': tecnica_base.nombre_tecnica,
                'errores': errores_acumulados_tecnica
            })

        self.puntaje_total_kata = sum(self.puntajes_por_tecnica_final)
        self.pareja.puntaje_total = self.puntaje_total_kata
        # Actualizar también los errores en la instancia de la pareja si es necesario
        # self.pareja.errores_tecnicas = self.errores_totales_por_tecnica # O una estructura similar

    def obtener_puntaje_total_kata(self) -> float:
        return self.puntaje_total_kata

    def obtener_errores_totales_por_tecnica(self) -> list:
        return self.errores_totales_por_tecnica

    def __str__(self):
        res = f"Puntuación Kata para Pareja ID: {self.pareja.id_pareja}\n"
        res += f"Puntaje Total Kata: {self.puntaje_total_kata}\n"
        res += "Puntajes por Técnica (después de descartes):\n"
        for i, pt_tecnica in enumerate(self.puntajes_por_tecnica_final):
            res += f"  - {self.tecnicas_kata[i].nombre_tecnica}: {pt_tecnica}\n"
        res += "Errores Totales por Técnica (acumulado de todos los jueces):\n"
        for err_tecnica_info in self.errores_totales_por_tecnica:
            res += f"  - Técnica: {err_tecnica_info['nombre_tecnica']}\n"
            res += f"    Pequeños: {err_tecnica_info['errores']['pequeno']}, Medianos: {err_tecnica_info['errores']['mediano']}, Grandes: {err_tecnica_info['errores']['grande']}, Olvidadas: {err_tecnica_info['errores']['olvidada']}\n"
        return res