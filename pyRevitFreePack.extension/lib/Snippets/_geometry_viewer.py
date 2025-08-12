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

doc   = __revit__.ActiveUIDocument.Document

def show_geometry(geometry_input, vector_origin=None, vector_scale=1.0, treat_xyz_as="auto"):
    """
    Mostra geometria(s) em laranja e espera ENTER para deletar
    
    Args:
        geometry_input: Qualquer geometria (sólidos, curves, faces, bbox, pontos, vetores)
        vector_origin: Ponto de origem para vetores (default: 0,0,0)
        vector_scale: Escala para vetores (default: 1.0)
        treat_xyz_as: "auto", "points", "vectors" - como tratar XYZ
    """
    
    # Nova transação só para o preview
    t_preview = Transaction(doc, "Preview Geometry")
    t_preview.Start()
    
    created_elements = []
    
    try:
        # ACHATAR todas as listas aninhadas
        geometry_list = flatten_geometry_list(geometry_input)
        
        # Origem padrão para vetores
        if vector_origin is None:
            vector_origin = XYZ(0, 0, 0)
        
        print("🎨 Processando {} geometria(s)...".format(len(geometry_list)))
        
        # Processar cada geometria
        for i, geom in enumerate(geometry_list):
            ds = None
            
            # SÓLIDOS
            if hasattr(geom, 'Volume'):  # É um Solid
                ds = create_solid_preview(geom, i)
                print("   📦 Sólido {} criado".format(i))
                
            # CURVES/LINHAS
            elif hasattr(geom, 'GetEndPoint'):  # É uma Curve
                ds = create_curve_preview(geom, i)
                print("   📏 Curve {} criada".format(i))
                
            # FACES
            elif hasattr(geom, 'Area'):  # É uma Face
                ds = create_face_preview(geom, i)
                print("   🔺 Face {} criada".format(i))
                
            # BOUNDING BOX
            elif hasattr(geom, 'Min') and hasattr(geom, 'Max'):  # É BoundingBox
                ds = create_bbox_preview(geom, i)
                print("   📦 BBox {} criada".format(i))
                
            # PONTOS E VETORES (XYZ)
            elif hasattr(geom, 'X') and hasattr(geom, 'Y') and hasattr(geom, 'Z'):  # É um XYZ
                # Decidir se é ponto ou vetor
                is_point = decide_if_point_or_vector(geom, vector_origin, treat_xyz_as)
                
                if is_point:
                    ds = create_point_preview(geom, i)
                    print("   📍 Ponto {} criado".format(i))
                else:
                    ds = create_vector_preview(geom, i, vector_origin, vector_scale)
                    print("   🧭 Vetor {} criado".format(i))
                
            else:
                print("⚠️ Tipo {} não suportado (item {})".format(type(geom), i))
                continue
            
            if ds:
                created_elements.append(ds)
                apply_orange_override(ds)
        
        # Commit para mostrar
        t_preview.Commit()
        
        print("🟠 {} geometria(s) mostrada(s)".format(len(created_elements)))
        input("Pressione ENTER para remover...")
        
    except Exception as e:
        pass
    
    # Deletar geometrias (nova transação)
    if created_elements:
        t_delete = Transaction(doc, "Delete Preview")
        t_delete.Start()
        
        deleted_count = 0
        for ds in created_elements:
            try:
                doc.Delete(ds.Id)
                deleted_count += 1
            except:
                pass
        
        t_delete.Commit()
        print("🗑️ {} geometria(s) deletada(s)!".format(deleted_count))

def flatten_geometry_list(geometry_input):
    """
    Achata listas aninhadas de geometrias em uma lista plana
    
    Ex: [boundary_curves, solid] -> [curve1, curve2, curve3, solid]
    """
    result = []
    
    # Se não é lista, transformar em lista
    if not isinstance(geometry_input, list):
        return [geometry_input]
    
    # Iterar sobre cada item
    for item in geometry_input:
        # Se o item é uma lista, recursivamente achatar
        if isinstance(item, list):
            result.extend(flatten_geometry_list(item))
        # Se não é lista, adicionar diretamente
        else:
            result.append(item)
    
    return result

