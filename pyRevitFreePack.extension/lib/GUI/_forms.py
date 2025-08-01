# -*- coding: utf-8 -*-
import clr
import wpf
import os

clr.AddReference("System.Windows.Forms")
clr.AddReference("System")
import System
from System.Collections.Generic import List
from System.Windows.Controls import CheckBox, Button, TextBox, ListBoxItem, TextBlock, ComboBoxItem

from System.Windows.Forms import Application, Form, ComboBox, Label, Button, FormStartPosition,FormBorderStyle
from System.Drawing import Point, Size, Font,ContentAlignment
from System.Windows import Window
from System.Windows.Controls import ComboBoxItem
from System.Windows import Visibility

from Autodesk.Revit.DB import BuiltInCategory

class select_from_dict(Window):
    def __init__(self, data_dict, title='Formulário de Seleção', label_busca="Busca:", label_serie="Filtro:"):
        PATH_SCRIPT = os.path.dirname(__file__)
        path_xaml_file = os.path.join(PATH_SCRIPT, "select_from_dict.xaml")
        wpf.LoadComponent(self, path_xaml_file)

        # Modificar o título e labels
        self.Title = title
        self.UIe_search_label.Text = label_busca
        self.UIe_series_label.Text = label_serie

        # Dados fornecidos pelo usuário
        self.series_data = data_dict

        # Variáveis para os itens da lista
        self.current_items = []
        self.displayed_items = []

        # Dicionário para manter o estado de seleção de cada item
        # A chave será o item (string) e o valor, um booleano indicando se está selecionado.
        self.item_selection_state = {}

        # Inicializar ComboBox
        self.UIe_series_combobox.ItemsSource = self.series_data.keys()
        self.UIe_series_combobox.SelectedIndex = 0

        # Configurar exibição inicial
        self.UIe_ComboBox_SelectionChanged(None, None)

        # Abrir o formulário
        self.ShowDialog()

    def UIe_ComboBox_SelectionChanged(self, sender, e):
        selected_series = self.UIe_series_combobox.SelectedItem
        self.UIe_items_panel.Children.Clear()

        if selected_series:
            self.current_items = self.series_data.get(selected_series, [])
            # Inicializa ou mantém o estado de seleção para cada item da série atual.
            for item in self.current_items:
                if item not in self.item_selection_state:
                    self.item_selection_state[item] = False
            # Exibe todos os itens inicialmente
            self.displayed_items = self.current_items[:]
            self.populate_items()

    def UIe_SearchBox_TextChanged(self, sender, e):
        search_text = self.UIe_searchbox.Text.lower()
        self.displayed_items = [
            item for item in self.current_items if search_text in item.lower()
        ]
        self.populate_items()

    def populate_items(self):
        # Limpa a lista atual na interface
        self.UIe_items_panel.Children.Clear()
        # Para cada item filtrado, cria um CheckBox configurando seu estado de acordo com o dicionário
        for item in self.displayed_items:
            checkbox = CheckBox(Content=item, IsChecked=self.item_selection_state.get(item, False))
            # Anexa os eventos para atualizar o estado quando o usuário marcar/desmarcar
            checkbox.Checked += lambda sender, e, item=item: self.update_item_state(item, True)
            checkbox.Unchecked += lambda sender, e, item=item: self.update_item_state(item, False)
            self.UIe_items_panel.Children.Add(checkbox)

    def update_item_state(self, item, state):
        # Atualiza o dicionário com o novo estado
        self.item_selection_state[item] = state

    def UIe_CheckButton_Click(self, sender, e):
        # Marca todos os itens exibidos e atualiza o estado no dicionário
        for item in self.displayed_items:
            self.item_selection_state[item] = True
        self.populate_items()

    def UIe_UncheckButton_Click(self, sender, e):
        # Desmarca todos os itens exibidos e atualiza o estado no dicionário
        for item in self.displayed_items:
            self.item_selection_state[item] = False
        self.populate_items()

    def UIe_SelectButton_Click(self, sender, e):
        # Ao confirmar, coleta todos os itens cujo estado no dicionário seja True,
        # independentemente de estarem visíveis no momento
        self.selected_items = [item for item, selected in self.item_selection_state.items() if selected]
        self.Close()


