import dearpygui.dearpygui as dpg
from functions import *
import datetime
from menu import *
        

def start():
    dpg.create_context()

    window_width = 600
    window_height = 600

    viewport = dpg.create_viewport(height=window_height, width=window_width, resizable=False, title='programs')


    with dpg.window(label='Script_manager', height=window_height, width=window_width, no_collapse=True, no_resize=True, no_close=True, tag='programs_window', no_move=True, pos=(0, 0)):
        menu(window_height, window_width, viewport)
                
        with dpg.group(horizontal=True, horizontal_spacing=5):   
            with dpg.child_window(width=290, height=500, tag='program'):
                update_list_of_programs('program')
                
            with dpg.group(width=290):

                dpg.add_text(default_value=f'number of programs: {len(dpg.get_item_children('program'))}', tag='program_list_counter')
                dpg.add_text(default_value=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), tag='date_time_lab')
                dpg.add_button(label='update', width=285, callback=update_button_callback, user_data='program')
                dpg.add_text(tag='error_user_program')        
            
                
    with dpg.window(label='Script_manager', height=window_height, width=window_width, no_collapse=True, no_resize=True, no_close=True, tag='monitoring_window', no_move=True, pos=(0, 0), show=False):
        menu(window_height, window_width, viewport)  
        dpg.add_button(label='update', callback=btn_callback_mon)
        with dpg.group(tag='monitoring'):
            update_monitoring()
                            
                
    with dpg.window(label='Script_manager', height=int(window_height * 1.5), width=window_width * 2, no_collapse=False, no_resize=True, no_close=True, tag='scripting_window', no_move=True, pos=(0, 0), show=False):
        menu(window_height, window_width, viewport)   
        
        with dpg.group(horizontal_spacing=2):
            with dpg.group(horizontal=True, horizontal_spacing=2): 
                with dpg.node_editor(callback=link_callback, delink_callback=delink_callback, width=int(window_width * 1.45), height=window_height, minimap=True, minimap_location=3, tag='nodes'):
                    with dpg.node(label='start', tag='start'):
                        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                            with dpg.group(horizontal=True, horizontal_spacing=2, label='buttons'): 
                                dpg.add_button(label='add_input', callback=add_input, user_data='start', width=140)
                                dpg.add_button(label='del_input', callback=del_input, width=140)
                                
                    with dpg.node(label='end', tag='end'):
                        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input):
                            dpg.add_text(default_value='output')
                
                with dpg.child_window(height=window_height, tag='script'):
                    update_list_of_scripts('script', 1)
                        
                graf = [] # мне лень делать класс для единичного случая, хотя надо
        with dpg.group(horizontal=True):
            with dpg.group():
                dpg.add_button(label='update', callback=update_scripts, user_data='script')
                dpg.add_button(label='start', callback=start_scripting)
                dpg.add_button(label='clear console', callback=lambda x, y, z: del_childrens(z), user_data='console')
                
            with dpg.child_window(tag='console'):
                pass
                
    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():

        update()
            
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
    
    