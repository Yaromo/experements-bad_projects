import sqlite3
import requests
import sys
from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtWidgets import (QApplication, QLabel, QLineEdit, QMainWindow, QPushButton, QWidget,
                             QDialog, QVBoxLayout, QDialogButtonBox, QScrollArea)


# глобальные переменные
global Window, dialog


# основное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # не изменяемый размер окна
        self.setFixedSize(800, 600)

        # площадь для скролла
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(0, 0, 800, 600))
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)

        # виджет с контентом для scrollArea
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 765, 559))

        # макет виджета с контентом
        self.verticalLayoutWidget = QWidget(self.scrollAreaWidgetContents)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 750, 200))
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        # кнопка для добавления контента в макет
        self.add_url_btn = QPushButton('Добавить url', self.verticalLayoutWidget)
        self.add_url_btn.setObjectName(u"pushButton")
        self.add_url_btn.setMinimumSize(QSize(100, 50))
        self.add_url_btn.clicked.connect(self.add_url)

        # объединение qwidgets
        self.verticalLayout.addWidget(self.add_url_btn)
        self.setCentralWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        # обработка базы данных и их вывод
        self.set_data()

        # диалог для добавления контента
    def add_url(self):
        global dialog
        dialog = DialogAddUrl()
        dialog.show()
        self.set_data()

        # обработка базы данных и их вывод
    def set_data(self):
        while self.verticalLayout.count() > 1:  # Пока в макете есть больше одного элемент
            item = self.verticalLayout.takeAt(1)  # Извлекаем элемент
            if item.widget():  # Если у элемента есть виджет
                item.widget().deleteLater()

        # Подключение к БД
        con = sqlite3.connect('../checker/base.sqlite')

        # Создание курсора
        cur = con.cursor()

        try:
            # Полученние url
            data = cur.execute('''SELECT url FROM urls''')
        except:
            cur.execute(f'''CREATE TABLE IF NOT EXISTS urls (url TEXT NOT NULL)''')
            data = []

        # добавление информации о url
        for url in data:
            url_info = UrlInfo()
            url_info.label.setText(url[0])
            url_info.set_data()
            self.verticalLayout.addWidget(url_info)

        # подключение макета к контенту scrollArea
        self.scrollAreaWidgetContents.setLayout(self.verticalLayout)

        # закрытие доступа к базе данных
        con.close()


# диалог для добавления url
class DialogAddUrl(QDialog):
    def __init__(self):
        super().__init__()
        # не изменяемый размер окна
        self.setFixedSize(300, 300)

        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget.setGeometry(QRect(70, 10, 168, 281))

        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout_2")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label_3")
        self.label.setMaximumSize(QSize(200, 50))
        self.label.setText(u"<html><head/><body><p align=\"center\">\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u0441\u0430\u0439\u0442</p></body></html>")

        self.lineEdit = QLineEdit(self.verticalLayoutWidget)
        self.lineEdit.setObjectName(u"lineEdit_3")

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.accepted.connect(self.on_ok_clicked)
        self.buttonBox.rejected.connect(self.on_cancel_clicked)

        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.lineEdit)
        self.verticalLayout.addWidget(self.buttonBox)

    # если нажата кнопка ok
    def on_ok_clicked(self):
        res = url_check(self.lineEdit.text())
        if not res:
            self.lineEdit.setText('Неправильное url')
        else:
            add_url(self.lineEdit.text())
            Window.set_data()
            self.accept()

    # если нажата кнопка cancel
    def on_cancel_clicked(self):
        self.reject()


# вывод информации о url
class UrlInfo(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(650, 200)
        self.setMinimumSize(QSize(650, 200))

        self.label = QLabel(self)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 650, 20))

        self.del_data = QPushButton('Удалить url', self)
        self.del_data.setObjectName(u"pushButton")
        self.del_data.setGeometry(QRect(19, 120, 350, 20))
        self.del_data.clicked.connect(self.del_url)

        self.update_data = QPushButton('Обновить данные', self)
        self.update_data.setObjectName(u"pushButton")
        self.update_data.setGeometry(QRect(400, 120, 350, 20))
        self.update_data.clicked.connect(self.set_data)

        self.label_2 = QLabel(self)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(17, 60, 431, 20))

    def set_data(self):
        dct_codes = {'4': 'Ошибка со стороны клиента', '1': 'Обработка',
                     '2': 'Доступен', '3': 'Перенаправлен запрос', '5': 'Ошибка сервера'}
        res = url_check(self.label.text())
        if res:
            self.label_2.setText(f'Статус: {dct_codes[str(res)[11]]}')
        else:
            self.label_2.setText(f'Статус: Ошибка доступа к сайту')

    def del_url(self):
        del_url(self.label.text())
        Window.set_data()
        self.close()


def get_sqlbase(url):
    con = sqlite3.connect('../../Рабочий стол/checker/base.sqlite')

    # Создание курсора
    cur = con.cursor()

    # Создание таблицы с трекерами домена по имени домена
    data = cur.execute('''SELECT * FROM urls
WHERE url = ?''', (url, ))

    return data


    # проверка на правильность url
def url_check(url):
    try:
        res = requests.get(url)
    except:
        return False
    return res


def add_url(url): # добавить url

    # Подключение к БД
    con = sqlite3.connect('../../Рабочий стол/checker/base.sqlite')

    # Создание курсора
    cur = con.cursor()

    # Создание таблицы с трекерами домена по имени домена
    cur.execute(f'''CREATE TABLE IF NOT EXISTS urls (url TEXT NOT NULL)''')

    # вписать данные
    cur.execute('''INSERT INTO urls(url) VALUES (?)''', (url,))

    # сохранение изменений
    con.commit()

    # закрытие базы данных
    con.close()


    # удаление url из базы данных
def del_url(url):
    # Подключение к БД
    con = sqlite3.connect('../../Рабочий стол/checker/base.sqlite')

    # Создание курсора
    cur = con.cursor()

    # удаление
    cur.execute('''DELETE FROM urls
WHERE url = ?''', (url, ))

    # сохранение изменений
    con.commit()

    # закрытие базы данных
    con.close()


    # функция запуска
def run():
    app = QApplication(sys.argv)
    global Window
    Window = MainWindow()
    Window.show()
    sys.exit(app.exec())


    # запуск файла
if __name__ == '__main__':
    run()