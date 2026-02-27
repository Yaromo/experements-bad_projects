from random import randint
import dearpygui.dearpygui as dpg

global dct
dct = {'input_txt1': 0, 'input_txt2': 0}

def callback_random(sender, app_data, user_data):
    dpg.configure_item('random_num', default_value=randint(*sorted(dct.values())))
    
        
def callback_txt(sender):
    txt = dpg.get_value(sender)
    if txt and txt.isdigit():
        dct[sender] = int(txt)

dpg.create_context()

window_width = 600
window_height = 200

dpg.create_viewport(height=window_height, width=window_width, resizable=False)


with dpg.window(label='Script_manager', height=window_height, width=window_width, no_collapse=True, no_resize=True, no_close=True, tag='main_window', no_move=True, pos=(0, 0)):
    dpg.add_text(default_value='random_integer')
    with dpg.group(horizontal=True):
        with dpg.group():
            input_txt1 = dpg.add_input_text(decimal=True, callback=callback_txt, tag='input_txt1', default_value=0)
            input_txt2 = dpg.add_input_text(decimal=True, callback=callback_txt, tag='input_txt2', default_value=0)
        with dpg.group():
            dpg.add_text(default_value='- max')
            dpg.add_text(default_value='- min')
            
    dpg.add_separator()    
    dpg.add_button(label='start', callback=callback_random, user_data=(dpg.get_value('max'), dpg.get_value('min')))
    dpg.add_text(default_value='???', tag='random_num')
    
    
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()