# -*- coding: utf-8 -*-
__title__ = "Cotas Famílias"
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

 
def main():

    # Seleção das famílias
    selected_families = [doc.GetElement(ref) for ref in uidoc.Selection.PickObjects(ObjectType.Element)]

    # Offset da cota
    offset = UnitUtils.ConvertToInternalUnits(forms.ask_for_number_slider(default=10,min=0,max=300,prompt="Insira o offset da cota (cm)"),UnitTypeId.Centimeters)

    if selected_families:
        # Obter as References e adicionar ao Array
        ref_array = ReferenceArray()

        for instance in selected_families:
            # Obter a reference
            ref = instance.GetReferences(FamilyInstanceReferenceType.CenterLeftRight)[0]

            # Adicionar ao Array
            ref_array.Append(ref)

        # Dados de uma família de amostra
        family_orientation = selected_families[0].FacingOrientation # Orientação
        family_orientation_orto = family_orientation.CrossProduct(XYZ.BasisZ) # Orientação Ortogonal
        location = selected_families[0].Location.Point # Localização

        # Linha da cota
        dim_line = Line.CreateBound(location, location + family_orientation_orto)    
            
        # Criar a cota
        new_dim = doc.Create.NewDimension(doc.ActiveView,dim_line,ref_array)

        # Mover a cota
        new_dim.Location.Move(family_orientation*offset)


    
    return
    

    

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




      

























