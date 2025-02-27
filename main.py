import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import sqlite3
import sys
import os
from PIL import Image, ImageTk
from datetime import datetime
import webbrowser
import random

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jyldam jauap")
        self.root.geometry("1000x600")

        # Обновленная цветовая схема: красный и черный с белым текстом
        self.primary_color = "#B71C1C"  # Темно-красный
        self.secondary_color = "#212121"  # Почти черный
        self.accent_color = "#F44336"  # Более яркий красный для акцентов
        self.bg_color = "#F5F5F5"  # Светло-серый фон
        self.text_color = "#FFFFFF"  # Белый для текста
        self.card_bg = "#FFFFFF"  # Белый для карточек

        self.root.configure(bg=self.bg_color)

        # Установка иконки приложения (если есть файл иконки)
        try:
            self.root.iconbitmap("images/icon.ico")
        except:
            pass

        # Создание разделов интерфейса
        self.create_header()
        self.create_sidebar()
        self.create_main_content()

    def create_header(self):
        header = tk.Frame(self.root, bg=self.primary_color, height=80)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # Добавляем логотип или иконку
        try:
            logo_img = Image.open("images/logo.png")
            logo_img = logo_img.resize((50, 50), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(header, image=logo_photo, bg=self.primary_color)
            logo_label.image = logo_photo  # Сохраняем ссылку на изображение
            logo_label.pack(side="left", padx=10, pady=10)
        except:
            # Если изображение не найдено, используем текстовую иконку
            logo_label = tk.Label(header, text="JJ", font=("Helvetica", 18, "bold"), 
                                 fg=self.primary_color, bg="white", width=3, height=1)
            logo_label.pack(side="left", padx=10, pady=10)

        title = tk.Label(header, text="JYLDAM JAUAP", font=("Helvetica", 24, "bold"), fg=self.text_color, bg=self.primary_color)
        title.pack(side="left", padx=5, pady=20)

        subtitle = tk.Label(header, text="Правовые решения для вашего бизнеса", font=("Helvetica", 12), fg=self.text_color, bg=self.primary_color)
        subtitle.pack(side="left", padx=10, pady=20)

        # Добавляем текущую дату
        current_date = datetime.now().strftime("%d.%m.%Y")
        date_label = tk.Label(header, text=current_date, font=("Helvetica", 12), 
                             fg=self.text_color, bg=self.primary_color)
        date_label.pack(side="right", padx=20, pady=20)

        # Добавляем кнопки языков - НОВЫЙ КОД
        lang_frame = tk.Frame(header, bg=self.primary_color)
        lang_frame.pack(side="right", padx=5, pady=20)
        
        # Стиль для кнопок языка
        lang_button_style = {
            "font": ("Helvetica", 10, "bold"),
            "width": 2,
            "bd": 1,
            "relief": "solid",
            "cursor": "hand2"
        }
        
        # Кнопки языка
        kz_btn = tk.Button(lang_frame, text="KZ", bg="white", fg=self.primary_color, 
                          command=self.switch_to_kazakh, **lang_button_style)
        kz_btn.pack(side="left", padx=2)
        
        ru_btn = tk.Button(lang_frame, text="RU", bg=self.accent_color, fg="white", 
                          command=self.switch_to_russian, **lang_button_style)
        ru_btn.pack(side="left", padx=2)
        
        en_btn = tk.Button(lang_frame, text="EN", bg="white", fg=self.primary_color, 
                          command=self.switch_to_english, **lang_button_style)
        en_btn.pack(side="left", padx=2)

        profile_icon = tk.Label(header, text="AJ", font=("Helvetica", 16, "bold"), 
                               fg=self.primary_color, bg="white", width=3, height=2, 
                               relief="solid", cursor="hand2")
        profile_icon.pack(side="right", padx=10, pady=10)
        profile_icon.bind("<Button-1>", lambda e: self.open_profile())
    
    # Функции для переключения языков - пока не работающие
    def switch_to_kazakh(self):
        messagebox.showinfo("Тіл ауыстыру", "Қазақ тіліне ауысу функциясы әзірге қолжетімді емес.")
    
    def switch_to_russian(self):
        messagebox.showinfo("Смена языка", "Функция переключения на русский язык пока недоступна.")
    
    def switch_to_english(self):
        messagebox.showinfo("Language Switch", "English language switch feature is not available yet.")

    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg=self.secondary_color, width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Добавляем разделитель с градиентом
        gradient_frame = tk.Frame(sidebar, bg=self.accent_color, height=3)
        gradient_frame.pack(fill="x", pady=5)

        button_style = {
            "font": ("Helvetica", 12),
            "bg": self.secondary_color,
            "fg": self.text_color,
            "bd": 0,
            "width": 25,
            "height": 2,
            "anchor": "w",
            "padx": 20,
            "activebackground": self.accent_color,
            "activeforeground": self.text_color,
            "cursor": "hand2"  # Курсор в виде руки при наведении
        }

        sections = [
            ("🏠 Главное меню", self.show_main_menu),
            ("🤖 ИИ Ассистент", self.open_ai_assistant),
            ("💰 Штрафы и налоги", self.open_fines),
            ("👥 База юристов", self.open_lawyers),
            ("📰 Новости", self.open_news),
            ("❓ Справка", self.open_help)
        ]

        # Создаем кнопки с эффектом наведения
        for text, command in sections:
            btn = tk.Button(sidebar, text=text, command=command, **button_style)
            btn.pack(fill="x", pady=2)
            
            # Добавляем эффект при наведении
            btn.bind("<Enter>", lambda e, b=btn: self.on_hover(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_leave(b))

        # Добавляем информацию о версии внизу сайдбара
        version_frame = tk.Frame(sidebar, bg=self.secondary_color)
        version_frame.pack(side="bottom", fill="x", pady=10)
        
        version_label = tk.Label(version_frame, text="Версия 1.2.0", 
                                font=("Helvetica", 8), fg="#888888", bg=self.secondary_color)
        version_label.pack(pady=5)

    def on_hover(self, button):
        button.config(bg=self.accent_color)

    def on_leave(self, button):
        button.config(bg=self.secondary_color)

    def create_main_content(self):
        self.main_content = tk.Frame(self.root, bg=self.bg_color)
        self.main_content.pack(side="right", fill="both", expand=True)
        self.show_main_menu()

    def show_main_menu(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Создаем фрейм с прокруткой
        main_frame = tk.Frame(self.main_content, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Добавляем канву и прокрутку
        canvas = tk.Canvas(main_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg=self.bg_color)
        
        # Настраиваем прокрутку
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        content_frame.bind("<Configure>", configure_scroll_region)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)

        # Приветственное сообщение с анимацией
        welcome_frame = tk.Frame(content_frame, bg=self.bg_color)
        welcome_frame.pack(fill="x", pady=10)
        
        welcome_label = tk.Label(welcome_frame, text="Добро пожаловать в Jyldam jauap!", 
                               font=("Helvetica", 24, "bold"), fg=self.primary_color, bg=self.bg_color)
        welcome_label.pack(pady=10)
        
        # Добавляем подзаголовок
        slogan_label = tk.Label(welcome_frame, 
                              text="Ваш надежный юридический помощник для бизнеса", 
                              font=("Helvetica", 14), fg=self.secondary_color, bg=self.bg_color)
        slogan_label.pack(pady=5)
        
        # Создаем панель быстрого доступа
        quick_access_frame = tk.Frame(content_frame, bg=self.bg_color)
        quick_access_frame.pack(fill="x", pady=15)
        
        # Заголовок панели быстрого доступа
        tk.Label(quick_access_frame, text="Быстрый доступ:", 
                font=("Helvetica", 16, "bold"), fg=self.primary_color, bg=self.bg_color).pack(anchor="w")
        
        # Карточки быстрого доступа
        cards_frame = tk.Frame(quick_access_frame, bg=self.bg_color)
        cards_frame.pack(fill="x", pady=10)
        
        # Создаем сетку карточек
        for i in range(3):
            cards_frame.columnconfigure(i, weight=1)
        
        # Карточка ИИ Ассистент
        ai_card = tk.Frame(cards_frame, bg=self.card_bg, relief="raised", bd=1)
        ai_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        tk.Label(ai_card, text="🤖", font=("Helvetica", 24), bg=self.card_bg).pack(pady=5)
        tk.Label(ai_card, text="ИИ Ассистент", 
                font=("Helvetica", 14, "bold"), bg=self.card_bg, fg=self.primary_color).pack()
        tk.Label(ai_card, text="Получите мгновенный юридический совет", 
                font=("Helvetica", 10), bg=self.card_bg, wraplength=150).pack(pady=5)
        
        ai_button = tk.Button(ai_card, text="Спросить", bg=self.primary_color, fg=self.text_color,
                            command=self.open_ai_assistant, cursor="hand2")
        ai_button.pack(pady=10)
        
        # Карточка Юристы
        lawyers_card = tk.Frame(cards_frame, bg=self.card_bg, relief="raised", bd=1)
        lawyers_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        tk.Label(lawyers_card, text="👥", font=("Helvetica", 24), bg=self.card_bg).pack(pady=5)
        tk.Label(lawyers_card, text="Юристы", 
                font=("Helvetica", 14, "bold"), bg=self.card_bg, fg=self.primary_color).pack()
        tk.Label(lawyers_card, text="Найдите профессионального юриста", 
                font=("Helvetica", 10), bg=self.card_bg, wraplength=150).pack(pady=5)
        
        lawyers_button = tk.Button(lawyers_card, text="Посмотреть", bg=self.primary_color, 
                                 fg=self.text_color, command=self.open_lawyers, cursor="hand2")
        lawyers_button.pack(pady=10)
        
        # Карточка Штрафы
        fines_card = tk.Frame(cards_frame, bg=self.card_bg, relief="raised", bd=1)
        fines_card.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        tk.Label(fines_card, text="💰", font=("Helvetica", 24), bg=self.card_bg).pack(pady=5)
        tk.Label(fines_card, text="Штрафы и налоги", 
                font=("Helvetica", 14, "bold"), bg=self.card_bg, fg=self.primary_color).pack()
        tk.Label(fines_card, text="Информация о штрафах и налогах", 
                font=("Helvetica", 10), bg=self.card_bg, wraplength=150).pack(pady=5)
        
        fines_button = tk.Button(fines_card, text="Узнать", bg=self.primary_color, 
                               fg=self.text_color, command=self.open_fines, cursor="hand2")
        fines_button.pack(pady=10)

        # Добавляем статистику (карточку с данными)
        stats_frame = tk.Frame(content_frame, bg=self.card_bg, relief="solid", bd=1)
        stats_frame.pack(fill="x", pady=15, padx=5)
        
        tk.Label(stats_frame, text="Статистика", 
                font=("Helvetica", 16, "bold"), fg=self.primary_color, bg=self.card_bg).pack(anchor="w", padx=15, pady=10)
        
        stats_data_frame = tk.Frame(stats_frame, bg=self.card_bg)
        stats_data_frame.pack(fill="x", pady=5, padx=15)
        
        # Показываем статистику
        try:
            conn = sqlite3.connect("db/users.db")
            cursor = conn.cursor()
            
            # Считаем количество юристов
            cursor.execute("SELECT COUNT(*) FROM lawyers")
            lawyers_count = cursor.fetchone()[0]
            
            # Считаем количество новостей
            cursor.execute("SELECT COUNT(*) FROM news")
            news_count = cursor.fetchone()[0]
            
            # Считаем количество штрафов
            cursor.execute("SELECT COUNT(*) FROM fines")
            fines_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Отображаем статистику в три колонки
            stats_labels = [
                f"🧑‍⚖️ Юристов в базе: {lawyers_count}",
                f"📰 Новостей: {news_count}",
                f"💰 Типов штрафов: {fines_count}"
            ]
            
            for i, text in enumerate(stats_labels):
                tk.Label(stats_data_frame, text=text, font=("Helvetica", 12), 
                        fg=self.secondary_color, bg=self.card_bg).pack(side="left", padx=20, pady=5)
                
        except Exception as e:
            tk.Label(stats_data_frame, text=f"Ошибка при загрузке статистики: {e}", 
                    font=("Helvetica", 12), fg="red", bg=self.card_bg).pack(pady=5)

        # Заголовок блока новостей
        news_header = tk.Frame(content_frame, bg=self.bg_color)
        news_header.pack(fill="x", pady=10)
        
        tk.Label(news_header, text="Последние новости:", 
                font=("Helvetica", 18, "bold"), fg=self.primary_color, bg=self.bg_color).pack(side="left")
        
        view_all_btn = tk.Button(news_header, text="Смотреть все", bg=self.secondary_color, 
                               fg=self.text_color, command=self.open_news, cursor="hand2")
        view_all_btn.pack(side="right", padx=10)

        # Новости
        news_frame = tk.Frame(content_frame, bg=self.bg_color)
        news_frame.pack(fill="x", pady=5)

        try:
            conn = sqlite3.connect("db/users.db")
            cursor = conn.cursor()
            cursor.execute("SELECT title, description FROM news ORDER BY id DESC LIMIT 3")
            news_data = cursor.fetchall()
            conn.close()

            if not news_data:
                tk.Label(news_frame, text="Новостей пока нет", 
                        font=("Helvetica", 12), fg=self.secondary_color, bg=self.bg_color).pack(anchor="w", pady=10)
            else:
                for title, desc in news_data:
                    news_card = tk.Frame(news_frame, bg=self.card_bg, relief="solid", borderwidth=1)
                    news_card.pack(fill="x", pady=5)
                    news_card.bind("<Button-1>", lambda e: self.open_news())
                    news_card.bind("<Enter>", lambda e, c=news_card: c.config(relief="raised"))
                    news_card.bind("<Leave>", lambda e, c=news_card: c.config(relief="solid"))

                    # Заголовок новости
                    tk.Label(news_card, text=title, font=("Helvetica", 14, "bold"), 
                            fg=self.primary_color, bg=self.card_bg).pack(anchor="w", padx=10, pady=5)
                    
                    # Описание новости с ограничением длины и переносом строк
                    short_desc = desc[:150] + "..." if len(desc) > 150 else desc
                    desc_label = tk.Label(news_card, text=short_desc, font=("Helvetica", 12), 
                                        fg=self.secondary_color, bg=self.card_bg, 
                                        wraplength=700, justify="left")
                    desc_label.pack(anchor="w", padx=10, pady=5)
                    
                    # Кнопка "Читать далее"
                    read_more = tk.Button(news_card, text="Читать далее", 
                                        bg=self.bg_color, fg=self.secondary_color,
                                        command=self.open_news, cursor="hand2")
                    read_more.pack(anchor="e", padx=10, pady=5)
        except Exception as e:
            tk.Label(news_frame, text=f"Ошибка при загрузке новостей: {e}", 
                    font=("Helvetica", 12), fg="red", bg=self.bg_color).pack(anchor="w", pady=10)

        # Добавляем подвал
        footer_frame = tk.Frame(content_frame, bg="#E0E0E0", height=40)
        footer_frame.pack(fill="x", pady=20, side="bottom")
        
        copyright_label = tk.Label(footer_frame, text="© 2025 Jyldam jauap. Все права защищены.", 
                                 font=("Helvetica", 10), fg=self.secondary_color, bg="#E0E0E0")
        copyright_label.pack(side="left", padx=20, pady=10)
        
        privacy_label = tk.Label(footer_frame, text="Политика конфиденциальности", 
                               font=("Helvetica", 10), fg=self.primary_color, bg="#E0E0E0", cursor="hand2")
        privacy_label.pack(side="right", padx=20, pady=10)
        privacy_label.bind("<Button-1>", lambda e: self.show_privacy_policy())

    def open_news(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Заголовок
        tk.Label(self.main_content, text="Новости", 
                font=("Helvetica", 24, "bold"), fg=self.primary_color, bg=self.bg_color).pack(pady=20)

        # Создаем фрейм с прокруткой для новостей
        news_container = tk.Frame(self.main_content, bg=self.bg_color)
        news_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Добавляем канву и прокрутку
        canvas = tk.Canvas(news_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(news_container, orient="vertical", command=canvas.yview)
        news_frame = tk.Frame(canvas, bg=self.bg_color)
        
        # Настраиваем прокрутку
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_window = canvas.create_window((0, 0), window=news_frame, anchor="nw")
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        news_frame.bind("<Configure>", configure_scroll_region)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)

        try:
            conn = sqlite3.connect("db/users.db")
            cursor = conn.cursor()
            cursor.execute("SELECT title, description FROM news ORDER BY id DESC")
            news_data = cursor.fetchall()
            conn.close()

            if not news_data:
                tk.Label(news_frame, text="Новостей пока нет", 
                        font=("Helvetica", 12), fg=self.secondary_color, bg=self.bg_color).pack(anchor="w", pady=10)
            else:
                for title, desc in news_data:
                    news_card = tk.Frame(news_frame, bg=self.card_bg, relief="solid", borderwidth=1)
                    news_card.pack(fill="x", pady=5)

                    # Заголовок новости
                    tk.Label(news_card, text=title, 
                            font=("Helvetica", 14, "bold"), fg=self.primary_color, bg=self.card_bg).pack(anchor="w", padx=10, pady=5)
                    
                    # Описание новости с переносом строк
                    desc_label = tk.Label(news_card, text=desc, 
                                        font=("Helvetica", 12), fg=self.secondary_color, 
                                        bg=self.card_bg, wraplength=700, justify="left")
                    desc_label.pack(anchor="w", padx=10, pady=5)
                    
                    # Дата публикации (случайная для примера)
                    date = f"{random.randint(1, 28)}.{random.randint(1, 12)}.2025"
                    date_label = tk.Label(news_card, text=f"Опубликовано: {date}", 
                                        font=("Helvetica", 10), fg="#888888", bg=self.card_bg)
                    date_label.pack(anchor="e", padx=10, pady=5)
        except Exception as e:
            tk.Label(news_frame, text=f"Ошибка при загрузке новостей: {e}", 
                    font=("Helvetica", 12), fg="red", bg=self.bg_color).pack(anchor="w", pady=10)

        # Кнопка назад
        back_btn = tk.Button(news_frame, text="← Назад", 
                            command=self.show_main_menu, bg=self.secondary_color, fg=self.text_color)
        back_btn.pack(pady=20)

    def open_fines(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Заголовок
        header_frame = tk.Frame(self.main_content, bg=self.bg_color)
        header_frame.pack(fill="x", pady=10)
        
        tk.Label(header_frame, text="Штрафы и налоги", 
                font=("Helvetica", 24, "bold"), fg=self.primary_color, bg=self.bg_color).pack(side="left", padx=20)
        
        # Добавляем поле поиска
        search_frame = tk.Frame(header_frame, bg=self.bg_color)
        search_frame.pack(side="right", padx=20)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=5)
        
        search_btn = tk.Button(search_frame, text="Поиск", 
                              bg=self.secondary_color, fg=self.text_color, 
                              command=lambda: self.search_fines(search_var.get()))
        search_btn.pack(side="left")

        # Создаем фрейм с прокруткой для списка штрафов
        fines_container = tk.Frame(self.main_content, bg=self.bg_color)
        fines_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Добавляем канву и прокрутку
        canvas = tk.Canvas(fines_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(fines_container, orient="vertical", command=canvas.yview)
        self.fines_frame = tk.Frame(canvas, bg=self.bg_color)
        
        # Настраиваем прокрутку
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_window = canvas.create_window((0, 0), window=self.fines_frame, anchor="nw")
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.fines_frame.bind("<Configure>", configure_scroll_region)
        
        # Загружаем штрафы
        self.load_fines()

        # Кнопка назад
        back_btn = tk.Button(self.main_content, text="← Назад", 
                            command=self.show_main_menu, bg=self.secondary_color, fg=self.text_color)
        back_btn.pack(pady=10)

    def load_fines(self, search_term=None):
        # Очищаем предыдущие данные
        for widget in self.fines_frame.winfo_children():
            widget.destroy()

        try:
            conn = sqlite3.connect("db/users.db")
            cursor = conn.cursor()
            
            if search_term:
                cursor.execute("SELECT description, amount FROM fines WHERE description LIKE ?", 
                             (f"%{search_term}%",))
            else:
                cursor.execute("SELECT description, amount FROM fines")
                
            fines = cursor.fetchall()
            conn.close()

            if not fines:
                tk.Label(self.fines_frame, text="Информация о штрафах и налогах отсутствует", 
                        font=("Helvetica", 12), fg=self.secondary_color, bg=self.bg_color).pack(anchor="w", pady=10)
            else:
                for i, (desc, amount) in enumerate(fines):
                    fine_card = tk.Frame(self.fines_frame, bg=self.card_bg, relief="solid", borderwidth=1)
                    fine_card.pack(fill="x", pady=5)
                    
                    # Используем разный фон для четных и нечетных строк
                    bg_color = "#F9F9F9" if i % 2 == 0 else self.card_bg
                    fine_card.configure(bg=bg_color)
                    
                    desc_label = tk.Label(fine_card, text=desc, font=("Helvetica", 12, "bold"), 
                                        fg=self.secondary_color, bg=bg_color, wraplength=700, justify="left")
                    desc_label.pack(anchor="w", padx=10, pady=5)
                    
                    amount_label = tk.Label(fine_card, text=f"Сумма: {amount} KZT", 
                                          font=("Helvetica", 12), fg=self.primary_color, bg=bg_color)
                    amount_label.pack(anchor="w", padx=10, pady=5)
        except Exception as e:
            tk.Label(self.fines_frame, text=f"Ошибка при загрузке данных: {e}", 
                    font=("Helvetica", 12), fg="red", bg=self.bg_color).pack(anchor="w", pady=10)

    def search_fines(self, search_term):
        self.load_fines(search_term)

    def open_lawyers(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Заголовок
        header_frame = tk.Frame(self.main_content, bg=self.bg_color)
        header_frame.pack(fill="x", pady=10)
        
        tk.Label(header_frame, text="База юристов", 
                font=("Helvetica", 24, "bold"), fg=self.primary_color, bg=self.bg_color).pack(side="left", padx=20)
        
        # Добавляем поле поиска
        search_frame = tk.Frame(header_frame, bg=self.bg_color)
        search_frame.pack(side="right", padx=20)
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=5)
        
        search_btn = tk.Button(search_frame, text="Поиск", 
                              bg=self.secondary_color, fg=self.text_color, 
                              command=lambda: self.search_lawyers(search_var.get()))
        search_btn.pack(side="left")

        # Создаем фрейм с прокруткой для списка юристов
        lawyers_container = tk.Frame(self.main_content, bg=self.bg_color)
        lawyers_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Добавляем канву и прокрутку
        canvas = tk.Canvas(lawyers_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(lawyers_container, orient="vertical", command=canvas.yview)
        self.lawyers_frame = tk.Frame(canvas, bg=self.bg_color)
        
        # Настраиваем прокрутку
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_window = canvas.create_window((0, 0), window=self.lawyers_frame, anchor="nw")
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        self.lawyers_frame.bind("<Configure>", configure_scroll_region)
        
        # Загружаем юристов
        self.load_lawyers()

        # Кнопка назад
        back_btn = tk.Button(self.main_content, text="← Назад", 
                            command=self.show_main_menu, bg=self.secondary_color, fg=self.text_color)
        back_btn.pack(pady=10)

    def load_lawyers(self, search_term=None):
        # Очищаем предыдущие данные
        for widget in self.lawyers_frame.winfo_children():
            widget.destroy()

        try:
            conn = sqlite3.connect("db/users.db")
            cursor = conn.cursor()
            
            if search_term:
                cursor.execute("""
                    SELECT name, phone, specialization, experience, rating FROM lawyers
                    WHERE name LIKE ? OR specialization LIKE ?
                    ORDER BY rating DESC
                """, (f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("""
                    SELECT name, phone, specialization, experience, rating FROM lawyers
                    ORDER BY rating DESC
                """)
                
            lawyers = cursor.fetchall()
            conn.close()

            if not lawyers:
                tk.Label(self.lawyers_frame, text="Информация о юристах отсутствует", 
                        font=("Helvetica", 12), fg=self.secondary_color, bg=self.bg_color).pack(anchor="w", pady=10)
            else:
                for row in lawyers:
                    lawyer_card = tk.Frame(self.lawyers_frame, bg=self.card_bg, relief="solid", borderwidth=1)
                    lawyer_card.pack(fill="x", pady=10)
                    
                    # Распаковываем данные
                    if len(row) >= 4:
                        name, phone, specialization, experience = row[:4]
                        rating = row[4] if len(row) > 4 else 0  # Рейтинг
                        
                        # Основная информация о юристе
                        info_frame = tk.Frame(lawyer_card, bg=self.card_bg)
                        info_frame.pack(fill="x", padx=10, pady=5)
                        
                        # Фото/иконка юриста
                        try:
                            img = Image.open(f"images/lawyers/{name.split()[0]}.jpg")
                            img = img.resize((80, 80), Image.LANCZOS)
                            photo = ImageTk.PhotoImage(img)
                            img_label = tk.Label(info_frame, image=photo, bg=self.card_bg)
                            img_label.image = photo
                            img_label.pack(side="left", padx=10)
                        except:
                            # Если фото не найдено, используем текстовую иконку
                            img_label = tk.Label(info_frame, text=name[0], font=("Helvetica", 24, "bold"), 
                                               fg=self.text_color, bg=self.primary_color, width=3, height=2)
                            img_label.pack(side="left", padx=10)
                        
                        # Детали юриста
                        details_frame = tk.Frame(info_frame, bg=self.card_bg)
                        details_frame.pack(side="left", fill="both", expand=True, padx=10)
                        
                        name_frame = tk.Frame(details_frame, bg=self.card_bg)
                        name_frame.pack(anchor="w", fill="x")
                        
                        tk.Label(name_frame, text=name, font=("Helvetica", 14, "bold"), 
                                fg=self.primary_color, bg=self.card_bg).pack(side="left")
                        
                        # Отображаем рейтинг звездами
                        rating_frame = tk.Frame(name_frame, bg=self.card_bg)
                        rating_frame.pack(side="left", padx=15)
                        
                        # Показываем рейтинг звездами
                        for i in range(5):
                            if i < int(rating):
                                star = "★"  # Полная звезда
                                color = "#FFD700"  # Золотой
                            elif i < rating:
                                star = "★"  # Полная звезда для дробной части
                                color = "#FFD700"  # Золотой
                            else:
                                star = "☆"  # Пустая звезда
                                color = "#888888"  # Серый
                                
                            tk.Label(rating_frame, text=star, font=("Helvetica", 12), 
                                   fg=color, bg=self.card_bg).pack(side="left")
                            
                        # Числовой рейтинг
                        tk.Label(rating_frame, text=f"({rating})", font=("Helvetica", 10), 
                               fg="#888888", bg=self.card_bg).pack(side="left", padx=5)
                        
                        # Основная информация
                        tk.Label(details_frame, text=f"Телефон: {phone}", font=("Helvetica", 12), 
                               fg=self.secondary_color, bg=self.card_bg).pack(anchor="w")
                        tk.Label(details_frame, text=f"Специализация: {specialization}", 
                               font=("Helvetica", 12), fg=self.secondary_color, bg=self.card_bg).pack(anchor="w")
                        tk.Label(details_frame, text=f"Опыт работы: {experience} лет", 
                               font=("Helvetica", 12), fg=self.secondary_color, bg=self.card_bg).pack(anchor="w")
                        
                        # Кнопки действий
                        button_frame = tk.Frame(lawyer_card, bg=self.card_bg)
                        button_frame.pack(fill="x", padx=10, pady=10)
                        
                        contact_btn = tk.Button(button_frame, text="Связаться", 
                                              bg=self.primary_color, fg=self.text_color,
                                              command=lambda p=phone: self.contact_lawyer(p))
                        contact_btn.pack(side="right", padx=5)
                        
                        info_btn = tk.Button(button_frame, text="Подробнее", 
                                           bg=self.secondary_color, fg=self.text_color,
                                           command=lambda n=name: self.show_lawyer_info(n))
                        info_btn.pack(side="right", padx=5)
                    elif len(row) == 2:
                        name, phone = row
                        tk.Label(lawyer_card, text=name, font=("Helvetica", 14, "bold"), 
                               fg=self.primary_color, bg=self.card_bg).pack(anchor="w", padx=10, pady=2)
                        tk.Label(lawyer_card, text=f"Телефон: {phone}", font=("Helvetica", 12), 
                               fg=self.secondary_color, bg=self.card_bg).pack(anchor="w", padx=10, pady=1)
                        
                        # Кнопка связаться
                        contact_btn = tk.Button(lawyer_card, text="Связаться", 
                                              bg=self.primary_color, fg=self.text_color,
                                              command=lambda p=phone: self.contact_lawyer(p))
                        contact_btn.pack(anchor="e", padx=10, pady=5)
        except Exception as e:
            tk.Label(self.lawyers_frame, text=f"Ошибка при загрузке данных: {e}", 
                    font=("Helvetica", 12), fg="red", bg=self.bg_color).pack(anchor="w", pady=10)

    def search_lawyers(self, search_term):
        self.load_lawyers(search_term)

    def contact_lawyer(self, phone):
        # Имитируем звонок или отправку сообщения
        messagebox.showinfo("Связаться с юристом", 
                          f"Связываемся с юристом по номеру {phone}\n\nВаш запрос отправлен. " + 
                          "Юрист свяжется с вами в ближайшее время.")

    def show_lawyer_info(self, name):
        # Показываем подробную информацию о юристе
        messagebox.showinfo("Информация о юристе", 
                          f"Подробная информация о юристе {name}\n\n" + 
                          "Здесь будет отображаться полная информация о юристе, " + 
                          "включая образование, опыт работы, специализацию и т.д.")

    def open_ai_assistant(self):
        # Запускаем chat.py как отдельный процесс вместо внедрения чата в главное окно
        try:
            subprocess.Popen(["python", "chat.py"])
        except Exception as e:
            # Если запуск не удался, показываем сообщение об ошибке
            for widget in self.main_content.winfo_children():
                widget.destroy()
                
            error_frame = tk.Frame(self.main_content, bg=self.bg_color)
            error_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            tk.Label(error_frame, text="Ошибка запуска ИИ Ассистента", 
                   font=("Helvetica", 24, "bold"), fg="red", bg=self.bg_color).pack(pady=20)
            
            tk.Label(error_frame, text=f"Не удалось запустить ИИ Ассистента: {e}", 
                   font=("Helvetica", 12), fg=self.secondary_color, bg=self.bg_color, 
                   wraplength=700, justify="left").pack(pady=10)
            
            tk.Label(error_frame, text="Убедитесь, что файл chat.py существует в директории программы.", 
                   font=("Helvetica", 12), fg=self.secondary_color, bg=self.bg_color).pack(pady=5)
            
            # Кнопка назад
            back_btn = tk.Button(error_frame, text="← Назад", 
                               command=self.show_main_menu, bg=self.secondary_color, fg=self.text_color)
            back_btn.pack(pady=20)

    def open_help(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Заголовок
        tk.Label(self.main_content, text="Справка", 
                font=("Helvetica", 24, "bold"), fg=self.primary_color, bg=self.bg_color).pack(pady=20)

        # Создаем фрейм с прокруткой для справки
        help_container = tk.Frame(self.main_content, bg=self.bg_color)
        help_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Добавляем канву и прокрутку
        canvas = tk.Canvas(help_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(help_container, orient="vertical", command=canvas.yview)
        help_frame = tk.Frame(canvas, bg=self.bg_color)
        
        # Настраиваем прокрутку
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_window = canvas.create_window((0, 0), window=help_frame, anchor="nw")
        
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        help_frame.bind("<Configure>", configure_scroll_region)
        
        # Создаем разделы справки
        help_sections = [
            ("О приложении", "Jyldam jauap - это приложение для получения юридической помощи и информации о законодательстве Казахстана."),
            ("Главное меню", "На главной странице вы найдете основную информацию и быстрый доступ к ключевым функциям приложения."),
            ("ИИ Ассистент", "ИИ Ассистент поможет вам получить ответы на юридические вопросы и найти нужную информацию."),
            ("Штрафы и налоги", "В этом разделе содержится информация о штрафах и налогах, их размерах и условиях применения."),
            ("База юристов", "База юристов содержит информацию о квалифицированных юристах, их специализации и контактных данных."),
            ("Новости", "В разделе новостей вы найдете актуальную информацию об изменениях в законодательстве и другие юридические новости.")
        ]
        
        for title, desc in help_sections:
            section_frame = tk.Frame(help_frame, bg=self.card_bg, relief="solid", borderwidth=1)
            section_frame.pack(fill="x", pady=5)
            
            tk.Label(section_frame, text=title, 
                   font=("Helvetica", 14, "bold"), fg=self.primary_color, bg=self.card_bg).pack(anchor="w", padx=10, pady=5)
            
            tk.Label(section_frame, text=desc, 
                   font=("Helvetica", 12), fg=self.secondary_color, bg=self.card_bg, 
                   wraplength=700, justify="left").pack(anchor="w", padx=10, pady=5)
        
        # Добавляем информацию о контактах
        contact_frame = tk.Frame(help_frame, bg=self.card_bg, relief="solid", borderwidth=1)
        contact_frame.pack(fill="x", pady=15)
        
        tk.Label(contact_frame, text="Контактная информация", 
                font=("Helvetica", 14, "bold"), fg=self.primary_color, bg=self.card_bg).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(contact_frame, text="Если у вас возникли вопросы или проблемы с приложением, свяжитесь с нами:", 
                font=("Helvetica", 12), fg=self.secondary_color, bg=self.card_bg).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(contact_frame, text="Email: support@jyldamjauap.kz", 
                font=("Helvetica", 12), fg=self.secondary_color, bg=self.card_bg).pack(anchor="w", padx=20, pady=2)
        
        tk.Label(contact_frame, text="Телефон: +7 (777) 123-45-67", 
                font=("Helvetica", 12), fg=self.secondary_color, bg=self.card_bg).pack(anchor="w", padx=20, pady=2)

        # Кнопка назад
        back_btn = tk.Button(help_frame, text="← Назад", 
                            command=self.show_main_menu, bg=self.secondary_color, fg=self.text_color)
        back_btn.pack(pady=20)

    def open_profile(self):
        # Открываем профиль пользователя
        try:
            subprocess.Popen(["python", "user_profile.py"])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть профиль: {e}")

    def show_privacy_policy(self):
        # Показываем политику конфиденциальности
        messagebox.showinfo("Политика конфиденциальности", 
                          "Политика конфиденциальности приложения Jyldam jauap\n\n" + 
                          "Мы не собираем личные данные пользователей без их согласия.\n" + 
                          "Вся информация, которую вы предоставляете, используется только для обеспечения работы приложения.")

if __name__ == "__main__":
    # Проверка наличия базы данных и создание директории при необходимости
    if not os.path.exists("db"):
        os.makedirs("db")
    
    # Создание директории для изображений, если она не существует
    if not os.path.exists("images"):
        os.makedirs("images")
    
    if not os.path.exists("images/lawyers"):
        os.makedirs("images/lawyers")
    
    # Проверка и создание базы данных с таблицами если она не существует
    if not os.path.exists("db/users.db"):
        conn = sqlite3.connect("db/users.db")
        cursor = conn.cursor()
        
        # Создание таблицы новостей
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
        ''')
        
        # Создание таблицы штрафов
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount TEXT NOT NULL
        )
        ''')
        
        # Создание таблицы юристов с полем рейтинга
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS lawyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            specialization TEXT,
            experience INTEGER,
            rating FLOAT DEFAULT 0
        )
        ''')
        
        # Добавление тестовых данных
        cursor.execute("INSERT INTO news (title, description) VALUES (?, ?)", 
                      ("Новый закон о налогообложении", "С 1 января 2025 года вступает в силу новый закон о налогообложении малого и среднего бизнеса. Закон предусматривает снижение налоговой нагрузки для ИП и малых предприятий, а также вводит новые льготы для инновационных компаний. Предприниматели смогут воспользоваться упрощенной системой отчетности и получить дополнительные преференции при регистрации новых предприятий."))
        cursor.execute("INSERT INTO news (title, description) VALUES (?, ?)", 
                      ("Изменение условий регистрации юридических лиц", "Правительство утвердило новый порядок регистрации юридических лиц и индивидуальных предпринимателей. Теперь весь процесс можно пройти онлайн, без посещения налоговых органов. Срок регистрации сокращен до 1 рабочего дня. Также отменены некоторые излишние требования к документам, что значительно упрощает процедуру для начинающих предпринимателей."))
        cursor.execute("INSERT INTO news (title, description) VALUES (?, ?)", 
                      ("Открытие Центра юридической поддержки", "В Астане открылся новый Центр юридической поддержки для предпринимателей. В центре можно получить бесплатную консультацию по вопросам ведения бизнеса, налогообложения и трудовых отношений. Центр работает ежедневно с 9:00 до 18:00. Предварительная запись на консультацию доступна на сайте центра или по телефону."))
        
        cursor.execute("INSERT INTO fines (description, amount) VALUES (?, ?)", 
                      ("Штраф за несвоевременную подачу налоговой декларации", "15000"))
        cursor.execute("INSERT INTO fines (description, amount) VALUES (?, ?)", 
                      ("Штраф за отсутствие регистрации ИП", "50000"))
        cursor.execute("INSERT INTO fines (description, amount) VALUES (?, ?)", 
                      ("Штраф за нарушение трудового законодательства", "100000"))
        cursor.execute("INSERT INTO fines (description, amount) VALUES (?, ?)", 
                      ("Штраф за нарушение прав потребителей", "75000"))
        cursor.execute("INSERT INTO fines (description, amount) VALUES (?, ?)", 
                      ("Штраф за несоблюдение санитарных норм", "120000"))
        
        cursor.execute("INSERT INTO lawyers (name, phone, specialization, experience, rating) VALUES (?, ?, ?, ?, ?)", 
                      ("Иванов Иван Иванович", "+7 (777) 123-45-67", "Налоговое право", 10, 4.7))
        cursor.execute("INSERT INTO lawyers (name, phone, specialization, experience, rating) VALUES (?, ?, ?, ?, ?)", 
                      ("Петрова Анна Сергеевна", "+7 (777) 987-65-43", "Корпоративное право", 8, 4.9))
        cursor.execute("INSERT INTO lawyers (name, phone, specialization, experience, rating) VALUES (?, ?, ?, ?, ?)", 
                      ("Серіков Нұрлан Қанатұлы", "+7 (777) 456-78-90", "Трудовое право", 15, 4.8))
        cursor.execute("INSERT INTO lawyers (name, phone, specialization, experience, rating) VALUES (?, ?, ?, ?, ?)", 
                      ("Ахметова Гүлнар Бекқызы", "+7 (777) 111-22-33", "Защита прав потребителей", 12, 4.5))
        cursor.execute("INSERT INTO lawyers (name, phone, specialization, experience, rating) VALUES (?, ?, ?, ?, ?)", 
                      ("Козлов Дмитрий Александрович", "+7 (777) 444-55-66", "Земельное право", 9, 4.6))
        
        conn.commit()
        conn.close()
    
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()