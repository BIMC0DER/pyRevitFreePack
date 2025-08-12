# -*- coding: utf-8 -*-
__title__ = "Criar Vistas\n2D e 3D"
__author__ = "Fellipe Caetano - BIM Coder"
__version__ = "Versão 1.0"
__doc__ = """
_____________________________________________________________________
Descrição:

Permite criar Vistas 2D e 3D de ambientes automático

_____________________________________________________________________
Passo a passo (do script):

>>> Clique no botão

>>> Escolha o Offset

_____________________________________________________________________
Última atualização:
- [25.03.2025] - VERSÃO 1.0

"""
# ___  __  __  ____    ___   ____   _____  ____  
#|_ _||  \/  ||  _ \  / _ \ |  _ \ |_   _|/ ___| 
# | | | |\/| || |_) || | | || |_) |  | |  \___ \ 
# | | | |  | ||  __/ | |_| ||  _ <   | |   ___) |
#|___||_|  |_||_|     \___/ |_| \_\  |_|  |____/ 
#=================================================

# Importações Python e .NET
import clr
import clr
import os, traceback,math,re
clr.AddReference("System")

# Importações Revit API
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Selection import *
from Autodesk.Revit.DB.Structure import StructuralType

# Importações pyRevit
from pyrevit import forms, script

# Suas Funções/ Snippets personalizados
from Snippets._selection import pick_by_category
from GUI._forms import select_category
#from Snippets._geometry_operations import element_get_geometry 
#from Snippets._transaction import bc_transaction
from Snippets._geometry_viewer import show_geometry

# Variáveis globais do Revit
doc   = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app   = __revit__.Application
rvt_year = int(app.VersionNumber)
PATH_SCRIPT = os.path.dirname(__file__)

# _____  _   _  _   _   ____  _____  ___   ___   _   _  ____  
#|  ___|| | | || \ | | / ___||_   _||_ _| / _ \ | \ | |/ ___| 
#| |_   | | | ||  \| || |      | |   | | | | | ||  \| |\___ \ 
#|  _|  | |_| || |\  || |___   | |   | | | |_| || |\  | ___) |
#|_|     \___/ |_| \_| \____|  |_|  |___| \___/ |_| \_||____/ 

class RoomSelectionFilter(ISelectionFilter):
    """Filtro de seleção para permitir apenas elementos da categoria Rooms"""
    
    def AllowElement(self, element):
        """Permite apenas elementos da categoria OST_Rooms"""
        if element.Category and element.Category.Id.IntegerValue == int(BuiltInCategory.OST_Rooms):
            return True
        return False
    
    def AllowReference(self, refer, point):
        """Não permite seleção de referências"""
        return False

def get_room_section_box(room,offset):
    # Obter as linhas do ambiente
    options = SpatialElementBoundaryOptions()
    options.SpatialElementBoundaryLocation = SpatialElementBoundaryLocation.Finish

    boundary_segments = room.GetBoundarySegments(options)

    # Obter a altura do ambiente
    room_height = UnitUtils.ConvertToInternalUnits(300,UnitTypeId.Centimeters)

    # Obter a localização do ambiente
    room_location = room.Location.Point

    # Extrair as linhas do boundary
    boundary_curves = []
    for boundary_segment in boundary_segments:
        for bs in boundary_segment:
            curve = bs.GetCurve()
            boundary_curves.append(curve)

    # Criar o CurveLoop
    curve_loop = CurveLoop.Create(boundary_curves)

    # Aplicar o Offset
    offset_loop = CurveLoop.CreateViaOffset(curve_loop,offset,XYZ.BasisZ)

    # Criar o sólido
    extrusion_vector = XYZ.BasisZ * (room_height + offset)
    solid = GeometryCreationUtilities.CreateExtrusionGeometry([offset_loop],XYZ.BasisZ, room_height)

    transform = Transform.CreateTranslation(room.Location.Point)
    transform_solid = SolidUtils.CreateTransformed(solid,transform)

    # Obter a BoundingBox do Sólido
    bbox = transform_solid.GetBoundingBox()

    # Aplicar offset no fundo
    bbox_min = XYZ(
        bbox.Min.X,
        bbox.Min.Y,
        bbox.Min.Z - offset
    )

    new_bbox = BoundingBoxXYZ()
    new_bbox.Min = bbox_min
    new_bbox.Max = bbox.Max

    # Centro da bbox original
    bbox_center = XYZ(
        (bbox.Min.X + bbox.Max.X) / 2,
        (bbox.Min.Y + bbox.Max.Y) / 2,
        (bbox.Min.Z + bbox.Max.Z) / 2
    )

    # Vetor de translação 
    # OBS: Necessário mover a BB pois BB obtida de geometria é instanciada na origem
    translation = solid.ComputeCentroid().Subtract(bbox_center)

    # Mover a bb
    moved_bbox = BoundingBoxXYZ()
    moved_bbox.Min = new_bbox.Min.Add(translation)
    moved_bbox.Max = new_bbox.Max.Add(translation) 

    return moved_bbox

 
def main():

    # Seleção dos ambientes
    refs = uidoc.Selection.PickObjects(ObjectType.Element,RoomSelectionFilter())
    rooms = [doc.GetElement(ref) for ref in refs]

    # Obter o offset
    offset = forms.ask_for_number_slider(default=15,prompt="Defina o Offset em cm",max=300,title=__title__)

    # Converter o offset para unidades internas
    offset_converted = UnitUtils.ConvertToInternalUnits(offset,UnitTypeId.Centimeters)

    # Obter view family type para vista 3D
    view3d_types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
    view3d_type = None
    
    for vft in view3d_types:
        if vft.ViewFamily == ViewFamily.ThreeDimensional:
            view3d_type = vft
            break

    
    for room in rooms:

        # Obter a Section Box
        section_box = get_room_section_box(room,offset_converted)

        room_name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
        
        # Criar a Vista 3D
        new_view3D = View3D.CreateIsometric(doc,view3d_type.Id)

        # Definir o novo nome
        for i in range(50):
            try:
                name = room_name + " - 3D"
                new_view3D.Name = name
                break
            except: 
                name += "*"
                
        # Aplicar section box
        new_view3D.SetSectionBox(section_box)
        
        # Criar a vista 2D
        active_view = doc.ActiveView

        # Duplicar a vista 2D
        new_view_id = active_view.Duplicate(ViewDuplicateOption.Duplicate)
        new_view = doc.GetElement(new_view_id)

        # Aplicar a cropbox
        new_view.CropBox = section_box

         # Definir o novo nome
        for i in range(50):
            try:
                name = room_name + " - 2D"
                new_view.Name = name
                break
            except: 
                name += "*"


# __  __     _     ___  _   _ 
#|  \/  |   / \   |_ _|| \ | |
#| |\/| |  / _ \   | | |  \| |
#| |  | | / ___ \  | | | |\  |
#|_|  |_|/_/   \_\|___||_| \_|


#main()

t = Transaction(doc,__title__)
t.Start()


try:
    main()
    t.Commit()

except:
    print(traceback.format_exc())
    t.RollBack()




      

