class select_from_list(Window):
    def __init__(self, lista, title='Formulário de Seleção', label_busca="Busca:", description=None, width=450, height=400):
        PATH_SCRIPT = os.path.dirname(__file__)
        path_xaml_file = os.path.join(PATH_SCRIPT, "select_from_list.xaml")
        wpf.LoadComponent(self, path_xaml_file)

        # Modificar o título
        self.Title = title
        
        # Ajustar as dimensões do formulário
        self.Width = width
        self.Height = height

        # Configurar labels dinamicamente
        self.UIe_search_label.Text = label_busca
        
        # Configurar a descrição (se fornecida)
        if description:
            self.UIe_description.Text = description
            self.UIe_description.Visibility = Visibility.Visible
        else:
            self.UIe_description.Visibility = Visibility.Collapsed

        # Dados fornecidos pelo usuário
        self.series_data = lista  # lista de itens

        # Variáveis para os itens da lista
        self.current_items = self.series_data
        self.displayed_items = self.current_items[:]

        # Dicionário para manter o estado de seleção de cada item
        self.item_selection_state = {}
        for item in self.current_items:
            if item not in self.item_selection_state:
                self.item_selection_state[item] = False

        self.populate_items()

        # Abrir o formulário
        self.ShowDialog()
    
    def UIe_searchbox_TextChanged(self, sender, e):
        search_text = self.UIe_searchbox.Text.lower()
        self.displayed_items = [
            item for item in self.current_items if search_text in str(item).lower()
        ]
        self.populate_items()

    def populate_items(self):
        self.UIe_items_panel.Children.Clear()
        for item in self.displayed_items:
            # Cria um CheckBox configurado com o estado armazenado no dicionário
            checkbox = CheckBox(Content=item, IsChecked=self.item_selection_state.get(item, False))
            # Anexa eventos para atualizar o estado quando o usuário marcar/desmarcar o item
            checkbox.Checked += lambda sender, e, item=item: self.update_item_state(item, True)
            checkbox.Unchecked += lambda sender, e, item=item: self.update_item_state(item, False)
            self.UIe_items_panel.Children.Add(checkbox)

    def update_item_state(self, item, state):
        # Atualiza o dicionário com o estado do item
        self.item_selection_state[item] = state

    def UIe_check_button_Click(self, sender, e):
        # Marca todos os itens atualmente exibidos e atualiza o dicionário
        for item in self.displayed_items:
            self.item_selection_state[item] = True
        self.populate_items()

    def UIe_uncheck_button_Click(self, sender, e):
        # Desmarca todos os itens atualmente exibidos e atualiza o dicionário
        for item in self.displayed_items:
            self.item_selection_state[item] = False
        self.populate_items()

    def UIe_select_button_Click(self, sender, e):
        # Coleta todos os itens marcados, independentemente de estarem visíveis ou não
        self.selected_items = [item for item, selected in self.item_selection_state.items() if selected]
        self.Close()


