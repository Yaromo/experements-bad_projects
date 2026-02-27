import datetime


def update(parent, dpg):
    dpg.configure_item(f'{parent}_lab', default_value=str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')))


def start(parent, dpg):
    dpg.add_text(default_value=datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'), tag=f'{parent}_lab', parent=parent)
    return update