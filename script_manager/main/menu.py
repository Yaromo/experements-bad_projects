import dearpygui.dearpygui as dpg


def setting():
    pass


def menu(window_height, window_width, viewport):
    with dpg.menu_bar():
        with dpg.menu(label='Settings'):
            setting()
        
        with dpg.menu(label='Modes'):
            dpg.add_menu_item(label='programs', callback=programs, user_data=(window_height, window_width, viewport))
            dpg.add_menu_item(label='monitoring', callback=monitoring, user_data=(window_height, window_width, viewport))
            dpg.add_menu_item(label='scripting', callback=scripting, user_data=(window_height, window_width, viewport))

def monitoring(sender, app_data, user_data):
    dpg.configure_item('scripting_window', show=False)
    dpg.configure_item('programs_window', show=False)
    dpg.configure_item('monitoring_window', show=True)
    dpg.configure_viewport(user_data[2], height=user_data[0], width=user_data[1], title='monitoring')


def scripting(sender, app_data, user_data):
    dpg.configure_item('scripting_window', show=True)
    dpg.configure_item('programs_window', show=False)
    dpg.configure_item('monitoring_window', show=False)
    dpg.configure_viewport(user_data[2], height=int(user_data[0] * 1.5), width=user_data[1] * 2, title='scripting')


def programs(sender, app_data, user_data):
    dpg.configure_item('scripting_window', show=False)
    dpg.configure_item('programs_window', show=True)
    dpg.configure_item('monitoring_window', show=False)
    dpg.configure_viewport(user_data[2], height=user_data[0], width=user_data[1], title='programs')