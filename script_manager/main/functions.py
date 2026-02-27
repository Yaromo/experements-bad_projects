import os
import json
import dearpygui.dearpygui as dpg
import sys
import subprocess
import importlib.util
import datetime


def list_of_files(name_directory, filtering=0):
    try:
        abspath = os.path.abspath(name_directory)
        if filtering:
            return list(filter(lambda x: os.path.isfile(f'{abspath}/{x}'), os.listdir(name_directory)))
        return list(filter(lambda x: os.path.isdir(f'{abspath}/{x}'), os.listdir(name_directory)))
    except:
        return False
    

def check_directory(name_directory):
    try:
        os.mkdir(path=f'{name_directory}')
        return []
    except:
        return os.path.abspath(name_directory)


def import_function_from_file(file_path, func_name):
    # Генерируем уникальное имя модуля по пути файла
    try:
        module_name = os.path.splitext(os.path.basename(file_path))[0]

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Получаем функцию из модуля по имени
        func = getattr(module, func_name)
        return func
    except:
        return False


def start_file_for_user(sender, app_data, user_data):
    if os.path.isfile(user_data):
        try:  # добавить асинхроность или в другой поток
            venv_python = os.path.join(sys.prefix, 'bin', 'python')
            subprocess.Popen([venv_python, user_data])
            dpg.configure_item('error_user_program', default_value='Succes!')
        except:
            dpg.configure_item('error_user_program', default_value='Error')
    else:
        dpg.configure_item('error_user_program', default_value='Error')
    
    
global update_lst
update_lst = []    

def update_monitoring():
    global update_lst
    update_lst.clear()
    del_childrens('monitoring')
    abs_name_monitoring = check_directory('sensors')
    if abs_name_monitoring:
        mon_list = list_of_files(abs_name_monitoring, 1)
        for i in enumerate(mon_list):
            dpg.add_collapsing_header(label=i[1], tag=f'{i[1]}-head', parent='monitoring')
            func = import_function_from_file(f'{abs_name_monitoring}/{i[1]}', 'start')
            if func:
                update_lst.append([import_function_from_file(f'{abs_name_monitoring}/{i[1]}', 'start')(f'{i[1]}-head', dpg), f'{i[1]}-head'])
            else:
                dpg.add_text(default_value='error', parent=f'{i[1]}-head')
                


def btn_callback_mon(sender, app_data, user_data):
    update_monitoring()  
    
    
def start_scripting(sender, app_data, user_data): # node_dct, links
    dpg.add_text(parent='console', default_value='start')
    global links
      # лучше переписать здесь все через граф и рекурсию, но мне интересней написать без этого
    files = {}
    abs_name_scripts = check_directory('scripts')
    for i in dpg.get_item_children('nodes')[1]:
        files[dpg.get_item_label(i)] = {}
        for j in links.keys():
            if links[j][1] in dpg.get_item_children(i)[1] and dpg.get_item_label(i) != 'start':
                parent = dpg.get_item_label(dpg.get_item_parent(links[j][0])) if dpg.get_item_label(dpg.get_item_parent(links[j][0])) != 'start' else links[j][0]
                files[dpg.get_item_label(i)]['input'] = files[dpg.get_item_label(i)].setdefault('input', []) + [parent]
            elif links[j][0] in dpg.get_item_children(i)[1] and dpg.get_item_label(i) != 'end':
                parent = dpg.get_item_label(dpg.get_item_parent(links[j][1])) if dpg.get_item_label(dpg.get_item_parent(links[j][1])) != 'start' else links[j][1]
                files[dpg.get_item_label(i)]['output'] = files[dpg.get_item_label(i)].setdefault('output', []) + [parent]
    flag = True
    num_result = 0
    for i in files.keys():
        if i not in ('start', 'end') and files[i].keys():
            num_result += 1
    m = 0
    while flag and m < 1000 and num_result > 0:
        for i in files.keys():
            if i not in ('start', 'end') and files[i].keys() and 'result' not in files[i].keys():
                data = []
                if 'input' in files[i].keys():
                    for j in files[i]['input']:
                        if isinstance(j, str):
                            if 'result' not in files[j].keys():
                                break
                            data.append(files[j]['result'])
                        else:
                            data.append(dct_inputs[dpg.get_item_label(j)])
                result = run_script(f'{abs_name_scripts}/{i[:i.index('.py')+3]}', *data)
                if not result:
                    flag = False
                    break
                files[i]['result'] = result
                num_result -= 1
        m += 1
    if m == 1000:
        dpg.add_text(parent='console', default_value='many iterations') 
        dpg.add_text(parent='console', default_value='stop')   
    else:
        dpg.add_text(parent='console', default_value=f'-------------------------------result-------------------------------')     
        for i in files['end']['input']:
            if isinstance(i, str):
                if 'result' in files[i].keys():
                    dpg.add_text(parent='console', default_value=f'from {i} - {files[i]['result']}')
                else:
                    dpg.add_text(parent='console', default_value=f'from {i} - nothing')
            else:
                dpg.add_text(parent='console', default_value=f'from {dpg.get_item_label(i)} - {dct_inputs[dpg.get_item_label(i)]}')
 
    