def decide_if_point_or_vector(xyz, vector_origin, treat_xyz_as):
    """
    Decide se XYZ deve ser tratado como ponto ou vetor
    """
    if treat_xyz_as == "points":
        return True
    elif treat_xyz_as == "vectors":
        return False
    else:  # "auto"
        # Auto: se magnitude pequena = vetor, se grande = ponto
        magnitude = xyz.GetLength()
        
        # Se magnitude muito pequena (< 10 metros) = provavelmente vetor
        if magnitude < 10.0:  # Menos de 10 unidades = vetor
            return False
        else:  # Maior = ponto
            return True

def create_solid_preview(solid, index):
    """Cria preview para sólido"""
    category_id = ElementId(BuiltInCategory.OST_GenericModel)
    ds = DirectShape.CreateElement(doc, category_id)
    ds.ApplicationId = "TempPreview_Solid"
    ds.ApplicationDataId = "Solid_{}".format(index)
    ds.SetShape([solid])
    return ds

def create_curve_preview(curve, index):
    """Cria preview para curve/linha"""
    category_id = ElementId(BuiltInCategory.OST_GenericModel)
    ds = DirectShape.CreateElement(doc, category_id)
    ds.ApplicationId = "TempPreview_Curve"
    ds.ApplicationDataId = "Curve_{}".format(index)
    ds.SetShape([curve])
    return ds

def create_face_preview(face, index):
    """Cria preview para face"""
    category_id = ElementId(BuiltInCategory.OST_GenericModel)
    ds = DirectShape.CreateElement(doc, category_id)
    ds.ApplicationId = "TempPreview_Face"
    ds.ApplicationDataId = "Face_{}".format(index)
    ds.SetShape([face])
    return ds

def create_bbox_preview(bbox, index):
    """Cria preview para bounding box (como wireframe)"""
    category_id = ElementId(BuiltInCategory.OST_GenericModel)
    
    # Criar linhas do wireframe da bbox
    min_pt = bbox.Min
    max_pt = bbox.Max
    
    # 8 vértices do box
    p1 = XYZ(min_pt.X, min_pt.Y, min_pt.Z)  # min
    p2 = XYZ(max_pt.X, min_pt.Y, min_pt.Z)
    p3 = XYZ(max_pt.X, max_pt.Y, min_pt.Z)
    p4 = XYZ(min_pt.X, max_pt.Y, min_pt.Z)
    p5 = XYZ(min_pt.X, min_pt.Y, max_pt.Z)
    p6 = XYZ(max_pt.X, min_pt.Y, max_pt.Z)
    p7 = XYZ(max_pt.X, max_pt.Y, max_pt.Z)  # max
    p8 = XYZ(min_pt.X, max_pt.Y, max_pt.Z)
    
    # 12 linhas do wireframe
    bbox_curves = [
        # Face inferior
        Line.CreateBound(p1, p2), Line.CreateBound(p2, p3),
        Line.CreateBound(p3, p4), Line.CreateBound(p4, p1),
        # Face superior  
        Line.CreateBound(p5, p6), Line.CreateBound(p6, p7),
        Line.CreateBound(p7, p8), Line.CreateBound(p8, p5),
        # Verticais
        Line.CreateBound(p1, p5), Line.CreateBound(p2, p6),
        Line.CreateBound(p3, p7), Line.CreateBound(p4, p8)
    ]
    
    ds = DirectShape.CreateElement(doc, category_id)
    ds.ApplicationId = "TempPreview_BBox"
    ds.ApplicationDataId = "BBox_{}".format(index)
    ds.SetShape(bbox_curves)
    return ds

def create_point_preview(point, index):
    """
    Cria preview para ponto (XYZ) como pequena cruz 3D
    """
    category_id = ElementId(BuiltInCategory.OST_GenericModel)
    
    # Tamanho da cruz (em unidades do Revit)
    cross_size = 1.0  # ~30cm
    
    # Criar 3 linhas perpendiculares formando uma cruz 3D
    point_curves = [
        # Linha X (vermelho conceitual)
        Line.CreateBound(
            point.Subtract(XYZ(cross_size, 0, 0)),
            point.Add(XYZ(cross_size, 0, 0))
        ),
        # Linha Y (verde conceitual)  
        Line.CreateBound(
            point.Subtract(XYZ(0, cross_size, 0)),
            point.Add(XYZ(0, cross_size, 0))
        ),
        # Linha Z (azul conceitual)
        Line.CreateBound(
            point.Subtract(XYZ(0, 0, cross_size)),
            point.Add(XYZ(0, 0, cross_size))
        )
    ]
    
    ds = DirectShape.CreateElement(doc, category_id)
    ds.ApplicationId = "TempPreview_Point"
    ds.ApplicationDataId = "Point_{}".format(index)
    ds.SetShape(point_curves)
    return ds

