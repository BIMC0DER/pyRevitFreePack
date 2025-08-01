# -*- coding: utf-8 -*-
__title__ = "Modelar Família\nCentro Ambiente"
__author__ = "Fellipe Caetano - BIM Coder"
__version__ = "Versão 1.0"
__doc__ = """
_____________________________________________________________________
Descrição:

Solução que demonstro como inserir famílias no centro de ambientes
_____________________________________________________________________
Passo a passo (do script):

>>> Obter os ambientes (busca ou seleção)

>>> Obter o sólido dos ambientes

>>> Obter o centróide do sólido

>>> Modelar a família neste ponto

>>> Definir a altura da família (opcional)

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
#from Snippets._geometry_operations import element_get_geometry 
#from Snippets._transaction import bc_transaction

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



# Função para obter o centróide de um ambiente
def get_room_centroid(room):
    """Vamos obter o centróide de um ambiente dado o seu sólido (geometria)"""

    # Opções de geometria
    options = Options()
    options.DetailLevel = ViewDetailLevel.Fine

    # Variável para opção de geometria
    geo_room = room.get_Geometry(options)

    # Obter o Sólido
    for geo in geo_room:
        room_solid = geo
        break

    # Obter o centróide do sólido
    if room_solid:
        centroid = room_solid.ComputeCentroid()
        return centroid
    
    # Não foi encontrado solid no Room
    return None

def get_type_by_name_category(family_name,type_name,category):
    """
    Obtém um Tipo (Family Symbol) dado o nome do tipo e a categoria (BuiltInCategory)
    
    Args:
        family_name: Nome da família
        name: Nome do tipo da família
        category: BuiltInCategory da família
    
    Returns:
        symbol: Tipo da família encontrado
        
    """

    # Obter o tipo da família
    all_family_types = FilteredElementCollector(doc).OfCategory(category).WhereElementIsElementType().ToElements()

    for family_type in all_family_types:
        # Nome da família
        family_type_family_name = family_type.FamilyName

        # Nome do tipo
        family_type_name = family_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()

        if family_type_family_name == family_name and family_type_name == type_name:
            return family_type
    
    # Tipo não encontrado
    return None

def family_in_center_room():
    # Lista das famílias modeladas
    new_family_instances =[]

    # Seleção dos ambientes
    rooms = pick_by_category(BuiltInCategory.OST_Rooms)
    print(rooms)

    # Tipo da família
    symbol = get_type_by_name_category("Ponto de Luz no Teto com caixa octogonal Reforçado suporte lajota 4x4","Comum",BuiltInCategory.OST_LightingFixtures)

    if symbol:
        # Centróide dos ambientes
        for room in rooms:
            centroid = get_room_centroid(room)

            # Modelar a família
            new_family = doc.Create.NewFamilyInstance(
                centroid,
                symbol,
                StructuralType.NonStructural

            )

            new_family_instances.append(new_family)
        
        return new_family_instances
    
    else:
        print("Tipo não encontrado no projeto")
    
    return 

# __  __     _     ___  _   _ 
#|  \/  |   / \   |_ _|| \ | |
#| |\/| |  / _ \   | | |  \| |
#| |  | | / ___ \  | | | |\  |
#|_|  |_|/_/   \_\|___||_| \_|

t = Transaction(doc,__title__)
t.Start()


try:
    family_in_center_room()
    t.Commit()

except:
    print(traceback.format_exc())
    t.RollBack()




      

