def run_script(script_path, *args):
    """
    Запускает другой Python скрипт как отдельный процесс.

    Args:
        script_path:  Путь к запускаемому Python файлу.
        *args:  Список аргументов, передаваемых в запускаемый скрипт.
    """
    try:
        # Формируем команду для запуска скрипта
        arguments = import_function_from_file(script_path, 'arguments')
        lst = []
        if args and arguments:
            arguments = arguments()
            for i in range(min([len(arguments), len(args)])):
                lst.append(f'{arguments[i]}={args[i]}')
            venv_python = os.path.join(sys.prefix, 'bin', 'python')
            command = [venv_python, script_path] + lst
            # Запускаем процесс и ожидаем его завершения
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            # Выводим stdout и stderr
            dpg.add_text(parent='console', default_value=f"Output from {script_path}:\n{result.stdout}")
            dpg.add_text(parent='console', default_value=f"Errors from {script_path}:\n{result.stderr}")
            #print(result.stdout)
            if result.stdout:
                return result.stdout
    except subprocess.CalledProcessError as e:
        dpg.add_text(parent='console', default_value=f"Error running {script_path}: {e}")
        dpg.add_text(parent='console', default_value=f"Output from {script_path}:\n{e.stdout}")
        dpg.add_text(parent='console', default_value=f"Errors from {script_path}:\n{e.stderr}")
        #print(f"Error running {script_path}: {e}", f"Output from {script_path}:\n{e.stdout}", f"Errors from {script_path}:\n{e.stderr}")
    return False


def update_list_of_programs(group, filtering=0):
    abs_name_scripts = check_directory(f'{group}s')
    if abs_name_scripts:
        lst_scripts = list_of_files(abs_name_scripts, filtering)
        if lst_scripts:
            for i in enumerate(lst_scripts):
                dpg.add_button(tag=f'Btn{i[0]}-{group}s', label=i[1], width=275, parent=group, user_data=f'{abs_name_scripts}/{i[1]}/start.py', callback=start_file_for_user) # создать функцию callback
        else:
            dpg.add_text(default_value=f'No {group}s', tag=f'{group}s_lab', parent=group)
    else:
        dpg.add_text(label=f'No {group}s', tag=f'{group}s_lab', parent=group)
    
    