def create_vector_preview(vector, index, origin, scale):
    """
    Cria preview para vetor (XYZ) como linha com seta
    
    Args:
        vector: XYZ representando direção e magnitude
        index: índice do vetor
        origin: ponto de origem
        scale: escala do vetor
    """
    category_id = ElementId(BuiltInCategory.OST_GenericModel)
    
    # Calcular ponto final do vetor
    scaled_vector = vector.Multiply(scale)
    end_point = origin.Add(scaled_vector)
    
    # Criar linha principal do vetor
    main_line = Line.CreateBound(origin, end_point)
    
    # Criar pequena seta na ponta (30% do tamanho, 30 graus)
    vector_length = scaled_vector.GetLength()
    if vector_length > 0:
        arrow_length = vector_length * 0.3
        arrow_angle = 30 * (3.14159 / 180)  # 30 graus em radianos
        
        # Normalizar vetor
        normalized = scaled_vector.Normalize()
        
        # Criar sistema de coordenadas perpendicular
        up = XYZ.BasisZ
        if abs(normalized.DotProduct(up)) > 0.9:  # Se quase paralelo ao Z
            up = XYZ.BasisX
        
        right = normalized.CrossProduct(up).Normalize()
        
        # Calcular pontos da seta
        arrow_back = end_point.Subtract(normalized.Multiply(arrow_length))
        
        # Duas linhas da seta
        import math
        arrow_offset = right.Multiply(arrow_length * math.sin(arrow_angle))
        
        arrow_point1 = arrow_back.Add(arrow_offset)
        arrow_point2 = arrow_back.Subtract(arrow_offset)
        
        arrow_line1 = Line.CreateBound(end_point, arrow_point1)
        arrow_line2 = Line.CreateBound(end_point, arrow_point2)
        
        # Juntar todas as linhas
        vector_curves = [main_line, arrow_line1, arrow_line2]
    else:
        # Se vetor tem comprimento zero, só mostrar um ponto pequeno
        small_offset = 0.1  # 10cm
        point_line = Line.CreateBound(
            origin.Subtract(XYZ(small_offset, 0, 0)),
            origin.Add(XYZ(small_offset, 0, 0))
        )
        vector_curves = [point_line]
    
    ds = DirectShape.CreateElement(doc, category_id)
    ds.ApplicationId = "TempPreview_Vector"
    ds.ApplicationDataId = "Vector_{}".format(index)
    ds.SetShape(vector_curves)
    return ds

def apply_orange_override(ds):
    """Aplica override laranja ao DirectShape"""
    override_settings = OverrideGraphicSettings()
    orange_color = Color(255, 128, 0)  # Laranja
    
    # Obter padrão de preenchimento sólido
    solid_pattern = None
    fill_patterns = FilteredElementCollector(doc).OfClass(FillPatternElement).ToElements()
    for pattern in fill_patterns:
        if pattern.GetFillPattern().IsSolidFill:
            solid_pattern = pattern
            break
    
    if solid_pattern:
        # Padrão de superfície primeiro plano: solid fill laranja
        override_settings.SetSurfaceForegroundPatternId(solid_pattern.Id)
        override_settings.SetSurfaceForegroundPatternColor(orange_color)
    
    # Transparência 60%
    override_settings.SetSurfaceTransparency(60)
    
    # Linhas também laranja
    override_settings.SetProjectionLineColor(orange_color)
    override_settings.SetCutLineColor(orange_color)
    override_settings.SetProjectionLineWeight(5)  # Linhas grossas para destacar
    override_settings.SetCutLineWeight(5)
    
    # Aplicar override
    doc.ActiveView.SetElementOverrides(ds.Id, override_settings)

# === FUNÇÕES DE CONVENIÊNCIA ===
def preview(geometry_input, vector_origin=None, vector_scale=1.0):
    """Função rápida para preview (auto-detecta pontos/vetores)"""
    show_geometry(geometry_input, vector_origin, vector_scale, treat_xyz_as="auto")

def preview_points(geometry_input):
    """Força tratar XYZ como pontos"""
    show_geometry(geometry_input, treat_xyz_as="points")

def preview_vectors(geometry_input, origin=None, scale=1.0):
    """Força tratar XYZ como vetores"""
    show_geometry(geometry_input, origin, scale, treat_xyz_as="vectors")