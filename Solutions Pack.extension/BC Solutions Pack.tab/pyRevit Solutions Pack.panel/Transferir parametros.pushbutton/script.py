# -*- coding: utf-8 -*-
__title__ = "Transferir\nParâmetros"
__author__ = "Fellipe Caetano - BIM Coder"
__version__ = "Versão 1.0"
__doc__ = """
_____________________________________________________________________
Descrição:


_____________________________________________________________________
Passo a passo (do script):



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
    # Formulário para selecionar se é tipo ou instância
    is_type_instance = forms.CommandSwitchWindow.show(
    ['Tipo','Instância'],
     message='Tipo ou Instância?',
    )

    # Formulário para escolher a categoria
    category = select_category(doc).selected_value

    # Formulário para escolher o parâmetro de origem
    source_param_name = forms.ask_for_string(prompt="Nome do Parâmetro de Origem",title=__title__)

    # Formulário para escolher o parâmetro de destino
    target_param_name = forms.ask_for_string(prompt="Nome do Parâmetro de Destino",title=__title__)

    # Obter os elementos - Origem
    collector = FilteredElementCollector(doc).OfCategory(category)

    if is_type_instance == "Tipo":
        elements = collector.WhereElementIsElementType().ToElements()
    elif is_type_instance == "Instância":
        elements = collector.WhereElementIsNotElementType().ToElements()
    else:
        forms.alert("Tipo ou Instância não definido",exitscript=True)
        
    
    # Inserir os parâmetros
    for element in elements:
        # Obter o valor do parâmetro de origem
        source_param_value = get_param_value(element.LookupParameter(source_param_name))

        # Obter o parâmetro de destino
        target_param = element.LookupParameter(target_param_name)

        # Inserir valor no parâmetro de destino
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




      

