def update_list_of_scripts(group, filtering=0):
    abs_name_scripts = check_directory(f'{group}s')
    if abs_name_scripts:
        lst_scripts = list_of_files(abs_name_scripts, filtering)
        if lst_scripts:
            for i in enumerate(lst_scripts):
                dpg.add_group(horizontal=True, tag=f'Group{i[0]}-{group}s', parent=group)
                dpg.add_text(tag=f'Text{i[0]}-{group}s', default_value=i[1], parent=f'Group{i[0]}-{group}s') # создать функцию callback
                dpg.add_button(label='+', parent=f'Group{i[0]}-{group}s', callback=add_node, user_data=(abs_name_scripts, i[1], 'nodes'))
        else:
            dpg.add_text(default_value=f'No {group}s', tag=f'{group}s_lab', parent=group)
    else:
        dpg.add_text(label=f'No {group}s', tag=f'{group}s_lab', parent=group)    
    dpg.configure_item('program_list_counter', default_value=f'number of programs - {len(dpg.get_item_children('program'))}')
      
      
def del_childrens(group):
    for i in dpg.get_item_children(group)[1]:
        dpg.delete_item(i)
      
      
def update_scripts(sender, app_data, user_data):
    del_childrens(user_data)
    update_list_of_scripts(user_data, 1)  
 
 
def update():
    if dpg.get_item_configuration('scripting_window')['show']:
        pass
    
    if dpg.get_item_configuration('monitoring_window')['show']:
        global update_lst
        for i in update_lst:
            if i[0] is not None:
                i[0](i[1], dpg)
                
    if dpg.get_item_configuration('programs_window')['show']:
        dpg.configure_item('date_time_lab', default_value=str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')))     
      
      
global nodes
nodes = {}     
      
def add_node(sender, app_data, user_data):
    if user_data[1] not in nodes.keys():
        nodes[user_data[1]] = set()
        
    diff = set([f'{user_data[1]}{i}' for i in range(len(nodes[user_data[1]]) + 1)]).difference(nodes[user_data[1]])
    name = min(diff, key=lambda x: int(x[len(user_data[1]):]))
    nodes[user_data[1]].add(name)
        
    with dpg.node(parent=user_data[2], label=name, tag=name):
        with dpg.node_attribute(label="Node A1"):
            dpg.add_text(default_value='input')

        with dpg.node_attribute(label="Node A2", attribute_type=dpg.mvNode_Attr_Output):
            dpg.add_text(default_value='output')
            
        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
            dpg.add_button(label='delete', callback=delete_node_button, user_data=name)       
        

global inputs, dct_inputs
inputs = 0
dct_inputs = dict()

def add_input(sender, app_data, user_data):
    global inputs
    inputs += 1
    with dpg.node_attribute(parent=user_data, attribute_type=dpg.mvNode_Attr_Output, tag=f'attribute-input-{inputs}', label=f'input-{inputs}'):
        dpg.add_input_text(tag=f'input-{inputs}', width=282, callback=callback_txt)
    dct_inputs[f'input-{inputs}'] = ''


def del_input(sender, app_data):
    global inputs
    if inputs:
        dpg.delete_item(f'attribute-input-{inputs}')
        del dct_inputs[f'input-{inputs}']
        inputs -= 1
        

def callback_txt(sender):
    dct_inputs[sender] = dpg.get_value(sender)


def delete_node_button(sender, app_data, user_data):
    dpg.delete_item(user_data)
    for i in range(-1, -len(user_data), -1):
        if not user_data[i].isdigit():
            nodes[user_data[:i + 1]].remove(user_data)
            break


def update_button_callback(sender, app_data, user_data):
    del_childrens(user_data)
    update_list_of_programs(user_data)      


def load_data_from_json(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except:
        return False


def load_data_from_txt(name_file):
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            data = file.read()
        return data
    except:
        return False
    

global links
links = {}


# callback runs when user attempts to connect attributes
def link_callback(sender, app_data):
    # app_data -> (link_id1, link_id2)
    global links
    dpg.add_node_link(app_data[0], app_data[1], parent=sender)
    links[list(set(dpg.get_item_children(sender)[0]).difference(set(links.keys())))[0]] = (app_data[0], app_data[1])
    
# callback runs when user attempts to disconnect attributes
def delink_callback(sender, app_data):
    # app_data -> link_id
    global links
    del links[app_data]
    dpg.delete_item(app_data)