# Formulário de Seleção da Categoria reutilizável
# Formulário de Seleção da Categoria reutilizável
class select_category(Window):
    """
    Classe para seleção de categoria do Revit.
    Permite escolher entre qualquer subconjunto de categorias ou todas as categorias disponíveis.
    """
    def __init__(self, doc, 
                 title="Selecionar Categoria", 
                 button_text="Confirmar", 
                 default_category=None,
                 categories_filter=None, 
                 xaml_path=None,
                 return_type="builtin",
                 auto_show=True):  # Novo parâmetro para controlar a exibição automática
        """
        Inicializa o formulário de seleção de categoria.
        
        Args:
            doc: Documento Revit ativo
            title: Título da janela
            button_text: Texto do botão de confirmação
            default_category: Nome da categoria selecionada por padrão
            categories_filter: Lista de nomes de categorias para filtrar (None = todas)
            xaml_path: Caminho personalizado para o arquivo XAML (None = usar padrão)
            return_type: Tipo de retorno ('name', 'category', ou 'builtin')
            auto_show: Se True, exibe automaticamente o formulário
        """
        # Definir caminho do XAML
        if xaml_path is None:
            PATH_SCRIPT = os.path.dirname(__file__)
            xaml_path = os.path.join(PATH_SCRIPT, "select_category.xaml")
        
        # Carregar XAML
        wpf.LoadComponent(self, xaml_path)
        
        # Configurar propriedades da janela
        self.Title = title
        self.UIe_button.Content = button_text
        
        # Configurar tipo de retorno
        self._return_type = return_type
        self.selected_value = None
        
        # Obtém as categorias do documento
        all_categories = doc.Settings.Categories
        self.category_dict = {}
        
        # Filtrar categorias se necessário
        if categories_filter is not None:
            for cat in all_categories:
                if cat.Name in categories_filter:
                    self.category_dict[cat.Name] = cat
        else:
            self.category_dict = {cat.Name: cat for cat in all_categories}
        
        # Preencher o ComboBox com nomes de categorias ordenados
        category_names = sorted(self.category_dict.keys())
        for name in category_names:
            self.UIe_combobox.Items.Add(name)
        
        # Definir a seleção padrão
        if default_category and default_category in category_names:
            self.UIe_combobox.SelectedItem = default_category
        elif category_names:
            self.UIe_combobox.SelectedItem = category_names[0]
        
        # Mostrar o formulário automaticamente se solicitado
        if auto_show:
            self.ShowDialog()
    
    def UIE_button_run(self, sender, e):
        """Ação ao clicar no botão de confirmação."""
        selected_name = self.UIe_combobox.SelectedItem
        
        if selected_name and selected_name in self.category_dict:
            category = self.category_dict[selected_name]
            
            # Retornar o valor conforme o tipo de retorno solicitado
            if self._return_type == "name":
                self.selected_value = selected_name
            elif self._return_type == "category":
                self.selected_value = category
            elif self._return_type == "builtin":
                try:
                    built_in_category_id = category.Id.IntegerValue
                    self.selected_value = BuiltInCategory(built_in_category_id)
                except Exception as e:
                    print("Erro ao mapear para BuiltInCategory: {}".format(e))
                    self.selected_value = None
        
        self.Close()
    
    @staticmethod
    def show(doc, **kwargs):
        """
        Método estático para criar, mostrar o diálogo e retornar o resultado.
        
        Args:
            doc: Documento Revit ativo
            **kwargs: Argumentos adicionais para passar para o construtor
            
        Returns:
            O valor selecionado conforme o tipo de retorno configurado
        """
        # Define auto_show como False no kwargs para evitar exibição dupla
        kwargs['auto_show'] = False
        
        # Cria o diálogo
        dialog = select_category(doc, **kwargs)
        
        # Exibe o diálogo e aguarda seu fechamento
        dialog.ShowDialog()
        
        # Retorna o valor selecionado
        return dialog.selected_value
    
class RevitCategoriesManager:
    def __init__(self, doc):
        """Inicializa a classe com o documento atual do Revit
        
        Args:
            doc: documento Revit atual
        """
        self.doc = doc
        # Define algumas categorias comuns
        self.common_categories = [
            "Walls", 
            "Doors", 
            "Windows", 
            "Floors", 
            "Ceilings", 
            "Furniture", 
            "Rooms",
            "Roofs",
            "Generic Models",
            "Mass",
            "Parking",
            "Railings"
            
        ]
        
        # Dicionário para mapear nomes de categorias para objetos Category
        self._category_dict = {}
        
        # Carrega todas as categorias disponíveis no documento
        for cat in self.doc.Settings.Categories:
            self._category_dict[cat.Name] = cat
    
    def list_categories(self):
        """Lista todas as categorias definidas na classe
        
        Returns:
            list: Lista dos nomes de categorias da classe
        """
        return self.common_categories
    
    def list_all_document_categories(self):
        """Lista todas as categorias do documento
        
        Returns:
            list: Lista com todos os nomes das categorias do documento
        """
        return sorted(self._category_dict.keys())
    
    def get_built_in_categories(self):
        """Obtem as BuiltInCategories das categorias definidas na classe
        
        Returns:
            dict: Dicionário com nomes de categorias e suas BuiltInCategory correspondentes
        """
        result = {}
        for cat_name in self.common_categories:
            if cat_name in self._category_dict:
                category = self._category_dict[cat_name]
                # Obtém a BuiltInCategory a partir do ID de categoria
                built_in_cat = BuiltInCategory(category.Id.IntegerValue)
                result[cat_name] = built_in_cat
        return result
    
    def get_built_in_categories_from_list(self, category_names):
        """Obtém BuiltInCategories para uma lista de nomes de categorias
        
        Args:
            category_names (list): Lista de nomes de categorias
            
        Returns:
            dict: Dicionário com nomes de categorias e suas BuiltInCategory correspondentes
        """
        result = []
        for cat_name in category_names:
            if cat_name in self._category_dict:
                category = self._category_dict[cat_name]
                # Obtém a BuiltInCategory a partir do ID de categoria
                built_in_cat = BuiltInCategory(category.Id.IntegerValue)
                result.append(built_in_cat)

        return result
    
    def print_category_info(self, category_name):
        """Imprime informações sobre uma categoria específica
        
        Args:
            category_name (str): Nome da categoria
        """
        if category_name not in self._category_dict:
            print("Categoria não encontrada: {}".format(category_name))
            return
            
        cat = self._category_dict[category_name]
        built_in_cat = BuiltInCategory(cat.Id.IntegerValue)
        
        print("Categoria: {}".format(cat.Name))
        print("ID: {}".format(cat.Id.IntegerValue))
        print("BuiltInCategory: {}".format(built_in_cat))
        print("Está visível nas vistas: {}".format(cat.AllowsBoundParameters))



