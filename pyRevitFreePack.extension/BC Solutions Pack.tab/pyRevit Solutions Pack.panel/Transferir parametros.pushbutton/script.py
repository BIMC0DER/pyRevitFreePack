# -*- coding: utf-8 -*-
__title__ = "Transferir\nParâmetros"
__author__ = "Fellipe Caetano - BIM Coder"
__version__ = "Versão 1.0"
__doc__ = """
_____________________________________________________________________
Descrição:

Transfere valores entre um parâmetro A e um parâmetro B

_____________________________________________________________________
Passo a passo (do script):

>>> Escolha se são elementos de Tipo ou Instância

>>> Defina a Categoria

>>> Defina o nome do parâmetro de origem

>>> Defina o nome do parâmetro de destino

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

def get_param_value(param):
    """Obtém a propriedade correta do tipo de dado do parâmetro"""
    # Obter o StorageType
    try:
        storage_type = param.StorageType
    except:
        return None

    if storage_type == StorageType.Double:
        return param.AsDouble()
    elif storage_type == StorageType.ElementId:
        return param.AsElementId()
    elif storage_type == StorageType.Integer:
        return param.AsInteger()
    else: # É string
        return param.AsString()






def main():
    # Formulário para verificar se é tipo ou instância
    is_type_instance = forms.CommandSwitchWindow.show(
    ['Tipo','Instância'],
     message='Selecione se for Tipo ou Instância',
    )

    # Formulário para selecionar Categoria
    category = select_category(doc).selected_value

    # Formulário para digitar o parâmetro de origem (source)
    source_param_name = forms.ask_for_string(prompt="Defina o nome do parâmetro de origem",title=__title__)

    # Formulário para digitar o parâmetro de destino (target)
    target_param_name = forms.ask_for_string(prompt="Defina o nome do parâmetro de destino",title=__title__)

    # Obter os elementos
    collector = FilteredElementCollector(doc).OfCategory(category)

    if is_type_instance == "Tipo":
        elements = collector.WhereElementIsElementType().ToElements()
    
    elif is_type_instance == "Instância":
        elements = collector.WhereElementIsNotElementType().ToElements()
    
    else:
        forms.alert("Tipo ou Instância não definido",exitscript=True)

    
    # Inserir os parâmetros
    for element in elements:
        # Obter o valor de origem
        source_param_value = get_param_value(element.LookupParameter(source_param_name))

        # Obter o parâmetro de destino
        target_param = element.LookupParameter(target_param_name)

        try:
            target_param.Set(source_param_value)
        except:
            continue





# __  __     _     ___  _   _ 
#|  \/  |   / \   |_ _|| \ | |
#| |\/| |  / _ \   | | |  \| |
#| |  | | / ___ \  | | | |\  |
#|_|  |_|/_/   \_\|___||_| \_|

t = Transaction(doc,__title__)
t.Start()


try:
    main()
    t.Commit()

except:
    print(traceback.format_exc())
    t.RollBack()




      

























