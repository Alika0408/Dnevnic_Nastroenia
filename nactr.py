import sys
import sqlite3
import hashlib
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon, QPixmap
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


def create_connection(database):
    # Создает соединение с базой данных.
    return sqlite3.connect(database)


def create_tables():
    # Создает необходимые таблицы в базе данных.
    with create_connection('mood_diary.db') as conn:
        cursor = conn.cursor()

        # Создание таблицы пользователей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')

        # Создание таблицы настроений
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood TEXT NOT NULL,
            comment TEXT,
            question_answer TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Создание таблицы вопросов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            date TEXT NOT NULL UNIQUE
        )
        ''')

        # Добавление вопросов, если их еще нет
        questions = [
            "Что сегодня сделало вас счастливым?",
            "Какое ваше главное достижение сегодня?",
            "Что вы могли бы улучшить в своем дне?",
            "Какое ваше любимое воспоминание?",
            "Что вас сегодня вдохновляет?",
            "Как вам погода сегодня на улице?",
            "Что вызывало у вас радость сегодня?",
            "Что новое вы узнали за сегодня?",
            "Что вам сегодня снилось?",
            "Из-за чего вы сегодня расстраивались?",
            "Что сегодня вас заставило улыбнуться?",
            "Какая сегодняшняя ситуация запоминалась вам?",
            "Что сегодня удивило?",
            "Какой урок вы извлекли из сегодняшнего дня?",
            "Какая часть вашего дня была самой продуктивной?",
            "Чем вы гордитесь в конце дня?"
        ]

        for question in questions:
            cursor.execute("INSERT OR IGNORE INTO questions (question, date) VALUES (?, '')", (question,))


class MainWindowUi(object):
    # Класс для настройки главного окна приложения.

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 540)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.error_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.error_label.setGeometry(QtCore.QRect(50, 330, 371, 31))
        self.error_label.setText("")
        self.error_label.setObjectName("error_label")

        # Создание сплиттеров для организации интерфейса
        self.main_splitter = QtWidgets.QSplitter(parent=self.centralwidget)
        self.main_splitter.setGeometry(QtCore.QRect(46, 105, 731, 161))
        self.main_splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)

        self.left_splitter = QtWidgets.QSplitter(parent=self.main_splitter)
        self.left_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)

        self.username_label = QtWidgets.QLabel(parent=self.left_splitter)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.username_label.setFont(font)

        self.password_label = QtWidgets.QLabel(parent=self.left_splitter)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.password_label.setFont(font)

        self.right_splitter = QtWidgets.QSplitter(parent=self.main_splitter)
        self.right_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)

        self.username_input = QtWidgets.QLineEdit(parent=self.right_splitter)
        self.password_input = QtWidgets.QLineEdit(parent=self.right_splitter)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.button_splitter = QtWidgets.QSplitter(parent=self.centralwidget)
        self.button_splitter.setGeometry(QtCore.QRect(0, 435, 781, 111))
        self.button_splitter.setOrientation(QtCore.Qt.Orientation.Vertical)

        self.login_button = QtWidgets.QPushButton(parent=self.button_splitter)
        self.register_button = QtWidgets.QPushButton(parent=self.button_splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        MainWindow.setWindowIcon(QIcon('Иконка.svg'))  # добавление иконки

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Дневник настроения"))
        self.username_label.setText(_translate("MainWindow", "Логин"))
        self.password_label.setText(_translate("MainWindow", "Пароль"))
        self.login_button.setText(_translate("MainWindow", "Вход"))
        self.register_button.setText(_translate("MainWindow", "Регистрация"))


class MoodDiaryApp(QtWidgets.QMainWindow, MainWindowUi):
    # Основной класс приложения для управления входом и регистрацией пользователей.

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Подключаем кнопки к методам
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.open_register_window)

        # Обработка нажатия клавиши Enter
        self.username_input.returnPressed.connect(self.login)  # Нажатие Enter в поле логина
        self.password_input.returnPressed.connect(self.login)  # Нажатие Enter в поле пароля

        self.is_open = False  # Флаг для отслеживания состояния окна

    def open_register_window(self):
        # Метод для открытия окна регистрации.
        if not self.is_open:
            self.is_open = True
            self.register_window = RegisterWindow()  # Создаем экземпляр окна регистрации
            self.register_window.exec()  # Открываем окно регистрации как диалог
            self.is_open = False  # Сбрасываем флаг после закрытия окна

    def login(self):
        # Метод для обработки входа пользователя.
        username = self.username_input.text().strip()
        password = self.password_input.text()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if not username or not password:
            self.error_label.setText("Пожалуйста, заполните все поля.")
            return

        with create_connection('mood_diary.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
            user = cursor.fetchone()

            if user:
                self.error_label.setText("Успешный вход!")
                self.current_user_id = user[0]
                self.open_main_menu()  # открываем меню
                self.close()  # Закрываем текущее окно
            else:
                self.error_label.setText("Неверное имя пользователя или пароль.")

    def open_main_menu(self):
        # Открывает главное меню приложения.
        self.main_menu = Menu(self.current_user_id)
        self.main_menu.show()  # Показываем окно Меню


class RegisterWindow(QtWidgets.QDialog):
    # Класс для окна регистрации нового пользователя.

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setGeometry(100, 100, 400, 300)

        self.username_label = QtWidgets.QLabel("Логин:", self)
        self.username_label.setGeometry(50, 50, 100, 30)
        self.username_input = QtWidgets.QLineEdit(self)
        self.username_input.setGeometry(150, 50, 200, 30)

        self.password_label = QtWidgets.QLabel("Пароль:", self)
        self.password_label.setGeometry(50, 100, 100, 30)
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setGeometry(150, 100, 200, 30)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.register_button = QtWidgets.QPushButton("Зарегистрироваться", self)
        self.register_button.setGeometry(150, 150, 200, 30)
        self.register_button.clicked.connect(self.register)

        self.status_label = QtWidgets.QLabel("", self)
        self.status_label.setGeometry(50, 200, 300, 30)

        self.setWindowIcon(QIcon('Иконка.svg'))

        # Обработка нажатия клавиши Enter
        self.username_input.returnPressed.connect(self.register)  # Нажатие Enter в поле логина
        self.password_input.returnPressed.connect(self.register)  # Нажатие Enter в поле пароля

    def register(self):
        # Метод для регистрации нового пользователя.
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        if not username or not password:
            self.status_label.setText("Пожалуйста, заполните все поля.")
            return

        with create_connection('mood_diary.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                self.status_label.setText("Регистрация успешна!")
                QtCore.QTimer.singleShot(500, self.close)  # Закрываем окно через 0.5 секунды после успешной регистрации
            except sqlite3.IntegrityError:
                self.status_label.setText("Пользователь с таким именем уже существует.")
            except Exception as e:
                self.status_label.setText(f"Ошибка: {e}")


class MoodDiaryWindow(QtWidgets.QMainWindow):
    # Класс для окна добавления записей о настроении.

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setGeometry(0, 0, 935, 876)
        self.setWindowTitle("Дневник настроения")
        self.setWindowIcon(QIcon('Иконка.svg'))

        # Создаем кнопку "Сохранить"
        self.save_button = QtWidgets.QPushButton("Сохранить", self)
        self.save_button.setGeometry(400, 750, 121, 41)
        self.save_button.setFont(QtGui.QFont("", 10))
        self.save_button.clicked.connect(self.save_mood)

        # Создаем горизонтальный сплиттер для выбора настроения
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        self.splitter.setGeometry(10, 60, 861, 22)

        # Создаем метку для выбора настроения
        self.mood_label = QtWidgets.QLabel("Выберите настроение:", self.splitter)
        self.mood_label.setFont(QtGui.QFont("", 9))

        # Создаем комбобокс для выбора настроения
        self.mood_combo = QtWidgets.QComboBox(self.splitter)
        moods = [
            "-",
            "Самый счастливый человек на земле",
            "Счастливое",
            "Удовлетворенное",
            "Нейтральное",
            "Слегка подавленное",
            "Раздосадованное",
            "Тревожный",
            "Грустное",
            "Подавленное",
            "Ужасное"
        ]
        self.mood_combo.addItems(moods)
        self.mood_combo.currentIndexChanged.connect(self.update_mood_description)

        # Создаем метку для описания настроения
        self.mood_description_label = QtWidgets.QLabel(self.splitter)
        self.mood_description_label.setText("")

        # Создаем вертикальный сплиттер для комментариев
        self.comment_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical, self)
        self.comment_splitter.setGeometry(10, 110, 861, 331)

        # Создаем метку комментария
        self.comment_label = QtWidgets.QLabel("Комментарий:", self.comment_splitter)
        self.comment_label.setFont(QtGui.QFont("", 9))

        # Создаем текстовое поле для комментария
        self.comment_input = QtWidgets.QTextEdit(self.comment_splitter)
        self.comment_input.setFont(QtGui.QFont("", 9))

        # Создаем метку для вопроса
        self.question_label = QtWidgets.QLabel("Вопрос дня:", self.comment_splitter)
        self.question_label.setFont(QtGui.QFont("", 9))

        # Создаем текстовое поле для ответа на вопрос
        self.answer_input = QtWidgets.QTextEdit(self.comment_splitter)
        self.answer_input.setFont(QtGui.QFont("", 9))

        # Загружаем вопрос дня
        self.load_daily_question()

    def save_mood(self):
        # Метод для сохранения настроения в базе данных.
        mood = self.mood_combo.currentText()
        comment = self.comment_input.toPlainText()
        answer = self.answer_input.toPlainText()
        date = datetime.now().strftime("%d-%m-%Y")

        if mood == "-":
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите настроение.")
            return

        with create_connection('mood_diary.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO moods (user_id, mood, comment, question_answer, date) VALUES (?, ?, ?, ?, ?)",
                           (self.user_id, mood, comment, answer, date))
            conn.commit()

        QtWidgets.QMessageBox.information(self, "Успех", "Ваше настроение сохранено.")
        self.clear_fields()  # Очищаем поля после сохранения
        self.close()  # Закрываем окно после успешного сохранения

    def update_mood_description(self):
        # Обновляет описание настроения в зависимости от выбора.
        mood_descriptions = {
            "Самый счастливый человек на земле": "Высшее счастье.",
            "Счастливое": "Счастливое состояние.",
            "Удовлетворенное": "Чувство удовлетворения.",
            "Нейтральное": "Нейтральное состояние.",
            "Слегка подавленное": "Небольшое беспокойство.",
            "Раздосадованное": "Чувство раздражения.",
            "Тревожный": "Беспокойное настроение.",
            "Грустное": "Печальное ощущение.",
            "Подавленное": "Угнетенное состояние.",
            "Ужасное": "Крайнее страдание."
        }
        selected_mood = self.mood_combo.currentText()
        description = mood_descriptions.get(selected_mood, "")
        self.mood_description_label.setText(description)  # Устанавливаем текст описания настроения

    def clear_fields(self):
        # Очищает поля ввода.
        self.mood_combo.setCurrentIndex(0)  # Сбрасываем выбор настроения
        self.comment_input.clear()  # Очищаем текстовое поле комментария
        self.answer_input.clear()  # Очищаем текстовое поле ответа на вопрос

    def load_daily_question(self):
        # Загружает вопрос дня из базы данных.
        with create_connection('mood_diary.db') as conn:
            cursor = conn.cursor()

            # Получаем текущую дату
            today = datetime.now().date()
            cursor.execute("SELECT question FROM questions WHERE date = ?", (today,))
            question = cursor.fetchone()

            if question:
                self.question_label.setText(question[0])  # Устанавливаем вопрос дня
            else:
                # Если вопрос не установлен на сегодня, выбираем случайный вопрос
                cursor.execute("SELECT question FROM questions ORDER BY RANDOM() LIMIT 1")
                random_question = cursor.fetchone()
                if random_question:
                    self.question_label.setText(random_question[0])  # Устанавливаем случайный вопрос
                    # Устанавливаем вопрос на сегодня
                    cursor.execute("INSERT OR REPLACE INTO questions (question, date) VALUES (?, ?)",
                                   (random_question[0], today))
                    conn.commit()


class Menu(QtWidgets.QMainWindow):
    # Класс для главного меню приложения.

    def __init__(self, user_id):
        # Инициализация главного меню.
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Меню")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('Иконка.svg'))

        # Создаем QLabel для отображения иконки приложения
        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setGeometry(350, 10, 100, 100)  # Установите размеры и позицию по своему усмотрению
        self.icon_label.setPixmap(
            QPixmap('Иконка.svg').scaled(100, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio))  # Установите иконку

        self.history_button = QtWidgets.QPushButton("Показать историю настроений", self)
        self.history_button.setGeometry(250, 120, 300, 40)
        self.history_button.clicked.connect(self.show_history)  # Подключаем кнопку к методу показа истории

        self.plot_button = QtWidgets.QPushButton("Показать график настроений", self)
        self.plot_button.setGeometry(250, 170, 300, 40)
        self.plot_button.clicked.connect(self.show_plot)  # Подключаем кнопку к методу показа графика

        self.add_entry_button = QtWidgets.QPushButton("Добавить запись", self)
        self.add_entry_button.setGeometry(250, 220, 300, 40)
        self.add_entry_button.clicked.connect(
            self.open_mood_diary_window)  # Подключаем кнопку к методу добавления записи

        self.question_button = QtWidgets.QPushButton("Вопрос дня", self)
        self.question_button.setGeometry(250, 270, 300, 40)
        self.question_button.clicked.connect(
            self.show_daily_question)  # Подключаем кнопку к методу показа вопроса дня

        self.close_button = QtWidgets.QPushButton("Закрыть", self)
        self.close_button.setGeometry(250, 320, 300, 40)
        self.close_button.clicked.connect(self.close)  # Подключаем кнопку к закрытию приложения

    def open_mood_diary_window(self):
        # Метод для открытия окна добавления записи о настроении.
        self.mood_diary_window = MoodDiaryWindow(self.user_id)  # Создаем экземпляр окна добавления настроений
        self.mood_diary_window.show()  # Показываем окно добавления настроений

    def show_history(self):
        # Отображает историю настроений пользователя.
        with create_connection('mood_diary.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date, mood, comment FROM moods WHERE user_id=?", (self.user_id,))
            records = cursor.fetchall()  # Получаем все записи настроений пользователя

            history_text = ""
            for record in records:
                history_text += f"{record[0]}: {record[1]} - {record[2]}\n"  # Форматируем текст истории

            if not history_text:
                history_text = "Нет записей о настроении."  # Сообщение, если записей нет

            QtWidgets.QMessageBox.information(self, "История настроений", history_text)  # Показываем сообщение

    def show_plot(self):
        # Отображает график настроений пользователя.
        with create_connection('mood_diary.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT date, mood FROM moods WHERE user_id=?", (self.user_id,))
            records = cursor.fetchall()  # Получаем все записи настроений

            if not records:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Нет записей о настроении для построения графика.")
                return  # Если нет записей, показываем предупреждение

            dates = [record[0] for record in records]  # Извлекаем даты записей
            moods = [record[1] for record in records]  # Извлекаем настроения

            # Определяем значения для настроений
            mood_values = {
                "Самый счастливый человек на земле": 5,
                "Счастливое": 4,
                "Удовлетворенное": 3,
                "Нейтральное": 2,
                "Слегка подавленное": 1,
                "Раздосадованное": 0,
                "Тревожный": -1,
                "Грустное": -2,
                "Подавленное": -3,
                "Ужасное": -4
            }

            mood_scores = [mood_values.get(mood, 0) for mood in moods]  # Преобразуем настроения в числовые значения
            x = np.arange(len(dates))  # Определяем ось X для графика

            # Построение графика
            plt.bar(x, mood_scores, align='center')
            plt.xticks(x, dates, rotation=45)  # Устанавливаем метки по оси X
            plt.xlabel('Дата')  # Подпись оси X
            plt.ylabel('Оценка настроения')  # Подпись оси Y
            plt.title('График настроений')  # Заголовок графика
            plt.axhline(0, color='black', linewidth=0.8)  # Горизонтальная линия на уровне 0
            plt.grid(axis='y')  # Включаем сетку по оси Y
            plt.show()  # Показываем график

    def show_daily_question(self):
        # Отображает вопрос дня.
        with create_connection('mood_diary.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT question FROM questions WHERE date = ?", (datetime.now().date(),))
            question = cursor.fetchone()  # Получаем вопрос дня

            if question:
                QtWidgets.QMessageBox.information(self, "Вопрос дня", question[0])  # Показываем вопрос
            else:
                QtWidgets.QMessageBox.warning(self, "Ошибка",
                                              "Нет доступного вопроса на сегодня.")  # Предупреждение, если вопроса нет


if __name__ == "__main__":
    create_tables()  # Создание таблиц при запуске приложения
    app = QtWidgets.QApplication(sys.argv)
    window = MoodDiaryApp()
    window.show()
    sys.exit(app.exec())
