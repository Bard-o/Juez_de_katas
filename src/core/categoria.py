# src/core/categoria.py

class Categoria:
    def __init__(self, nombre_categoria: str, tipo_kata: str):
        self.nombre_categoria = nombre_categoria
        self.tipo_kata = tipo_kata
        self.parejas = []

    def agregar_pareja(self, pareja):
        self.parejas.append(pareja)
        print(f"Pareja '{pareja.id_pareja}' agregada a la categoría '{self.nombre_categoria}'.")

    def __str__(self):
        return f"Categoría: {self.nombre_categoria}, Tipo de Kata: {self.tipo_kata}"