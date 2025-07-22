# -*- coding: utf-8 -*-

#Imports
from Autodesk.Revit.DB import Options, ViewDetailLevel,ReferenceArray, GeometryInstance
import math

# Functions

class WallGeometry:
    def __init__(self, wall):
        """
        Inicializa a classe com a parede fornecida.
        """
        self.wall = wall
        self._geometry = self.get_geometry()
        self._parallel_refs = None

    def get_geometry(self):
        """
        Obtém a geometria da parede, lidando com instâncias de geometria aninhada.
        """
        opt = Options()
        opt.ComputeReferences = True
        opt.DetailLevel = ViewDetailLevel.Coarse
        geometria = self.wall.get_Geometry(opt)

        # Lista para armazenar todas as geometrias (incluindo subgeometrias)
        all_geometry = []

        for obj in geometria:
            if isinstance(obj, GeometryInstance):
                # Expandir a geometria da instância
                instance_geometry = obj.GetInstanceGeometry()
                all_geometry.extend(instance_geometry)
            else:
                all_geometry.append(obj)

        return all_geometry

    def get_wall_direction(self):
        """
        Obtém a direção da linha de localização da parede.
        """
        return self.wall.Location.Curve.Direction

    def get_parallel_references(self):
        """
        Obtém as referências das faces paralelas da parede, ordenadas por área.
        Caso o número de faces seja maior que 2, retorna as referências das 2 maiores por área.
        """
        if self._parallel_refs is None:
            wall_direction = self.get_wall_direction()
            parallel_faces = []

            # Obter faces paralelas
            for obj in self._geometry:
                for face in obj.Faces:
                    try:
                        normal = face.FaceNormal
                        # Verifica se a face é paralela (normal e direção ortogonais)
                        if abs(normal.Z) < 1e-6 and abs(wall_direction.DotProduct(normal)) < 1e-6:
                            parallel_faces.append(face)
                    except:
                        pass

            # Ordenar as faces por área em ordem decrescente
            parallel_faces.sort(key=lambda f: f.Area, reverse=True)

            # Capturar referências das 2 maiores ou todas, se menor ou igual a 2
            self._parallel_refs = ReferenceArray()
            for face in parallel_faces[:2]:
                self._parallel_refs.Append(face.Reference)

        return self._parallel_refs

    def get_parallel_faces(self):
        """
        Obtém as faces paralelas como objetos de face, ordenadas por área.
        Caso o número de faces seja maior que 2, retorna as 2 maiores por área.
        """
        wall_direction = self.get_wall_direction()
        parallel_faces = []

        for obj in self._geometry:
            for face in obj.Faces:
                try:
                    normal = face.FaceNormal
                    # Verifica se a face é paralela
                    if abs(normal.Z) < 1e-6 and abs(wall_direction.DotProduct(normal)) < 1e-6:
                        parallel_faces.append(face)
                except:
                    pass

        # Ordenar as faces por área em ordem decrescente
        parallel_faces.sort(key=lambda f: f.Area, reverse=True)

        # Retornar as 2 maiores se houver mais de 2 faces
        if len(parallel_faces) > 2:
            return parallel_faces[:2]

        return parallel_faces


def are_walls_collinear(wall1, wall2):
    """
    Verifica se duas paredes estão alinhadas (colineares) com base na direção e produto vetorial.
    :param wall1: Primeira parede
    :param wall2: Segunda parede
    :param tolerance: Tolerância para verificar colinearidade
    :return: True se as paredes forem colineares, False caso contrário
    """
    # Obter as curvas de localização das paredes
    curve1 = wall1.Location.Curve
    curve2 = wall2.Location.Curve

    # Obter as direções das curvas
    direction1 = curve1.Direction
    direction2 = curve2.Direction

    # Verifica se as direções são colineares
    if not direction1.CrossProduct(direction2).GetLength() < 1e-6:
        return False

    # Verificar se as curvas estão no mesmo eixo (colineares)
    start1 = curve1.GetEndPoint(0)
    start2 = curve2.GetEndPoint(0)
    connection_vector = start2 - start1

    # Produto vetorial entre o vetor de conexão e a direção da primeira parede
    return connection_vector.CrossProduct(direction1).GetLength() < 1e-6

def filter_collinear_walls(walls):
    """
    Filtra paredes para manter apenas uma por alinhamento (colinearidade).
    :param walls: Lista de paredes
    :param tolerance: Tolerância para verificar colinearidade
    :return: Lista filtrada de paredes
    """
    filtered_walls = []
    for i, wall1 in enumerate(walls):
        is_unique = True
        for wall2 in filtered_walls:
            if are_walls_collinear(wall1, wall2):
                is_unique = False
                break
        if is_unique:
            filtered_walls.append(wall1)
    return filtered_walls