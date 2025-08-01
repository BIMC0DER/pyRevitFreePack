# -*- coding: utf-8 -*-

#Imports
from Autodesk.Revit.DB import XYZ
import math

# Functions

def rotate_vector(vector, rotation_rad):
    # pt_start = XYZ(BB.Min.X, (BB.Min.Y + BB.Max.Y) / 2, BB.Min.Z)
    # pt_end   = XYZ(BB.Max.X, (BB.Min.Y + BB.Max.Y) / 2, BB.Min.Z)
    # vector   = pt_end - pt_start
    # rotation = self.element.Location.Rotation

    # Get vector X,Y
    vector_x = vector.X
    vector_y = vector.Y

    # Apply Rotation
    rotated_x = vector_x * math.cos(rotation_rad) - vector_y * math.sin(rotation_rad)
    rotated_y = vector_x * math.sin(rotation_rad) + vector_y * math.cos(rotation_rad)
    rotated_z = vector.Z

    # Creating a new rotated vector
    return XYZ(rotated_x, rotated_y, rotated_z)


def vector_isparallel(vec1,vec2):
    cross_product = vec1.CrossProduct(vec2)
    dot_product = vec1.DotProduct(vec2)
    # Vetores paralelos terão produto cruzado 0 e o produto escalar será positivo (0°) ou negativo (180°)
    return cross_product.IsZeroLength() and abs(dot_product) > 0

