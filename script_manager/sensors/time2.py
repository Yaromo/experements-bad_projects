import datetime


def update(parent, dpg):
    dpg.configure_item(f'{parent}_lab', default_value=str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')))

