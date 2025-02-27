import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from PIL import Image, ImageTk, ImageDraw, ImageFont
from datetime import datetime
import shutil
import random

class UserProfile:
    def __init__(self, root, user_id=1):
        self.root = root
        self.root.title("Jyldam jauap - Профиль пользователя")
        self.root.geometry("900x700")
        self.user_id = user_id
        self.edit_mode = False
        self.current_tab = "profile"  # Текущая активная вкладка
        
        # Настройка темы и цветов
        self.setup_theme()
        
        # Подключение к базе данных
        self.setup_database()
        
        # Создание UI
        self.create_ui()
        
        # Загрузка данных пользователя
        self.load_user_data()
        
        # Создание папки для изображений профиля, если не существует
        if not os.path.exists("images/profile"):
            os.makedirs("images/profile", exist_ok=True)
    
    def setup_theme(self):
        # Обновленная цветовая схема (соответствует главному меню)
        self.primary_color = "#B71C1C"  # Темно-красный
        self.secondary_color = "#212121"  # Почти черный
        self.accent_color = "#F44336"  # Более яркий красный для акцентов
        self.bg_color = "#F5F5F5"  # Светло-серый фон
        self.card_bg = "#FFFFFF"  # Белый фон для карточек
        self.text_color = "#212121"  # Текст темный для карточек
        self.text_light = "#FFFFFF"  # Белый текст для темного фона
        self.border_color = "#E0E0E0"  # Светло-серая рамка
        self.success_color = "#4CAF50"  # Зеленый для успешных действий
        self.warning_color = "#FFC107"  # Желтый для предупреждений
        self.inactive_tab = "#EEEEEE"  # Светло-серый для неактивных вкладок
        
        # Конфигурация стилей ttk
        self.style = ttk.Style()
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('Card.TFrame', background=self.card_bg)
        
        self.style.configure('TLabel', background=self.card_bg, foreground=self.text_color, font=('Helvetica', 11))
        self.style.configure('Header.TLabel', background=self.card_bg, foreground=self.primary_color, font=('Helvetica', 16, 'bold'))
        self.style.configure('Title.TLabel', background=self.bg_color, foreground=self.primary_color, font=('Helvetica', 18, 'bold'))
        self.style.configure('Small.TLabel', background=self.card_bg, foreground=self.text_color, font=('Helvetica', 9))
        self.style.configure('Info.TLabel', background=self.primary_color, foreground=self.text_light, font=('Helvetica', 11))
        
        # Стили вкладок
        self.style.configure('Tab.TFrame', background=self.inactive_tab)
        self.style.configure('ActiveTab.TFrame', background=self.card_bg)
        self.style.configure('Tab.TLabel', background=self.inactive_tab, foreground=self.text_color, font=('Helvetica', 11))
        self.style.configure('ActiveTab.TLabel', background=self.card_bg, foreground=self.primary_color, font=('Helvetica', 11, 'bold'))
        
        # Стили кнопок
        self.style.configure('TButton', font=('Helvetica', 11))
        self.style.map('Primary.TButton',
            background=[('active', self.accent_color), ('!active', self.primary_color)],
            foreground=[('active', 'white'), ('!active', 'white')])
        self.style.map('Accent.TButton',
            background=[('active', self.accent_color), ('!active', self.secondary_color)],
            foreground=[('active', 'white'), ('!active', 'white')])
        self.style.map('Success.TButton',
            background=[('active', '#388E3C'), ('!active', self.success_color)],
            foreground=[('active', 'white'), ('!active', 'white')])
        
        # Стили для Entry
        self.style.configure('TEntry', background="white", foreground=self.text_color, fieldbackground="white")
        
        # Конфигурирация корневого окна
        self.root.configure(bg=self.bg_color)
    
    def setup_database(self):
        # Убедимся, что директория db существует
        os.makedirs("db", exist_ok=True)
        
        # Подключение к базе данных
        self.conn = sqlite3.connect('db/users.db')
        self.cursor = self.conn.cursor()
        
        # Проверяем существующую структуру таблицы users
        self.cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        # Если таблица users не существует, создаем её с новой структурой
        if not columns:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    iin TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    city TEXT,
                    address TEXT,
                    role TEXT DEFAULT 'client',
                    profile_image TEXT,
                    rating REAL DEFAULT 0,
                    cases_completed INTEGER DEFAULT 0,
                    registration_date TEXT
                )
            ''')
        else:
            # Добавляем недостающие столбцы, если они отсутствуют
            if 'address' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
            if 'profile_image' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")
            if 'rating' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN rating REAL DEFAULT 0")
            if 'cases_completed' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN cases_completed INTEGER DEFAULT 0")
            if 'registration_date' not in columns:
                self.cursor.execute("ALTER TABLE users ADD COLUMN registration_date TEXT")
        
        # Создание таблицы услуг, если она не существует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                service_name TEXT NOT NULL,
                description TEXT,
                price REAL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Создание таблицы активности, если она не существует
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                activity_type TEXT NOT NULL,
                description TEXT,
                timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Проверка, нужно ли добавить образцы данных
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] == 0:
            self.add_sample_data()
        
        self.conn.commit()
    
    def add_sample_data(self):
        # Добавление образцов пользователей
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        sample_users = [
            ('Алексей Иванов', '123456789012', 'alexey@example.com', '+7-705-123-4567', 'Астана', 
             'ул. Сатпаева 11, кв. 42', 'client', None, 0, 0, current_date),
            ('Мария Смирнова', '234567890123', 'maria@lawfirm.com', '+7-777-987-6543', 'Алматы', 
             'ул. Абая 25, офис 301', 'lawyer', None, 4.8, 24, current_date),
            ('Нурлан Серіков', '345678901234', 'nurlan@example.com', '+7-701-456-7890', 'Шымкент', 
             'мкр. Асар 5, дом 12', 'client', None, 0, 0, current_date),
            ('Гүлнар Ахметова', '456789012345', 'gulnar@legalaid.org', '+7-775-234-5678', 'Астана', 
             'пр. Республики 67, офис 405', 'lawyer', None, 4.9, 31, current_date)
        ]
        
        self.cursor.executemany('''
            INSERT INTO users (name, iin, email, phone, city, address, role, profile_image, rating, cases_completed, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_users)
        
        # Добавление образцов услуг для юристов
        self.cursor.execute("SELECT id FROM users WHERE role = 'lawyer'")
        lawyer_ids = [row[0] for row in self.cursor.fetchall()]
        
        sample_services = []
        for lawyer_id in lawyer_ids:
            sample_services.extend([
                (lawyer_id, 'Первичная консультация', 'Первичная встреча для обсуждения юридических вопросов', 10000.00),
                (lawyer_id, 'Проверка документов', 'Юридическая экспертиза договоров и документов', 15000.00),
                (lawyer_id, 'Представительство в суде', 'Представление интересов в судебном процессе', 50000.00)
            ])
        
        self.cursor.executemany('''
            INSERT INTO services (user_id, service_name, description, price)
            VALUES (?, ?, ?, ?)
        ''', sample_services)
        
        # Добавление образцов активности
        sample_activities = []
        for user_id in range(1, 5):
            # Для каждого пользователя добавим 5 действий
            for i in range(5):
                if i % 2 == 0:
                    activity_type = "login"
                    description = "Вход в систему"
                else:
                    activity_type = "update_profile"
                    description = "Обновление профиля"
                
                # Генерируем случайную дату в прошлом месяце
                day = random.randint(1, 28)
                hour = random.randint(8, 20)
                minute = random.randint(0, 59)
                timestamp = f"2025-01-{day:02d} {hour:02d}:{minute:02d}:00"
                
                sample_activities.append((user_id, activity_type, description, timestamp))
        
        self.cursor.executemany('''
            INSERT INTO activities (user_id, activity_type, description, timestamp)
            VALUES (?, ?, ?, ?)
        ''', sample_activities)
    
    def create_ui(self):
        # Шапка в стиле главного меню
        header = tk.Frame(self.root, bg=self.primary_color, height=80)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # Логотип в шапке
        try:
            logo_img = Image.open("images/logo.png")
            logo_img = logo_img.resize((50, 50), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header, image=logo_photo, bg=self.primary_color)
            logo_label.image = logo_photo  # Сохраняем ссылку
            logo_label.pack(side="left", padx=10, pady=10)
        except:
            # Если изображение не найдено, используем текстовую иконку
            logo_label = tk.Label(header, text="JJ", font=("Helvetica", 18, "bold"), 
                                 fg=self.primary_color, bg="white", width=3, height=1)
            logo_label.pack(side="left", padx=10, pady=10)

        title = tk.Label(header, text="JYLDAM JAUAP", font=("Helvetica", 24, "bold"), 
                        fg=self.text_light, bg=self.primary_color)
        title.pack(side="left", pady=20)

        subtitle = tk.Label(header, text="Профиль пользователя", font=("Helvetica", 12), 
                          fg=self.text_light, bg=self.primary_color)
        subtitle.pack(side="left", padx=10, pady=20)

        # Текущая дата
        current_date = datetime.now().strftime("%d.%m.%Y")
        date_label = tk.Label(header, text=current_date, font=("Helvetica", 12), 
                             fg=self.text_light, bg=self.primary_color)
        date_label.pack(side="right", padx=20, pady=20)
        
        # Основной контейнер с прокруткой для длинного контента
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Добавляем холст для прокрутки
        self.canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=885)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Основной контейнер в прокручиваемой области
        self.main_container = ttk.Frame(scrollable_frame, style='TFrame')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Создаем вкладки навигации
        self.create_tabs()
        
        # Контейнер для содержимого вкладок
        self.content_container = ttk.Frame(self.main_container, style='TFrame')
        self.content_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Инициализируем содержимое для всех вкладок
        self.create_profile_tab()
        self.create_services_tab()
        self.create_activity_tab()
        self.create_settings_tab()
        
        # По умолчанию показываем профиль
        self.show_tab("profile")
        
        # Кнопка назад
        back_button = ttk.Button(self.main_container, text="← Назад в главное меню", 
                                command=self.go_back_to_main, style='Accent.TButton')
        back_button.pack(pady=15, anchor="w")
    
    def create_tabs(self):
        # Создаем панель навигации с вкладками
        tabs_frame = tk.Frame(self.main_container, bg=self.bg_color)
        tabs_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Словарь для хранения фреймов и меток вкладок
        self.tabs = {}
        
        # Список вкладок: (id, название, иконка)
        tab_info = [
            ("profile", "Профиль", "👤"),
            ("services", "Услуги", "🛎️"),
            ("activity", "Активность", "📋"),
            ("settings", "Настройки", "⚙️")
        ]
        
        # Создаем вкладки
        for i, (tab_id, tab_name, icon) in enumerate(tab_info):
            tab_frame = ttk.Frame(tabs_frame, style='Tab.TFrame', padding=(10, 5))
            tab_frame.pack(side=tk.LEFT, padx=5)
            
            label_text = f"{icon} {tab_name}"
            tab_label = ttk.Label(tab_frame, text=label_text, style='Tab.TLabel')
            tab_label.pack(padx=10, pady=5)
            
            # Сохраняем ссылки на фрейм и метку
            self.tabs[tab_id] = {"frame": tab_frame, "label": tab_label}
            
            # Добавляем обработчик нажатия
            tab_frame.bind("<Button-1>", lambda e, tid=tab_id: self.show_tab(tid))
            tab_label.bind("<Button-1>", lambda e, tid=tab_id: self.show_tab(tid))
    
    def show_tab(self, tab_id):
        """Переключение между вкладками"""
        # Сначала скрываем все содержимое вкладок
        for frame_id in ["profile_content", "services_content", "activity_content", "settings_content"]:
            if hasattr(self, frame_id):
                getattr(self, frame_id).pack_forget()
        
        # Обновляем стили всех вкладок как неактивные
        for tab in self.tabs.values():
            tab["frame"].configure(style='Tab.TFrame')
            tab["label"].configure(style='Tab.TLabel')
            # Явно устанавливаем цвет фона для меток вкладок
            tab["label"].configure(background=self.inactive_tab)
        
        # Делаем выбранную вкладку активной
        self.tabs[tab_id]["frame"].configure(style='ActiveTab.TFrame')
        self.tabs[tab_id]["label"].configure(style='ActiveTab.TLabel')
        # Явно устанавливаем цвет фона для активной метки
        self.tabs[tab_id]["label"].configure(background=self.card_bg)
        
        # Показываем содержимое выбранной вкладки
        frame_id = f"{tab_id}_content"
        if hasattr(self, frame_id):
            getattr(self, frame_id).pack(fill=tk.BOTH, expand=True)
        
        # Обновляем текущую вкладку
        self.current_tab = tab_id
    
    def create_profile_tab(self):
        """Создает содержимое вкладки профиля"""
        self.profile_content = ttk.Frame(self.content_container, style='TFrame')
        
        # Карточка профиля с рамкой
        profile_card = tk.Frame(self.profile_content, bg=self.border_color, padx=2, pady=2, relief=tk.RAISED)
        profile_card.pack(fill=tk.BOTH, expand=True)
        
        # Содержимое карточки
        card = ttk.Frame(profile_card, style='Card.TFrame')
        card.pack(fill=tk.BOTH, expand=True)
        
        # Верхняя секция с изображением профиля
        top_section = ttk.Frame(card, style='Card.TFrame')
        top_section.pack(fill=tk.X, padx=30, pady=30)
        
        # Контейнер изображения профиля
        image_container = ttk.Frame(top_section, style='Card.TFrame')
        image_container.pack(side=tk.LEFT)
        
        # Заполнитель для изображения профиля
        self.profile_image_frame = tk.Frame(image_container, bg=self.card_bg)
        self.profile_image_frame.pack(padx=10)
        
        self.profile_image_label = ttk.Label(self.profile_image_frame, background=self.card_bg)
        self.profile_image_label.pack()
        
        # Кнопка изменения фото (появляется в режиме редактирования)
        self.change_photo_btn = ttk.Button(self.profile_image_frame, text="Изменить фото", 
                                         command=self.change_profile_photo, style='Accent.TButton')
        
        # Контейнер информации о пользователе
        info_container = ttk.Frame(top_section, style='Card.TFrame')
        info_container.pack(side=tk.LEFT, padx=20, fill=tk.X, expand=True)
        
        # Имя и роль
        self.name_var = tk.StringVar()
        self.role_var = tk.StringVar()
        name_label = ttk.Label(info_container, textvariable=self.name_var, style='Header.TLabel')
        name_label.pack(anchor=tk.W)
        role_label = ttk.Label(info_container, textvariable=self.role_var, style='TLabel')
        role_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Статистика (для юристов)
        self.stats_frame = ttk.Frame(info_container, style='Card.TFrame')
        self.stats_frame.pack(anchor=tk.W, pady=10, fill=tk.X)
        
        # Создаем переменные для статистики
        self.rating_var = tk.StringVar(value="0.0")
        self.cases_var = tk.StringVar(value="0")
        self.since_var = tk.StringVar(value="")
        
        # Будет заполнено в load_user_data
        
        # Контейнер кнопок
        button_container = ttk.Frame(top_section, style='Card.TFrame')
        button_container.pack(side=tk.RIGHT)
        
        self.edit_button = ttk.Button(button_container, text="Изменить профиль", 
                                     command=self.toggle_edit_mode, style='Primary.TButton')
        self.edit_button.pack(padx=5, pady=5)
        
        self.save_button = ttk.Button(button_container, text="Сохранить изменения", 
                                     command=self.save_changes, style='Primary.TButton')
        self.save_button.pack(padx=5, pady=5)
        self.save_button.config(state=tk.DISABLED)
        
        # Разделитель
        ttk.Separator(card, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=30, pady=10)
        
        # Секция деталей
        details_section = ttk.Frame(card, style='Card.TFrame')
        details_section.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Создаем переменные полей
        self.iin_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.city_var = tk.StringVar()
        self.address_var = tk.StringVar()
        
        # Создаем поля деталей
        self.create_field(details_section, 'IIN', self.iin_var)
        self.create_field(details_section, 'Email', self.email_var)
        self.create_field(details_section, 'Телефон', self.phone_var)
        self.create_field(details_section, 'Город', self.city_var)
        self.create_field(details_section, 'Адрес', self.address_var)
    
    def create_field(self, parent, label_text, string_var):
        """Создает строку поля с меткой и значением/полем ввода"""
        frame = ttk.Frame(parent, style='Card.TFrame')
        frame.pack(fill=tk.X, pady=10)
        
        # Метка (явно устанавливаем цвет фона)
        label = ttk.Label(frame, text=f"{label_text}:", width=10, anchor=tk.W, style='TLabel')
        label.configure(background=self.card_bg)
        label.pack(side=tk.LEFT)
        
        # Метка значения (для режима просмотра, явно устанавливаем цвет фона)
        value_label = ttk.Label(frame, textvariable=string_var, style='TLabel')
        value_label.configure(background=self.card_bg, foreground=self.text_color)
        value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        setattr(self, f"{label_text.lower()}_label", value_label)
        
        # Поле ввода (для режима редактирования)
        entry = ttk.Entry(frame, textvariable=string_var, width=30)
        setattr(self, f"{label_text.lower()}_entry", entry)
        # Поле ввода будет отображено только в режиме редактирования
    
    def create_services_tab(self):
        """Создает содержимое вкладки услуг"""
        self.services_content = ttk.Frame(self.content_container, style='TFrame')
        
        # Заголовок
        header_frame = ttk.Frame(self.services_content, style='TFrame')
        header_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(header_frame, text="Услуги и расценки", style='Title.TLabel').pack(side=tk.LEFT)
        
        # Кнопка добавления услуги (видима только для юристов)
        self.add_service_button = ttk.Button(header_frame, text="+ Добавить услугу", 
                                           command=self.add_service, style='Primary.TButton')
        self.add_service_button.pack(side=tk.RIGHT)
        
        # Фрейм для списка услуг
        self.services_list_frame = ttk.Frame(self.services_content, style='Card.TFrame')
        self.services_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Контейнер услуг будет заполнен в load_services
    
    def create_activity_tab(self):
        """Создает содержимое вкладки активности"""
        self.activity_content = ttk.Frame(self.content_container, style='TFrame')
        
        # Заголовок
        ttk.Label(self.activity_content, text="История активности", style='Title.TLabel').pack(anchor=tk.W, pady=10)
        
        # Фильтры и поиск
        filter_frame = ttk.Frame(self.activity_content, style='TFrame')
        filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filter_frame, text="Фильтр:", style='TLabel', background=self.bg_color).pack(side=tk.LEFT, padx=5)
        
        self.activity_filter = ttk.Combobox(filter_frame, values=["Все действия", "Вход в систему", "Обновление профиля", "Другое"])
        self.activity_filter.pack(side=tk.LEFT, padx=5)
        self.activity_filter.current(0)
        self.activity_filter.bind("<<ComboboxSelected>>", self.filter_activity)
        
        # Контейнер для временной шкалы активности
        self.timeline_container = tk.Frame(self.activity_content, bg=self.bg_color)
        self.timeline_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Содержимое будет загружено в load_activity
    
    def create_settings_tab(self):
        """Создает содержимое вкладки настроек"""
        self.settings_content = ttk.Frame(self.content_container, style='TFrame')
        
        # Заголовок
        ttk.Label(self.settings_content, text="Настройки аккаунта", style='Title.TLabel').pack(anchor=tk.W, pady=10)
        
        # Карточка настроек безопасности
        security_card = tk.Frame(self.settings_content, bg=self.border_color, padx=2, pady=2)
        security_card.pack(fill=tk.X, pady=10)
        
        security_content = ttk.Frame(security_card, style='Card.TFrame', padding=15)
        security_content.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок раздела
        ttk.Label(security_content, text="Безопасность", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        # Изменение пароля
        password_frame = ttk.Frame(security_content, style='Card.TFrame')
        password_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(password_frame, text="Изменение пароля", style='TLabel').pack(anchor=tk.W)
        
        change_pass_btn = ttk.Button(password_frame, text="Изменить пароль", 
                                   command=self.change_password, style='Accent.TButton')
        change_pass_btn.pack(anchor=tk.W, pady=5)
        
        # Настройки приватности
        privacy_card = tk.Frame(self.settings_content, bg=self.border_color, padx=2, pady=2)
        privacy_card.pack(fill=tk.X, pady=10)
        
        privacy_content = ttk.Frame(privacy_card, style='Card.TFrame', padding=15)
        privacy_content.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок раздела
        ttk.Label(privacy_content, text="Приватность", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        # Опции приватности с переключателями
        privacy_options = [
            "Показывать мой профиль в публичном доступе",
            "Разрешить отправку уведомлений на email",
            "Получать новости и обновления"
        ]
        
        self.privacy_vars = []
        
        for option in privacy_options:
            var = tk.BooleanVar(value=True)
            self.privacy_vars.append(var)
            
            option_frame = ttk.Frame(privacy_content, style='Card.TFrame')
            option_frame.pack(fill=tk.X, pady=5)
            
            chk = ttk.Checkbutton(option_frame, text=option, variable=var, style='TCheckbutton')
            chk.pack(anchor=tk.W)
        
        # Кнопка сохранения настроек
        save_settings_btn = ttk.Button(self.settings_content, text="Сохранить настройки", 
                                     command=self.save_settings, style='Primary.TButton')
        save_settings_btn.pack(anchor=tk.E, pady=10)
        
        # Кнопка выхода из аккаунта
        logout_btn = ttk.Button(self.settings_content, text="Выйти из аккаунта", 
                               command=self.logout, style='Accent.TButton')
        logout_btn.pack(anchor=tk.W, pady=10)
    
    def change_profile_photo(self):
        """Изменяет фото профиля"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Изображения", "*.jpg *.jpeg *.png")]
        )
        
        if not file_path:
            return
            
        try:
            # Создаем копию изображения в нашей директории
            user_image_dir = "images/profile"
            os.makedirs(user_image_dir, exist_ok=True)
            
            # Имя файла на основе ID пользователя
            file_ext = os.path.splitext(file_path)[1]
            new_filename = f"user_{self.user_id}{file_ext}"
            new_file_path = os.path.join(user_image_dir, new_filename)
            
            # Открываем и изменяем размер изображения
            img = Image.open(file_path)
            img = img.resize((120, 120), Image.LANCZOS)
            img.save(new_file_path)
            
            # Обновляем путь к изображению в базе данных
            self.cursor.execute("UPDATE users SET profile_image = ? WHERE id = ?",
                             (new_file_path, self.user_id))
            self.conn.commit()
            
            # Обновляем изображение в интерфейсе
            self.load_profile_image(new_file_path)
            
            # Добавляем активность
            self.add_activity("update_profile", "Изменение фото профиля")
            
            # Уведомление
            self.show_notification("Фото профиля успешно обновлено", "success")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить фото профиля: {str(e)}")
    
    def load_profile_image(self, image_path=None):
        """Загружает изображение профиля или создает аватар с инициалами"""
        if image_path and os.path.exists(image_path):
            try:
                # Загружаем изображение из файла
                img = Image.open(image_path)
                img = img.resize((120, 120), Image.LANCZOS)
                
                # Создаем круглое изображение
                mask = Image.new('L', (120, 120), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 120, 120), fill=255)
                
                # Применяем маску
                result = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
                result.paste(img, (0, 0), mask)
                
                # Преобразуем в PhotoImage и сохраняем ссылку
                self.profile_photo = ImageTk.PhotoImage(result)
                self.profile_image_label.config(image=self.profile_photo)
                return
            except Exception as e:
                print(f"Ошибка загрузки изображения: {str(e)}")
        
        # Если фото нет или не удалось загрузить, создаем аватар с инициалами
        self.create_profile_image(self.name_var.get())
    
    def create_profile_image(self, name):
        """Создает изображение профиля с инициалами пользователя"""
        # Извлекаем инициалы
        parts = name.split()
        if len(parts) >= 2:
            initials = parts[0][0] + parts[1][0]
        else:
            initials = name[0] if name else "U"
        
        try:
            # Создаем круглый аватар
            size = 120
            image = Image.new('RGB', (size, size), color=self.primary_color)
            draw = ImageDraw.Draw(image)
            
            # Добавляем текст
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                # Если шрифт не найден, используем стандартный
                try:
                    font = ImageFont.load_default()
                except:
                    # Если и это не сработало, создаем простую метку
                    self.profile_image_label.config(image="")
                    self.profile_image_label.config(
                        text=initials, 
                        font=("Helvetica", 24, "bold"),
                        foreground="white",
                        background=self.primary_color,
                        width=4, height=2
                    )
                    return
            
            # Рисуем текст
            try:
                text_width, text_height = draw.textbbox((0, 0), initials, font=font)[2:4]
                position = ((size - text_width) / 2, (size - text_height) / 2)
                draw.text(position, initials, font=font, fill="white")
                
                # Преобразуем в PhotoImage и сохраняем ссылку
                self.profile_photo = ImageTk.PhotoImage(image)
                self.profile_image_label.config(image=self.profile_photo)
            except Exception as e:
                print(f"Ошибка при создании изображения: {str(e)}")
                # Запасной вариант - текстовая метка
                self.profile_image_label.config(
                    text=initials, 
                    font=("Helvetica", 24, "bold"),
                    foreground="white",
                    background=self.primary_color,
                    width=4, height=2
                )
        except Exception as e:
            print(f"Ошибка при создании аватара: {str(e)}")
            # Если всё плохо, создаем простую текстовую метку
            self.profile_image_label.config(
                text=initials, 
                font=("Helvetica", 24, "bold"),
                foreground="white",
                background=self.primary_color,
                width=4, height=2
            )
    
    def load_user_data(self):
        """Загружает данные пользователя из базы данных"""
        try:
            # Получаем список колонок в таблице users
            self.cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # Формируем SQL запрос в зависимости от наличия колонок
            # Начинаем с базовых колонок
            select_columns = "name, iin, email, phone, city, role"
            
            # Добавляем дополнительные колонки, если они есть
            if 'address' in columns:
                select_columns += ", address"
            else:
                select_columns += ", ''"  # Пустая строка для address
                
            if 'profile_image' in columns:
                select_columns += ", profile_image"
            else:
                select_columns += ", NULL"  # NULL для profile_image
                
            if 'rating' in columns:
                select_columns += ", rating"
            else:
                select_columns += ", 0"  # 0 для rating
                
            if 'cases_completed' in columns:
                select_columns += ", cases_completed"
            else:
                select_columns += ", 0"  # 0 для cases_completed
                
            if 'registration_date' in columns:
                select_columns += ", registration_date"
            else:
                select_columns += ", ''"  # Пустая строка для registration_date
            
            # Запрос данных пользователя
            query = f"SELECT {select_columns} FROM users WHERE id = ?"
            self.cursor.execute(query, (self.user_id,))
            
            user = self.cursor.fetchone()
            
            if not user:
                messagebox.showerror("Ошибка", f"Пользователь с ID {self.user_id} не найден")
                return
            
            # Устанавливаем значения
            name, iin, email, phone, city, role, address, profile_image, rating, cases_completed, registration_date = user
            
            self.name_var.set(name)
            self.iin_var.set(iin)
            self.email_var.set(email if email else "")
            self.phone_var.set(phone if phone else "")
            self.city_var.set(city if city else "")
            self.address_var.set(address if address else "")
            
            # Перевод роли на русский
            role_translation = {"lawyer": "Юрист", "client": "Клиент"}
            self.role_var.set(role_translation.get(role.lower(), role.capitalize()))
            
            # Статистика для юристов
            if role.lower() == 'lawyer':
                # Показываем статистику
                self.create_lawyer_stats(rating, cases_completed, registration_date)
                
                # Загружаем услуги
                self.load_services()
                
                # Показываем кнопку добавления услуги
                self.add_service_button.pack(side=tk.RIGHT)
            else:
                # Очищаем фрейм статистики
                for widget in self.stats_frame.winfo_children():
                    widget.destroy()
                
                # Скрываем кнопку добавления услуги
                self.add_service_button.pack_forget()
                
                # Добавляем информацию для клиентов
                client_info = ttk.Label(self.stats_frame, text="Статус: Активный клиент", 
                                     style='TLabel', background=self.card_bg)
                client_info.pack(side=tk.LEFT, padx=5)
                
                # Отображаем с какой даты клиент с нами
                if registration_date:
                    since_label = ttk.Label(self.stats_frame, 
                                         text=f"С нами с {registration_date}", 
                                         style='Small.TLabel', background=self.card_bg)
                    since_label.pack(side=tk.LEFT, padx=10)
                    
            # Загружаем изображение профиля
            self.load_profile_image(profile_image)
            
            # Загружаем активность
            self.load_activity()
                
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
    
    def create_lawyer_stats(self, rating, cases_completed, registration_date):
        """Создает статистику для юриста"""
        # Очищаем фрейм статистики
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Рейтинг с звездами
        rating_frame = ttk.Frame(self.stats_frame, style='Card.TFrame')
        rating_frame.pack(side=tk.LEFT, padx=10)
        
        rating_label = ttk.Label(rating_frame, text="Рейтинг: ", style='TLabel', background=self.card_bg)
        rating_label.pack(side=tk.LEFT)
        
        # Отображаем рейтинг звездами
        stars_frame = ttk.Frame(rating_frame, style='Card.TFrame')
        stars_frame.pack(side=tk.LEFT)
        
        for i in range(5):
            if i < int(rating):
                star = "★"  # Полная звезда
                color = "#FFD700"  # Золотой
            elif i < rating:
                star = "★"  # Полная звезда для дробной части
                color = "#FFD700"  # Золотой
            else:
                star = "☆"  # Пустая звезда
                color = "#AAAAAA"  # Серый
                
            star_label = tk.Label(stars_frame, text=star, font=("Helvetica", 12), 
                                fg=color, bg=self.card_bg)
            star_label.pack(side=tk.LEFT)
        
        # Числовой рейтинг
        rating_number = tk.Label(stars_frame, text=f"({rating})", font=("Helvetica", 10), 
                                fg="#888888", bg=self.card_bg)
        rating_number.pack(side=tk.LEFT, padx=5)
        
        # Разделитель
        separator = ttk.Separator(self.stats_frame, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Количество дел
        cases_frame = ttk.Frame(self.stats_frame, style='Card.TFrame')
        cases_frame.pack(side=tk.LEFT, padx=10)
        
        cases_label = ttk.Label(cases_frame, text=f"Завершенных дел: {cases_completed}", 
                             style='TLabel', background=self.card_bg)
        cases_label.pack(side=tk.LEFT)
        
        # Разделитель
        separator2 = ttk.Separator(self.stats_frame, orient=tk.VERTICAL)
        separator2.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Дата регистрации
        since_frame = ttk.Frame(self.stats_frame, style='Card.TFrame')
        since_frame.pack(side=tk.LEFT, padx=10)
        
        since_label = ttk.Label(since_frame, text=f"В системе с {registration_date}", 
                             style='TLabel', background=self.card_bg)
        since_label.pack(side=tk.LEFT)
    
    def load_services(self):
        """Загружает услуги пользователя"""
        try:
            # Очищаем список услуг
            for widget in self.services_list_frame.winfo_children():
                widget.destroy()
            
            # Запрашиваем услуги из базы данных
            self.cursor.execute('''
                SELECT id, service_name, description, price
                FROM services
                WHERE user_id = ?
                ORDER BY price DESC
            ''', (self.user_id,))
            
            services = self.cursor.fetchall()
            
            if not services:
                no_services_label = ttk.Label(self.services_list_frame, 
                                           text="У вас пока нет добавленных услуг", 
                                           style='TLabel', background=self.card_bg)
                no_services_label.pack(pady=20)
                return
            
            # Создаем список услуг
            for service_id, name, description, price in services:
                # Создаем карточку услуги
                service_card = tk.Frame(self.services_list_frame, bg=self.border_color, padx=2, pady=2)
                service_card.pack(fill=tk.X, pady=10)
                
                service_content = ttk.Frame(service_card, style='Card.TFrame', padding=15)
                service_content.pack(fill=tk.BOTH, expand=True)
                
                # Верхняя часть с названием и ценой
                top_frame = ttk.Frame(service_content, style='Card.TFrame')
                top_frame.pack(fill=tk.X)
                
                # Название услуги
                service_name_label = ttk.Label(top_frame, text=name, style='Header.TLabel')
                service_name_label.pack(side=tk.LEFT)
                
                # Цена
                price_frame = ttk.Frame(top_frame, style='Card.TFrame')
                price_frame.pack(side=tk.RIGHT)
                
                price_label = ttk.Label(price_frame, 
                                     text=f"{price:,.0f} KZT", 
                                     font=('Helvetica', 12, 'bold'), 
                                     foreground=self.primary_color, 
                                     background=self.card_bg)
                price_label.pack()
                
                # Описание
                description_label = ttk.Label(service_content, text=description, style='TLabel', wraplength=700)
                description_label.pack(anchor=tk.W, pady=10)
                
                # Кнопки действий
                actions_frame = ttk.Frame(service_content, style='Card.TFrame')
                actions_frame.pack(fill=tk.X, pady=5)
                
                edit_btn = ttk.Button(actions_frame, text="Изменить", 
                                    command=lambda sid=service_id: self.edit_service(sid))
                edit_btn.pack(side=tk.LEFT, padx=5)
                
                delete_btn = ttk.Button(actions_frame, text="Удалить", 
                                      command=lambda sid=service_id: self.delete_service(sid))
                delete_btn.pack(side=tk.LEFT, padx=5)
                
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
    
    def load_activity(self):
        """Загружает историю активности пользователя"""
        try:
            # Очищаем контейнер активности
            for widget in self.timeline_container.winfo_children():
                widget.destroy()
            
            # Проверяем существование таблицы activities
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activities'")
            table_exists = self.cursor.fetchone() is not None
            
            if not table_exists:
                # Создаем таблицу, если её нет
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS activities (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        activity_type TEXT NOT NULL,
                        description TEXT,
                        timestamp TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                self.conn.commit()
                
                # Добавляем начальную активность
                self.add_activity("login", "Первый вход в систему")
            
            # Запрашиваем активность из базы данных
            self.cursor.execute('''
                SELECT activity_type, description, timestamp
                FROM activities
                WHERE user_id = ?
                ORDER BY timestamp DESC
            ''', (self.user_id,))
            
            activities = self.cursor.fetchall()
            
            if not activities:
                no_activity_label = ttk.Label(self.timeline_container, 
                                           text="История активности пуста", 
                                           style='TLabel', background=self.bg_color)
                no_activity_label.pack(pady=20)
                return
            
            # Создаем временную шкалу
            for i, (activity_type, description, timestamp) in enumerate(activities):
                # Преобразуем тип активности для отображения
                type_translation = {
                    "login": "Вход в систему",
                    "update_profile": "Обновление профиля",
                    "add_service": "Добавление услуги",
                    "edit_service": "Изменение услуги",
                    "delete_service": "Удаление услуги"
                }
                
                activity_type_display = type_translation.get(activity_type, activity_type.capitalize())
                
                # Создаем элемент временной шкалы
                timeline_item = tk.Frame(self.timeline_container, bg=self.bg_color)
                timeline_item.pack(fill=tk.X, pady=5)
                
                # Левая часть с линией и точкой
                line_frame = tk.Frame(timeline_item, bg=self.bg_color, width=50)
                line_frame.pack(side=tk.LEFT, fill=tk.Y)
                
                # Точка на линии
                dot_color = self.primary_color if i == 0 else self.secondary_color
                dot = tk.Frame(line_frame, bg=dot_color, width=12, height=12)
                dot.place(relx=0.5, y=15, anchor=tk.CENTER)
                
                # Линия (кроме последнего элемента)
                if i < len(activities) - 1:
                    line = tk.Frame(line_frame, bg=self.secondary_color, width=2)
                    line.place(relx=0.5, y=15, rely=0, relheight=1, anchor=tk.N)
                
                # Карточка активности
                activity_card = tk.Frame(timeline_item, bg=self.border_color, padx=1, pady=1)
                activity_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
                
                card_content = tk.Frame(activity_card, bg=self.card_bg, padx=15, pady=10)
                card_content.pack(fill=tk.BOTH, expand=True)
                
                # Верхняя часть с типом и датой
                card_header = tk.Frame(card_content, bg=self.card_bg)
                card_header.pack(fill=tk.X)
                
                # Тип активности
                type_label = tk.Label(card_header, text=activity_type_display, 
                                    font=('Helvetica', 11, 'bold'), 
                                    fg=self.primary_color, bg=self.card_bg)
                type_label.pack(side=tk.LEFT)
                
                # Дата и время
                time_label = tk.Label(card_header, text=timestamp, 
                                    font=('Helvetica', 9), 
                                    fg="#888888", bg=self.card_bg)
                time_label.pack(side=tk.RIGHT)
                
                # Описание активности
                description_label = tk.Label(card_content, text=description, 
                                          font=('Helvetica', 10), 
                                          fg=self.text_color, bg=self.card_bg, 
                                          wraplength=600, justify=tk.LEFT)
                description_label.pack(anchor=tk.W, pady=5)
                
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
    
    def filter_activity(self, event=None):
        """Фильтрует активность по выбранному типу"""
        try:
            selected_filter = self.activity_filter.get()
            
            # Очищаем контейнер активности
            for widget in self.timeline_container.winfo_children():
                widget.destroy()
            
            # Определяем фильтр SQL в зависимости от выбора
            if selected_filter == "Все действия":
                self.cursor.execute('''
                    SELECT activity_type, description, timestamp
                    FROM activities
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                ''', (self.user_id,))
            elif selected_filter == "Вход в систему":
                self.cursor.execute('''
                    SELECT activity_type, description, timestamp
                    FROM activities
                    WHERE user_id = ? AND activity_type = 'login'
                    ORDER BY timestamp DESC
                ''', (self.user_id,))
            elif selected_filter == "Обновление профиля":
                self.cursor.execute('''
                    SELECT activity_type, description, timestamp
                    FROM activities
                    WHERE user_id = ? AND activity_type = 'update_profile'
                    ORDER BY timestamp DESC
                ''', (self.user_id,))
            else:
                # Фильтр "Другое" - исключаем известные типы
                self.cursor.execute('''
                    SELECT activity_type, description, timestamp
                    FROM activities
                    WHERE user_id = ? AND activity_type NOT IN ('login', 'update_profile')
                    ORDER BY timestamp DESC
                ''', (self.user_id,))
            
            activities = self.cursor.fetchall()
            
            if not activities:
                no_activity_label = ttk.Label(self.timeline_container, 
                                           text=f"Нет активности для фильтра '{selected_filter}'", 
                                           style='TLabel', background=self.bg_color)
                no_activity_label.pack(pady=20)
                return
            
            # Перезагружаем активность с учетом фильтра
            # Код аналогичен методу load_activity, но не повторяю его здесь для краткости
            
            # Создаем временную шкалу
            for i, (activity_type, description, timestamp) in enumerate(activities):
                # Преобразуем тип активности для отображения
                type_translation = {
                    "login": "Вход в систему",
                    "update_profile": "Обновление профиля",
                    "add_service": "Добавление услуги",
                    "edit_service": "Изменение услуги",
                    "delete_service": "Удаление услуги"
                }
                
                activity_type_display = type_translation.get(activity_type, activity_type.capitalize())
                
                # Создаем элемент временной шкалы
                timeline_item = tk.Frame(self.timeline_container, bg=self.bg_color)
                timeline_item.pack(fill=tk.X, pady=5)
                
                # Левая часть с линией и точкой
                line_frame = tk.Frame(timeline_item, bg=self.bg_color, width=50)
                line_frame.pack(side=tk.LEFT, fill=tk.Y)
                
                # Точка на линии
                dot_color = self.primary_color if i == 0 else self.secondary_color
                dot = tk.Frame(line_frame, bg=dot_color, width=12, height=12)
                dot.place(relx=0.5, y=15, anchor=tk.CENTER)
                
                # Линия (кроме последнего элемента)
                if i < len(activities) - 1:
                    line = tk.Frame(line_frame, bg=self.secondary_color, width=2)
                    line.place(relx=0.5, y=15, rely=0, relheight=1, anchor=tk.N)
                
                # Карточка активности
                activity_card = tk.Frame(timeline_item, bg=self.border_color, padx=1, pady=1)
                activity_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
                
                card_content = tk.Frame(activity_card, bg=self.card_bg, padx=15, pady=10)
                card_content.pack(fill=tk.BOTH, expand=True)
                
                # Верхняя часть с типом и датой
                card_header = tk.Frame(card_content, bg=self.card_bg)
                card_header.pack(fill=tk.X)
                
                # Тип активности
                type_label = tk.Label(card_header, text=activity_type_display, 
                                    font=('Helvetica', 11, 'bold'), 
                                    fg=self.primary_color, bg=self.card_bg)
                type_label.pack(side=tk.LEFT)
                
                # Дата и время
                time_label = tk.Label(card_header, text=timestamp, 
                                    font=('Helvetica', 9), 
                                    fg="#888888", bg=self.card_bg)
                time_label.pack(side=tk.RIGHT)
                
                # Описание активности
                description_label = tk.Label(card_content, text=description, 
                                          font=('Helvetica', 10), 
                                          fg=self.text_color, bg=self.card_bg, 
                                          wraplength=600, justify=tk.LEFT)
                description_label.pack(anchor=tk.W, pady=5)
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
    
    def toggle_edit_mode(self):
        """Переключение между режимами просмотра и редактирования"""
        self.edit_mode = not self.edit_mode
        
        # Устанавливаем состояния кнопок
        if self.edit_mode:
            self.edit_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.NORMAL)
            # Показываем кнопку изменения фото
            self.change_photo_btn.pack(pady=5)
        else:
            self.edit_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.DISABLED)
            # Скрываем кнопку изменения фото
            self.change_photo_btn.pack_forget()
        
        # Переключаем отображение полей
        for field in ['iin', 'email', 'телефон', 'город', 'адрес']:
            label = getattr(self, f"{field}_label")
            entry = getattr(self, f"{field}_entry")
            
            if self.edit_mode:
                # Переключаемся в режим редактирования
                label.pack_forget()
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                # Переключаемся в режим просмотра
                entry.pack_forget()
                label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def save_changes(self):
        """Сохраняет изменения пользователя в базе данных"""
        try:
            # Получаем список колонок в таблице users
            self.cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            # Формируем SQL запрос в зависимости от наличия колонок
            update_columns = "iin = ?, email = ?, phone = ?, city = ?"
            values = [
                self.iin_var.get(),
                self.email_var.get(),
                self.phone_var.get(),
                self.city_var.get()
            ]
            
            # Добавляем address, если колонка существует
            if 'address' in columns:
                update_columns += ", address = ?"
                values.append(self.address_var.get())
            
            # Добавляем ID пользователя в конце списка значений
            values.append(self.user_id)
            
            # Выполняем запрос
            query = f"UPDATE users SET {update_columns} WHERE id = ?"
            self.cursor.execute(query, values)
            
            self.conn.commit()
            
            # Добавляем запись об активности
            self.add_activity("update_profile", "Обновление информации профиля")
            
            # Обновляем UI
            self.toggle_edit_mode()
            
            # Показываем уведомление
            self.show_notification("Профиль успешно обновлен", "success")
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
    
    def add_service(self):
        """Открывает диалог для добавления новой услуги"""
        # Создаем всплывающее окно
        popup = tk.Toplevel(self.root)
        popup.title("Добавить новую услугу")
        popup.geometry("500x400")
        popup.configure(bg=self.bg_color)
        popup.transient(self.root)
        popup.grab_set()
        
        # Создаем заголовок для всплывающего окна
        header = tk.Frame(popup, bg=self.primary_color, height=60)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        header_title = tk.Label(header, text="Добавление услуги", font=("Helvetica", 16, "bold"), 
                               fg=self.text_light, bg=self.primary_color)
        header_title.pack(side="left", padx=20, pady=15)
        
        # Создаем контент
        content = tk.Frame(popup, bg=self.card_bg, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Поля
        # Название услуги
        name_frame = ttk.Frame(content, style='Card.TFrame')
        name_frame.pack(fill=tk.X, pady=10)
        ttk.Label(name_frame, text="Название услуги:", width=15, anchor=tk.W, background=self.card_bg).pack(side=tk.LEFT)
        service_name = tk.StringVar()
        ttk.Entry(name_frame, textvariable=service_name, width=35).pack(side=tk.LEFT, padx=5)
        
        # Описание (многострочное)
        desc_frame = ttk.Frame(content, style='Card.TFrame')
        desc_frame.pack(fill=tk.X, pady=10)
        ttk.Label(desc_frame, text="Описание:", width=15, anchor=tk.W, background=self.card_bg).pack(side=tk.LEFT, anchor="n")
        
        description_text = tk.Text(desc_frame, height=5, width=35, font=('Helvetica', 10))
        description_text.pack(side=tk.LEFT, padx=5)
        
        # Скроллбар для описания
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient="vertical", command=description_text.yview)
        desc_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        description_text.config(yscrollcommand=desc_scrollbar.set)
        
        # Цена
        price_frame = ttk.Frame(content, style='Card.TFrame')
        price_frame.pack(fill=tk.X, pady=10)
        ttk.Label(price_frame, text="Цена (KZT):", width=15, anchor=tk.W, background=self.card_bg).pack(side=tk.LEFT)
        price = tk.StringVar()
        ttk.Entry(price_frame, textvariable=price, width=35).pack(side=tk.LEFT, padx=5)
        
        # Информация
        info_frame = ttk.Frame(content, style='Card.TFrame')
        info_frame.pack(fill=tk.X, pady=10)
        
        info_label = ttk.Label(info_frame, 
                             text="После добавления услуги она станет видна клиентам в вашем профиле.", 
                             background=self.card_bg, foreground=self.secondary_color, wraplength=400,
                             font=('Helvetica', 9))
        info_label.pack(pady=10)
        
        # Кнопки
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Функции действий
        def cancel():
            popup.destroy()
            
        def save():
            # Проверка ввода
            if not service_name.get().strip():
                messagebox.showerror("Ошибка", "Название услуги обязательно")
                return
                
            try:
                price_value = float(price.get().replace(' ', '').replace(',', '.'))
                if price_value <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Ошибка", "Цена должна быть положительным числом")
                return
                
            # Получаем текст описания
            description = description_text.get("1.0", tk.END).strip()
                
            # Сохраняем в базу данных
            try:
                self.cursor.execute('''
                    INSERT INTO services (user_id, service_name, description, price)
                    VALUES (?, ?, ?, ?)
                ''', (
                    self.user_id,
                    service_name.get(),
                    description,
                    price_value
                ))
                
                self.conn.commit()
                
                # Добавляем запись об активности
                self.add_activity("add_service", f"Добавление услуги: {service_name.get()}")
                
                # Перезагружаем список услуг
                self.load_services()
                
                # Уведомление
                self.show_notification("Услуга успешно добавлена", "success")
                
                popup.destroy()
                
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка базы данных", str(e))
        
        # Создаем кнопки явно и сохраняем ссылки на них
        cancel_button = ttk.Button(button_frame, text="Отмена", command=cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        save_button = ttk.Button(button_frame, text="Сохранить", command=save, style='Primary.TButton')
        save_button.pack(side=tk.RIGHT, padx=5, pady=5)
    
    def edit_service(self, service_id):
        """Редактирует существующую услугу"""
        try:
            # Получаем информацию об услуге
            self.cursor.execute('''
                SELECT service_name, description, price
                FROM services
                WHERE id = ?
            ''', (service_id,))
            
            service = self.cursor.fetchone()
            
            if not service:
                messagebox.showerror("Ошибка", "Услуга не найдена")
                return
                
            name, description, price = service
            
            # Создаем всплывающее окно
            popup = tk.Toplevel(self.root)
            popup.title("Редактировать услугу")
            popup.geometry("500x400")
            popup.configure(bg=self.bg_color)
            popup.transient(self.root)
            popup.grab_set()
            
            # Создаем заголовок для всплывающего окна
            header = tk.Frame(popup, bg=self.primary_color, height=60)
            header.pack(side="top", fill="x")
            header.pack_propagate(False)
            
            header_title = tk.Label(header, text="Редактирование услуги", font=("Helvetica", 16, "bold"), 
                                   fg=self.text_light, bg=self.primary_color)
            header_title.pack(side="left", padx=20, pady=15)
            
            # Создаем контент
            content = tk.Frame(popup, bg=self.card_bg, padx=20, pady=20)
            content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Поля
            # Название услуги
            name_frame = ttk.Frame(content, style='Card.TFrame')
            name_frame.pack(fill=tk.X, pady=10)
            ttk.Label(name_frame, text="Название услуги:", width=15, anchor=tk.W).pack(side=tk.LEFT)
            service_name = tk.StringVar(value=name)
            ttk.Entry(name_frame, textvariable=service_name, width=35).pack(side=tk.LEFT, padx=5)
            
            # Описание (многострочное)
            desc_frame = ttk.Frame(content, style='Card.TFrame')
            desc_frame.pack(fill=tk.X, pady=10)
            ttk.Label(desc_frame, text="Описание:", width=15, anchor=tk.W).pack(side=tk.LEFT, anchor="n")
            
            description_text = tk.Text(desc_frame, height=5, width=35, font=('Helvetica', 10))
            description_text.insert("1.0", description)
            description_text.pack(side=tk.LEFT, padx=5)
            
            # Скроллбар для описания
            desc_scrollbar = ttk.Scrollbar(desc_frame, orient="vertical", command=description_text.yview)
            desc_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
            description_text.config(yscrollcommand=desc_scrollbar.set)
            
            # Цена
            price_frame = ttk.Frame(content, style='Card.TFrame')
            price_frame.pack(fill=tk.X, pady=10)
            ttk.Label(price_frame, text="Цена (KZT):", width=15, anchor=tk.W).pack(side=tk.LEFT)
            price_var = tk.StringVar(value=f"{price:,.0f}")
            ttk.Entry(price_frame, textvariable=price_var, width=35).pack(side=tk.LEFT, padx=5)
            
            # Кнопки
            button_frame = ttk.Frame(content, style='Card.TFrame')
            button_frame.pack(fill=tk.X, pady=(20, 0))
            
            # Функции действий
            def cancel():
                popup.destroy()
                
            def save():
                # Проверка ввода
                if not service_name.get().strip():
                    messagebox.showerror("Ошибка", "Название услуги обязательно")
                    return
                    
                try:
                    price_value = float(price_var.get().replace(' ', '').replace(',', '.'))
                    if price_value <= 0:
                        raise ValueError
                except:
                    messagebox.showerror("Ошибка", "Цена должна быть положительным числом")
                    return
                    
                # Получаем текст описания
                description = description_text.get("1.0", tk.END).strip()
                    
                # Обновляем в базе данных
                try:
                    self.cursor.execute('''
                        UPDATE services
                        SET service_name = ?, description = ?, price = ?
                        WHERE id = ?
                    ''', (
                        service_name.get(),
                        description,
                        price_value,
                        service_id
                    ))
                    
                    self.conn.commit()
                    
                    # Добавляем запись об активности
                    self.add_activity("edit_service", f"Изменение услуги: {service_name.get()}")
                    
                    # Перезагружаем список услуг
                    self.load_services()
                    
                    # Уведомление
                    self.show_notification("Услуга успешно обновлена", "success")
                    
                    popup.destroy()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Ошибка базы данных", str(e))
            
            # Добавляем кнопки
            ttk.Button(button_frame, text="Отмена", command=cancel).pack(side=tk.LEFT)
            ttk.Button(button_frame, text="Сохранить", command=save, style='Primary.TButton').pack(side=tk.RIGHT)
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
    
    def delete_service(self, service_id):
        """Удаляет услугу"""
        try:
            # Получаем название услуги для подтверждения
            self.cursor.execute("SELECT service_name FROM services WHERE id = ?", (service_id,))
            result = self.cursor.fetchone()
            
            if not result:
                messagebox.showerror("Ошибка", "Услуга не найдена")
                return
                
            service_name = result[0]
            
            # Просим подтверждение
            if not messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить услугу '{service_name}'?"):
                return
                
            # Удаляем из базы данных
            self.cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
            self.conn.commit()
            
            # Добавляем запись об активности
            self.add_activity("delete_service", f"Удаление услуги: {service_name}")
            
            # Перезагружаем список услуг
            self.load_services()
            
            # Уведомление
            self.show_notification("Услуга успешно удалена", "warning")
            
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", str(e))
    
    def change_password(self):
        """Изменяет пароль пользователя"""
        # Создаем всплывающее окно
        popup = tk.Toplevel(self.root)
        popup.title("Изменение пароля")
        popup.geometry("400x300")
        popup.configure(bg=self.bg_color)
        popup.transient(self.root)
        popup.grab_set()
        
        # Создаем заголовок для всплывающего окна
        header = tk.Frame(popup, bg=self.primary_color, height=50)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        header_title = tk.Label(header, text="Изменение пароля", font=("Helvetica", 14, "bold"), 
                               fg=self.text_light, bg=self.primary_color)
        header_title.pack(side="left", padx=20, pady=10)
        
        # Создаем контент
        content = tk.Frame(popup, bg=self.card_bg, padx=20, pady=20)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Текущий пароль
        current_frame = ttk.Frame(content, style='Card.TFrame')
        current_frame.pack(fill=tk.X, pady=10)
        ttk.Label(current_frame, text="Текущий пароль:", anchor=tk.W).pack(anchor=tk.W, pady=5)
        current_password = tk.StringVar()
        current_entry = ttk.Entry(current_frame, textvariable=current_password, show="*", width=30)
        current_entry.pack(anchor=tk.W, pady=5)
        
        # Новый пароль
        new_frame = ttk.Frame(content, style='Card.TFrame')
        new_frame.pack(fill=tk.X, pady=10)
        ttk.Label(new_frame, text="Новый пароль:", anchor=tk.W).pack(anchor=tk.W, pady=5)
        new_password = tk.StringVar()
        new_entry = ttk.Entry(new_frame, textvariable=new_password, show="*", width=30)
        new_entry.pack(anchor=tk.W, pady=5)
        
        # Подтверждение нового пароля
        confirm_frame = ttk.Frame(content, style='Card.TFrame')
        confirm_frame.pack(fill=tk.X, pady=10)
        ttk.Label(confirm_frame, text="Подтвердите пароль:", anchor=tk.W).pack(anchor=tk.W, pady=5)
        confirm_password = tk.StringVar()
        confirm_entry = ttk.Entry(confirm_frame, textvariable=confirm_password, show="*", width=30)
        confirm_entry.pack(anchor=tk.W, pady=5)
        
        # Кнопки
        button_frame = ttk.Frame(content, style='Card.TFrame')
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Функции действий
        def cancel():
            popup.destroy()
            
        def save():
            # Проверка ввода
            if not current_password.get():
                messagebox.showerror("Ошибка", "Введите текущий пароль")
                return
                
            if not new_password.get():
                messagebox.showerror("Ошибка", "Введите новый пароль")
                return
                
            if new_password.get() != confirm_password.get():
                messagebox.showerror("Ошибка", "Пароли не совпадают")
                return
                
            if len(new_password.get()) < 8:
                messagebox.showerror("Ошибка", "Новый пароль должен содержать минимум 8 символов")
                return
            
            # В реальном приложении здесь была бы проверка текущего пароля
            # и хеширование нового пароля перед сохранением
            
            # Поскольку это демо, просто показываем успешное сообщение
            messagebox.showinfo("Успех", "Пароль успешно изменен")
            
            # Добавляем запись об активности
            self.add_activity("change_password", "Изменение пароля")
            
            popup.destroy()
            
        # Добавляем кнопки
        ttk.Button(button_frame, text="Отмена", command=cancel).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Сохранить", command=save, style='Primary.TButton').pack(side=tk.RIGHT)
    
    def save_settings(self):
        """Сохраняет настройки пользователя"""
        # В реальном приложении здесь было бы сохранение настроек в базу данных
        
        # Добавляем запись об активности
        self.add_activity("update_settings", "Обновление настроек аккаунта")
        
        # Показываем уведомление
        self.show_notification("Настройки успешно сохранены", "success")
    
    def logout(self):
        """Выход из аккаунта"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти из аккаунта?"):
            # В реальном приложении здесь был бы код для выхода
            # Для демо просто закрываем окно
            self.root.destroy()
    
    def add_activity(self, activity_type, description):
        """Добавляет запись об активности в базу данных"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.cursor.execute('''
                INSERT INTO activities (user_id, activity_type, description, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (self.user_id, activity_type, description, timestamp))
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении активности: {str(e)}")
    
    def show_notification(self, message, notification_type="info"):
        """Показывает всплывающее уведомление"""
        # Определяем цвет в зависимости от типа уведомления
        colors = {
            "info": self.primary_color,
            "success": self.success_color,
            "warning": self.warning_color,
            "error": "#F44336"
        }
        
        bg_color = colors.get(notification_type, self.primary_color)
        
        # Создаем окно уведомления
        notification = tk.Toplevel(self.root)
        notification.overrideredirect(True)  # Убираем рамку окна
        notification.attributes("-topmost", True)  # Поверх всех окон
        
        # Расположение в правом верхнем углу основного окна
        x = self.root.winfo_x() + self.root.winfo_width() - 320
        y = self.root.winfo_y() + 100
        notification.geometry(f"300x80+{x}+{y}")
        
        # Содержимое уведомления
        frame = tk.Frame(notification, bg=bg_color, padx=15, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Иконка в зависимости от типа
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        icon = icons.get(notification_type, "ℹ️")
        
        # Заголовок с иконкой
        header_frame = tk.Frame(frame, bg=bg_color)
        header_frame.pack(fill=tk.X)
        
        icon_label = tk.Label(header_frame, text=icon, font=("Helvetica", 14), bg=bg_color, fg="white")
        icon_label.pack(side=tk.LEFT)
        
        # Текст уведомления
        message_label = tk.Label(frame, text=message, font=("Helvetica", 11), 
                                bg=bg_color, fg="white", wraplength=250, justify=tk.LEFT)
        message_label.pack(pady=(5, 0), anchor=tk.W)
        
        # Закрытие через таймер
        notification.after(3000, notification.destroy)
        
        # Добавляем эффекты появления и исчезновения
        def fade_in():
            alpha = notification.attributes("-alpha")
            if alpha < 1.0:
                notification.attributes("-alpha", alpha + 0.1)
                notification.after(30, fade_in)
        
        def fade_out():
            alpha = notification.attributes("-alpha")
            if alpha > 0.1:
                notification.attributes("-alpha", alpha - 0.1)
                notification.after(30, fade_out)
            else:
                notification.destroy()
        
        # Запускаем появление
        notification.attributes("-alpha", 0.0)
        fade_in()
        
        # Запускаем исчезновение через 2.5 секунды
        notification.after(2500, fade_out)
    
    def go_back_to_main(self):
        """Возврат в главное меню"""
        self.root.destroy()

if __name__ == "__main__":
    # Проверка наличия PIL/Pillow
    try:
        from PIL import Image, ImageTk, ImageDraw, ImageFont
    except ImportError:
        print("Для этого приложения требуется PIL/Pillow.")
        print("Установите его с помощью: pip install pillow")
        exit(1)
        
    # Создаем и запускаем приложение
    root = tk.Tk()
    app = UserProfile(root)
    root.mainloop()