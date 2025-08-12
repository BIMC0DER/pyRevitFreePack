# -*- coding: utf-8 -*-
__title__ = "Exportar dados\npara Dashboard"
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

def export_to_csv(data_lists, file_path, headers=None):
    """
    Exporta listas de dados para um arquivo CSV
    
    Args:
        data_lists (list): Lista contendo as listas de dados para cada coluna
        file_path (str): Caminho completo do arquivo CSV a ser criado
        headers (list, opcional): Lista com os nomes das colunas
    
    Returns:
        bool: True se exportou com sucesso, False caso contrário
    """
    import csv
    import os
    
    try:
        # Verifica se data_lists não está vazio
        if not data_lists:
            print("ERRO: Nenhuma lista de dados fornecida!")
            return False
        
        # Encontra o tamanho máximo entre todas as listas
        max_length = max(len(lst) for lst in data_lists)
        
        # Preenche listas menores com valores vazios
        normalized_lists = []
        for lst in data_lists:
            normalized_list = list(lst)  # Cria uma cópia
            while len(normalized_list) < max_length:
                normalized_list.append("")
            normalized_lists.append(normalized_list)
        
        # Cria o diretório se não existir
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Escreve o arquivo CSV
        with open(file_path, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            
            # Escreve os cabeçalhos se fornecidos
            if headers:
                writer.writerow(headers)
            
            # Escreve os dados linha por linha
            for i in range(max_length):
                row = [normalized_lists[col][i] for col in range(len(normalized_lists))]
                writer.writerow(row)
        
        print("✅ CSV exportado com sucesso: {}".format(file_path))
        return True
        
    except Exception as e:
        print("❌ ERRO ao exportar CSV: {}".format(str(e)))
        return False
    

 
def main():

    walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

    walls_type_name = []
    walls_length = []
    walls_level = []
    walls_width = []


    for wall in walls:
        # Nome do tipo
        type = doc.GetElement(wall.GetTypeId())
        type_name = type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
        walls_type_name.append(type_name)

        # Comprimento
        try: length = round(UnitUtils.ConvertToInternalUnits(wall.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble(),UnitTypeId.Meters),2)
        except: length = 0

        walls_length.append(length)

        # Nível
        try: 
            level = doc.GetElement(wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId())
            level_name = level.Name
        
        except:
            level = "Sem nível"

        walls_level.append(level_name)

        # Espessura da parede
        try: 
            wall_width = UnitUtils.ConvertFromInternalUnits(wall.Width,UnitTypeId.Centimeters)
        
        except:
            wall_width = 0

        walls_width.append(wall_width)

    

    file_path = r"C:\temp\dados_paredes.csv"

    export_to_csv([walls_type_name,walls_length,walls_level,walls_width], file_path, headers=["Nome do tipo","Comprimento","Nivel","Espessura"])







    



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




      



"""

walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

    walls_type_name = []
    walls_length = []
    walls_base_level = []
    wall_width = []
    
    for wall in walls:
        # Obter o nome do tipo
        type = doc.GetElement(wall.GetTypeId())
        type_name = type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()

        # Dados da parede
        length = round(UnitUtils.ConvertFromInternalUnits(wall.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble(),UnitTypeId.Meters),2)

        base_level = doc.GetElement(wall.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()).Name

        width = round(UnitUtils.ConvertFromInternalUnits(type.Width,UnitTypeId.Centimeters),2)

        walls_type_name.append(type_name)
        walls_length.append(length)
        walls_base_level.append(base_level)
        wall_width.append(width)
    
    print(walls_type_name)
    print(walls_length)
    print(walls_base_level)
    print(wall_width)

    caminho_arquivo = r"C:\temp\dados_paredes.csv"
    export_to_csv([walls_type_name,walls_length,walls_base_level,wall_width], caminho_arquivo, 
                headers=["Tipo","Comprimento","Nivel","Espessura"])



"""