class select_item_combobox(Window):
    """
    Classe genérica para seleção de opções em um combobox.
    Permite escolher entre qualquer lista de opções fornecida pelo usuário.
    """
    def __init__(self, 
                 options_list, 
                 title="Selecionar Opção", 
                 button_text="Confirmar", 
                 label_text="Item",  # Novo parâmetro para o texto da label
                 default_option=None,
                 options_map=None, 
                 xaml_path=None,
                 auto_show=True):
        """
        Inicializa o formulário de seleção de opção.
        
        Args:
            options_list: Lista de opções a serem exibidas no combobox
            title: Título da janela
            button_text: Texto do botão de confirmação
            label_text: Texto da label acima do combobox
            default_option: Opção selecionada por padrão
            options_map: Dicionário que mapeia cada opção exibida para um valor real
            xaml_path: Caminho personalizado para o arquivo XAML (None = usar padrão)
            auto_show: Se True, exibe automaticamente o formulário
        """
        # Definir caminho do XAML
        if xaml_path is None:
            PATH_SCRIPT = os.path.dirname(__file__)
            xaml_path = os.path.join(PATH_SCRIPT, "select_item.xaml")
        
        # Carregar XAML
        wpf.LoadComponent(self, xaml_path)
        
        # Configurar propriedades da janela
        self.Title = title
        self.UIe_button.Content = button_text
        
        # Definir o texto da label (assumindo que a label se chama UIe_label no XAML)
        # Se o nome da label for diferente, altere "UIe_label" para o nome correto
        if hasattr(self, "UIe_label"):
            self.UIe_label.Text = label_text
        
        # Inicializar resultado
        self.selected_value = None
        
        # Armazenar o mapeamento de opções
        self.options_map = options_map or {}
        
        # Preencher o ComboBox com as opções
        if isinstance(options_list, list):
            options_display = sorted([str(option) for option in options_list])
            for option in options_display:
                self.UIe_combobox.Items.Add(option)
        else:
            self.UIe_combobox.Items.Add("Nenhuma opção disponível")
        
        # Definir a seleção padrão
        if default_option and str(default_option) in self.UIe_combobox.Items:
            self.UIe_combobox.SelectedItem = str(default_option)
        elif self.UIe_combobox.Items.Count > 0:
            self.UIe_combobox.SelectedItem = self.UIe_combobox.Items[0]
        
        # Mostrar o formulário automaticamente se solicitado
        if auto_show:
            self.ShowDialog()
    
    def UIE_button_run(self, sender, e):
        """Ação ao clicar no botão de confirmação."""
        selected_text = self.UIe_combobox.SelectedItem
        
        if selected_text:
            # Se houver um mapeamento para a opção selecionada, use-o
            if selected_text in self.options_map:
                self.selected_value = self.options_map[selected_text]
            else:
                self.selected_value = selected_text
        
        self.Close()