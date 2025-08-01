# -*- coding: utf-8 -*-

# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╚═╝
#==================================================
from Autodesk.Revit.DB import *
import sys
import System
from System import Array
from System.Collections.Generic import *

# ╔╦╗╔═╗╦╔╗╔
# ║║║╠═╣║║║║
# ╩ ╩╩ ╩╩╝╚╝
#==================================================
def is_point_in_solid(solid,point):
    # Curva pequena criada para utilizar o método disponível na API do Revit
    curve_loc = Line.CreateBound(point, point + XYZ(1,0,0))
    try:
        intersect = solid.IntersectWithCurve(curve_loc,SolidCurveIntersectionOptions())
        intersect_result = intersect.GetCurveSegment(0)
        return True
    except:
        return False

def cylinder_by_line(line,radius=1):
    # Parâmetros para o círculo
    center = line.GetEndPoint(0)  # Centro do círculo
    start_angle = 0.0  # Ângulo inicial (em radianos)
    end_angle = 6.28318530718  # Ângulo final (2π radianos para um círculo completo)

    # Criar o plano onde o círculo será desenhado (XY plano por padrão)
    normal = line.Direction
    plane = Plane.CreateByNormalAndOrigin(normal, center)

    # Criar o arco que forma o círculo completo
    # Foi necessário separar em dois por requisito da API do Revit
    circle1 = Arc.Create(plane, radius, start_angle, end_angle/2)
    circle2 = Arc.Create(plane, radius, end_angle/2, end_angle)

    # CurveLoop
    curve_loops = List[CurveLoop]()
    curve_loop = CurveLoop()
    curve_loop.Append(circle1)
    curve_loop.Append(circle2)
    curve_loops.Add(curve_loop)

    profile = curve_loops

    # Criar Sólido
    solid = GeometryCreationUtilities.CreateExtrusionGeometry(profile,normal,line.Length)

    return solid


def face_project_points(face,u_divisions=10,v_divisions=10,margin=0.1):
    # Obter os limites UV da superfície
    bbox = face.GetBoundingBox()
    minUV = bbox.Min
    maxUV = bbox.Max

    # Ajustar os limites para considerar a margem
    adjustedMinU = minUV.U + (maxUV.U - minUV.U) * margin
    adjustedMaxU = maxUV.U - (maxUV.U - minUV.U) * margin
    adjustedMinV = minUV.V + (maxUV.V - minUV.V) * margin
    adjustedMaxV = maxUV.V - (maxUV.V - minUV.V) * margin

    # Gerar a malha de pontos UV centralizada
    points = []
    for i in range(u_divisions + 1):
        for j in range(v_divisions + 1):
            u = adjustedMinU + (adjustedMaxU - adjustedMinU) * i / u_divisions
            v = adjustedMinV + (adjustedMaxV - adjustedMinV) * j / v_divisions
            # Converter para ponto 3D na face
            point_on_surface = face.Evaluate(UV(u, v))
            points.append(point_on_surface)
        
        
    return points    
         
 
def faces_get_bottom(faces):
    i=0
    min_origin= None
    bottom_face = None

    for face in faces:
        origin = face.Origin.Z

        if i==0:
            bottom_face=face

        if origin<min_origin:
            bottom_face = face
        
        i+=1   

    return bottom_face

def face_perimeter_lines(face):
    lines = []
    curve_loops = face.GetEdgesAsCurveLoops()
    for curve_loop in curve_loops:
        for curve in curve_loop:
            lines.append(curve)
    
    return lines



def element_get_solid(element):
    options = Options()
    options.ComputeReferences = True
    options.DetailLevel = ViewDetailLevel.Fine
    geometry = element.get_Geometry(options)  # Obter a geometria do elemento
    solids = []
    
    for geom_obj in geometry:
        if isinstance(geom_obj, Solid) and geom_obj.Volume > 0:  # Filtrar apenas sólidos válidos
            solids.append(geom_obj)
    
    if not solids:
        raise Exception("Nenhum sólido encontrado.")
    
    return solids

def element_get_faces(element):
    options = Options()
    options.ComputeReferences = True
    options.DetailLevel = ViewDetailLevel.Fine
    geometry = element.get_Geometry(options)  # Obter a geometria do elemento
    solids = []
    
    for geom_obj in geometry:
        if isinstance(geom_obj, Solid) and geom_obj.Volume > 0:  # Filtrar apenas sólidos válidos
            solid = geom_obj
            break
    
    if not solid:
        raise Exception("Nenhum sólido encontrado.")
    
    else:
        faces = []
        face_array = solid.Faces
        for array in face_array:
            faces.append(array)
        
        return faces


def element_get_geometry(element):
    options = Options()
    options.ComputeReferences = True
    options.DetailLevel = ViewDetailLevel.Fine
    geometry = element.get_Geometry(options)  # Obter a geometria do elemento
    geometries = []
    
    for geom_obj in geometry:
        geometries.append(geom_obj)
        
    return geometries


def geometry_translate(geometry,direction,length):
    # Criar o Transform
    transform = Transform.CreateTranslation(direction.Normalize() * length)

    # Criar a nova linha deslocada
    transfomed_geometry = geometry.CreateTransformed(transform)

    return transfomed_geometry