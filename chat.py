import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import threading
import time
import openai
import os
import json
from datetime import datetime
from PIL import Image, ImageTk
from constants import OPENAI_API_KEY

# Обновленная цветовая схема (соответствует главному меню)
PRIMARY_COLOR = "#B71C1C"  # Темно-красный
SECONDARY_COLOR = "#212121"  # Почти черный
ACCENT_COLOR = "#F44336"  # Более яркий красный для акцентов
BG_COLOR = "#F5F5F5"  # Светло-серый фон
TEXT_COLOR = "#FFFFFF"  # Белый для текста
USER_BG = "#E0E0E0"  # Светло-серый для сообщений пользователя
AI_BG = "#B71C1C"  # Темно-красный для сообщений AI
LIGHT_GRAY = "#CCCCCC"  # Светло-серый для разделителей
FONT = ("Helvetica", 12)
BUTTON_FONT = ("Helvetica", 10)

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jyldam jauap - Правовой ассистент")
        self.root.geometry("900x700")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(600, 500)

        # Устанавливаем API ключ и задаем настройки для более стабильной работы
        openai.api_key = OPENAI_API_KEY
        # Устанавливаем таймаут для запросов
        openai.api_requestor.TIMEOUT_SECS = 30
        self.message_history = [
            {"role": "system", "content": """
             Вы - юридический помощник. Отвечайте на вопросы по законодательству Казахстана.
             
             Важно: в конце каждого ответа указывайте источники информации в виде ссылок на 
             нормативные правовые акты, законы, кодексы или официальные государственные ресурсы.
             
             Пример формата:
             
             Источники:
             1. Гражданский кодекс РК, статья 123
             2. Закон РК "О правах потребителей", статья 45
             """}
        ]
        self.is_requesting = False
        self.conversation_started = False
        self.chat_messages = []

        # Создаем папку для сохранения истории чатов
        if not os.path.exists("chat_history"):
            os.makedirs("chat_history")

        self.create_widgets()
        self.show_welcome_message()

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Создаем главный фрейм
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель (боковое меню)
        self.sidebar = tk.Frame(main_frame, bg=SECONDARY_COLOR, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Заголовок боковой панели
        sidebar_header = tk.Frame(self.sidebar, bg=SECONDARY_COLOR, height=80)
        sidebar_header.pack(fill=tk.X)
        
        # Логотип в боковой панели
        try:
            logo_img = Image.open("images/logo.png")
            logo_img = logo_img.resize((40, 40), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(sidebar_header, image=logo_photo, bg=SECONDARY_COLOR)
            logo_label.image = logo_photo
            logo_label.pack(side=tk.LEFT, padx=10, pady=20)
        except:
            logo_text = tk.Label(sidebar_header, text="JJ", font=("Helvetica", 18, "bold"), 
                               fg=PRIMARY_COLOR, bg="white", width=2, height=1)
            logo_text.pack(side=tk.LEFT, padx=10, pady=20)

        # Названия секций
        sections_label = tk.Label(self.sidebar, text="Правовой ассистент", 
                                font=("Helvetica", 14, "bold"), fg=TEXT_COLOR, bg=SECONDARY_COLOR)
        sections_label.pack(pady=10)

        # Разделительная линия
        separator = tk.Frame(self.sidebar, height=2, bg=ACCENT_COLOR)
        separator.pack(fill=tk.X, pady=5)

        # Кнопки в боковой панели
        button_style = {
            "font": BUTTON_FONT,
            "bg": SECONDARY_COLOR,
            "fg": TEXT_COLOR,
            "bd": 0,
            "highlightthickness": 0,
            "activebackground": ACCENT_COLOR,
            "activeforeground": TEXT_COLOR,
            "cursor": "hand2",
            "anchor": "w",
            "width": 20,
            "pady": 8
        }
        
        # Добавляем кнопки с иконками
        self.new_chat_btn = tk.Button(self.sidebar, text="🔄 Новый разговор", 
                                     command=self.new_conversation, **button_style)
        self.new_chat_btn.pack(fill=tk.X, pady=2, padx=5)
        
        self.save_chat_btn = tk.Button(self.sidebar, text="💾 Сохранить чат", 
                                      command=self.save_conversation, **button_style)
        self.save_chat_btn.pack(fill=tk.X, pady=2, padx=5)
        
        self.history_btn = tk.Button(self.sidebar, text="📋 История чатов", 
                                    command=self.show_history, **button_style)
        self.history_btn.pack(fill=tk.X, pady=2, padx=5)
        
        # Часто задаваемые вопросы
        faq_label = tk.Label(self.sidebar, text="Популярные вопросы:", 
                           font=("Helvetica", 12, "bold"), fg=TEXT_COLOR, bg=SECONDARY_COLOR)
        faq_label.pack(anchor="w", padx=10, pady=(20, 5))
        
        faqs = [
            "❓ Как открыть ИП?",
            "❓ Налоговый вычет",
            "❓ Трудовой договор",
            "❓ Регистрация ТОО"
        ]
        
        for faq in faqs:
            faq_btn = tk.Button(self.sidebar, text=faq, **button_style)
            faq_btn.pack(fill=tk.X, pady=1, padx=5)
            faq_btn.configure(command=lambda q=faq[2:]: self.ask_faq(q))
            # Добавляем эффекты при наведении
            faq_btn.bind("<Enter>", lambda e, b=faq_btn: b.config(bg=PRIMARY_COLOR))
            faq_btn.bind("<Leave>", lambda e, b=faq_btn: b.config(bg=SECONDARY_COLOR))
        
        # Добавляем версию внизу сайдбара
        version_label = tk.Label(self.sidebar, text="Версия 1.2.0", 
                               font=("Helvetica", 8), fg="#888888", bg=SECONDARY_COLOR)
        version_label.pack(side=tk.BOTTOM, pady=10)

        # Правая панель (основной контент)
        right_panel = tk.Frame(main_frame, bg=BG_COLOR)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Заголовок
        header = tk.Frame(right_panel, bg=PRIMARY_COLOR, height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(header, text="JYLDAM JAUAP", font=("Helvetica", 24, "bold"), 
                       fg=TEXT_COLOR, bg=PRIMARY_COLOR)
        title.pack(side=tk.LEFT, padx=20, pady=20)

        subtitle = tk.Label(header, text="Правовой ассистент", font=("Helvetica", 12), 
                          fg=TEXT_COLOR, bg=PRIMARY_COLOR)
        subtitle.pack(side=tk.LEFT, padx=10, pady=20)
        
        # Текущая дата
        current_date = datetime.now().strftime("%d.%m.%Y")
        date_label = tk.Label(header, text=current_date, font=("Helvetica", 12), 
                            fg=TEXT_COLOR, bg=PRIMARY_COLOR)
        date_label.pack(side=tk.RIGHT, padx=20, pady=20)

        # Фрейм для чата
        self.chat_container = tk.Frame(right_panel, bg=BG_COLOR)
        self.chat_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Создаем Canvas для прокрутки
        self.canvas = tk.Canvas(self.chat_container, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.chat_container, orient="vertical", command=self.canvas.yview)
        self.message_container = tk.Frame(self.canvas, bg=BG_COLOR)
        
        # Настраиваем прокрутку
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.message_container, anchor="nw", width=self.canvas.winfo_width())
        
        # Обновляем размер окна при изменении размера холста
        def configure_message_container(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
            
        self.canvas.bind("<Configure>", configure_message_container)
        
        # Обновляем область прокрутки
        def configure_scroll_region(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
        self.message_container.bind("<Configure>", configure_scroll_region)
        
        # Добавляем кнопку прокрутки вниз
        self.scroll_btn_frame = tk.Frame(self.chat_container, bg=BG_COLOR)
        self.scroll_btn_frame.place(relx=0.95, rely=0.9)
        
        self.scroll_btn = tk.Button(self.scroll_btn_frame, text="↓", font=("Helvetica", 16), 
                                  bg=PRIMARY_COLOR, fg=TEXT_COLOR, bd=0, padx=5, pady=0,
                                  command=self.scroll_to_bottom, cursor="hand2")
        self.scroll_btn.pack()

        # Нижняя панель для ввода сообщений
        input_panel = tk.Frame(right_panel, bg=SECONDARY_COLOR)
        input_panel.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Многострочное поле ввода с прокруткой
        self.input_frame = tk.Frame(input_panel, bg=SECONDARY_COLOR, padx=15, pady=10)
        self.input_frame.pack(fill=tk.X)
        
        self.input_box = scrolledtext.ScrolledText(self.input_frame, bg=TEXT_COLOR, fg=SECONDARY_COLOR, 
                                                 font=FONT, bd=1, relief="solid", height=3)
        self.input_box.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 10))
        self.input_box.bind("<Return>", self.handle_return)
        self.input_box.bind("<Shift-Return>", self.add_newline)
        
        # Подсказка для поля ввода
        self.input_box.insert(tk.INSERT, "Введите ваш вопрос...")
        self.input_box.config(fg="gray")
        
        def on_focus_in(event):
            if self.input_box.get("1.0", "end-1c") == "Введите ваш вопрос...":
                self.input_box.delete("1.0", tk.END)
                self.input_box.config(fg=SECONDARY_COLOR)
                
        def on_focus_out(event):
            if not self.input_box.get("1.0", "end-1c").strip():
                self.input_box.insert("1.0", "Введите ваш вопрос...")
                self.input_box.config(fg="gray")
                
        self.input_box.bind("<FocusIn>", on_focus_in)
        self.input_box.bind("<FocusOut>", on_focus_out)
        
        # Кнопки действий
        buttons_frame = tk.Frame(self.input_frame, bg=SECONDARY_COLOR)
        buttons_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.send_button = tk.Button(buttons_frame, text="Отправить", bg=ACCENT_COLOR, fg=TEXT_COLOR,
                                   font=BUTTON_FONT, bd=0, padx=15, pady=8, 
                                   command=self.send_message, cursor="hand2")
        self.send_button.pack(side=tk.BOTTOM)

    def show_welcome_message(self):
        """Показываем приветственное сообщение"""
        welcome_msg = (
            "👋 Добро пожаловать в Правовой ассистент Jyldam jauap!\n\n"
            "Я помогу вам с юридическими вопросами по законодательству Казахстана. "
            "Вы можете спросить меня о:\n"
            "• Регистрации бизнеса (ИП, ТОО)\n"
            "• Налогообложении\n"
            "• Трудовом праве\n"
            "• Договорах и сделках\n"
            "• Защите прав потребителей\n\n"
            "Как я могу помочь вам сегодня?"
        )
        self.display_message(welcome_msg, "ai")

    def handle_return(self, event):
        """Обрабатываем нажатие Enter для отправки сообщения"""
        # Предотвращаем стандартное поведение (добавление новой строки)
        self.input_box.unbind("<Return>")
        # Отправляем сообщение
        self.send_message()
        # Восстанавливаем обработку Enter
        self.root.after(100, lambda: self.input_box.bind("<Return>", self.handle_return))
        return "break"  # Предотвращаем стандартное поведение

    def add_newline(self, event):
        """Добавляем новую строку при Shift+Enter"""
        return None  # Разрешаем стандартное поведение

    def send_message(self, event=None):
        """Отправка сообщения и запрос к OpenAI"""
        if self.is_requesting:
            return

        user_message = self.input_box.get("1.0", tk.END).strip()
        if not user_message or user_message == "Введите ваш вопрос...":
            return

        self.input_box.delete("1.0", tk.END)
        self.display_message(user_message, "user")
        
        # Отмечаем, что разговор начат
        self.conversation_started = True

        self.message_history.append({"role": "user", "content": user_message})
        self.is_requesting = True

        # Показываем индикатор загрузки
        self.show_loading_indicator()

        # Запускаем поток для получения ответа
        threading.Thread(target=self.get_ai_response, daemon=True).start()
        
        # Прокручиваем чат вниз
        self.scroll_to_bottom()

    def show_loading_indicator(self):
        """Показываем анимированный индикатор загрузки"""
        self.loading_frame = tk.Frame(self.message_container, bg=BG_COLOR)
        self.loading_frame.pack(anchor="w", padx=10, pady=5, fill="x")
        
        # Создаем фрейм с аватаром AI
        avatar_frame = tk.Frame(self.loading_frame, bg=BG_COLOR)
        avatar_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        # Аватар AI
        ai_avatar = tk.Label(avatar_frame, text="AI", font=("Helvetica", 12, "bold"), 
                           fg=TEXT_COLOR, bg=PRIMARY_COLOR, width=3, height=2)
        ai_avatar.pack()
        
        # Пузырь сообщения
        bubble = tk.Frame(self.loading_frame, bg=AI_BG, padx=15, pady=10,
                        highlightbackground=SECONDARY_COLOR, highlightthickness=1)
        bubble.pack(side=tk.LEFT, anchor="w")
        
        # Точки загрузки
        self.loading_label = tk.Label(bubble, text="Генерирую ответ", 
                                    font=FONT, bg=AI_BG, fg=TEXT_COLOR)
        self.loading_label.pack()
        
        # Обновляем прокрутку
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)  # Прокручиваем до конца

    def update_loading_animation(self):
        """Обновляем анимацию загрузки с проверкой существования элементов"""
        try:
            if not hasattr(self, 'loading_label') or not self.loading_label.winfo_exists():
                return False
                
            dots = ["", ".", "..", "..."]
            for dot in dots:
                # Проверяем существование метки перед обновлением
                if not hasattr(self, 'loading_label') or not self.loading_label.winfo_exists():
                    return False
                    
                # Безопасное обновление UI
                try:
                    self.loading_label.config(text=f"Генерирую ответ{dot}")
                    self.root.update_idletasks()  # Используем update_idletasks вместо update
                    time.sleep(0.2)  # Уменьшаем задержку для более быстрой анимации
                except tk.TclError:
                    # Обрабатываем случай, когда виджет был уничтожен
                    return False
                    
            return True
        except Exception as e:
            print(f"Ошибка анимации: {str(e)}")
            return False

    def get_ai_response(self):
        """Запрос к OpenAI API"""
        # Показываем анимацию не более 10 секунд (максимальное время ожидания)
        animation_counter = 0
        max_animation_cycles = 10
        
        while animation_counter < max_animation_cycles and self.update_loading_animation():
            animation_counter += 1
        
        try:
            # Устанавливаем таймаут для запроса
            openai.api_requestor.TIMEOUT_SECS = 30
            
            # Запрос к API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Используем более быструю модель, можно вернуть gpt-4 позже
                messages=self.message_history,
                max_tokens=1000,
                timeout=30  # Добавляем явный таймаут для запроса
            )
            
            # Обработка ответа с проверкой наличия необходимых полей
            if 'choices' in response and len(response['choices']) > 0 and 'message' in response['choices'][0]:
                ai_response = response['choices'][0]['message']['content']
                self.message_history.append({"role": "assistant", "content": ai_response})
                
                # Удаляем индикатор загрузки через tkinter main thread
                def update_ui():
                    # Удаляем индикатор загрузки
                    if hasattr(self, 'loading_frame') and self.loading_frame.winfo_exists():
                        self.loading_frame.destroy()
                    
                    # Отображаем ответ
                    self.display_message(ai_response, "ai")
                    
                    # Прокручиваем чат вниз
                    self.scroll_to_bottom()
                    
                    # Отмечаем, что обработка запроса завершена
                    self.is_requesting = False
                
                # Запускаем обновление UI в главном потоке tkinter
                self.root.after(100, update_ui)
            else:
                raise Exception("Не удалось получить ответ от API. Попробуйте еще раз.")
                
        except Exception as e:
            print(f"Ошибка API: {str(e)}")  # Выводим ошибку в консоль для отладки
            
            # Обрабатываем ошибку в главном потоке tkinter
            def handle_error():
                if hasattr(self, 'loading_frame') and self.loading_frame.winfo_exists():
                    self.loading_frame.destroy()
                self.display_message(f"Ошибка: {str(e)}\nПопробуйте задать вопрос еще раз или перезапустить приложение.", "error")
                self.is_requesting = False
            
            self.root.after(100, handle_error)

    def display_message(self, message, sender):
        """Отображение сообщений в улучшенном стиле"""
        # Создаем карточку сообщения
        message_card = tk.Frame(self.message_container, bg=BG_COLOR)
        
        if sender == "user":
            message_card.pack(padx=10, pady=5, fill="x")
            
            # Фрейм для контента
            content_frame = tk.Frame(message_card, bg=BG_COLOR)
            content_frame.pack(side=tk.RIGHT)
            
            # Аватар пользователя
            avatar_frame = tk.Frame(content_frame, bg=BG_COLOR)
            avatar_frame.pack(side=tk.RIGHT, padx=(10, 0))
            
            user_avatar = tk.Label(avatar_frame, text="Вы", font=("Helvetica", 12, "bold"), 
                                 fg=PRIMARY_COLOR, bg="#FFFFFF", width=3, height=2,
                                 borderwidth=1, relief="solid")
            user_avatar.pack()
            
            # Пузырь сообщения с закругленными углами
            bubble = tk.Frame(content_frame, bg=USER_BG, padx=15, pady=10,
                           highlightbackground=SECONDARY_COLOR, highlightthickness=1)
            bubble.pack(side=tk.RIGHT)
            
            # Текст сообщения
            msg_label = tk.Label(bubble, text=message, wraplength=500, font=FONT, 
                               justify="left", bg=USER_BG, fg=SECONDARY_COLOR)
            msg_label.pack()
            
            # Сохраняем сообщение
            self.chat_messages.append({"sender": "user", "message": message, "time": datetime.now().strftime("%H:%M")})
            
        elif sender == "ai":
            message_card.pack(padx=10, pady=5, fill="x")
            
            # Фрейм для контента
            content_frame = tk.Frame(message_card, bg=BG_COLOR)
            content_frame.pack(side=tk.LEFT)
            
            # Аватар AI
            avatar_frame = tk.Frame(content_frame, bg=BG_COLOR)
            avatar_frame.pack(side=tk.LEFT, padx=(0, 10))
            
            ai_avatar = tk.Label(avatar_frame, text="AI", font=("Helvetica", 12, "bold"), 
                               fg=TEXT_COLOR, bg=PRIMARY_COLOR, width=3, height=2)
            ai_avatar.pack()
            
            # Пузырь сообщения с закругленными углами
            bubble = tk.Frame(content_frame, bg=AI_BG, padx=15, pady=10,
                           highlightbackground=SECONDARY_COLOR, highlightthickness=1)
            bubble.pack(side=tk.LEFT)
            
            # Текст сообщения
            msg_label = tk.Label(bubble, text=message, wraplength=500, font=FONT, 
                               justify="left", bg=AI_BG, fg=TEXT_COLOR)
            msg_label.pack()
            
            # Кнопки действий для сообщения AI
            actions_frame = tk.Frame(bubble, bg=AI_BG)
            actions_frame.pack(anchor="e", pady=(10, 0))
            
            # Кнопка копирования
            copy_btn = tk.Button(actions_frame, text="Копировать", font=("Helvetica", 8), 
                               bg=SECONDARY_COLOR, fg=TEXT_COLOR, bd=0, padx=5, pady=2,
                               command=lambda: self.copy_to_clipboard(message))
            copy_btn.pack(side=tk.LEFT, padx=2)
            
            # Кнопки обратной связи
            thumbs_up = tk.Button(actions_frame, text="👍", font=("Helvetica", 8), 
                                bg=SECONDARY_COLOR, fg=TEXT_COLOR, bd=0, padx=5, pady=2,
                                command=lambda: self.feedback("positive"))
            thumbs_up.pack(side=tk.LEFT, padx=2)
            
            thumbs_down = tk.Button(actions_frame, text="👎", font=("Helvetica", 8), 
                                  bg=SECONDARY_COLOR, fg=TEXT_COLOR, bd=0, padx=5, pady=2,
                                  command=lambda: self.feedback("negative"))
            thumbs_down.pack(side=tk.LEFT, padx=2)
            
            # Сохраняем сообщение
            self.chat_messages.append({"sender": "ai", "message": message, "time": datetime.now().strftime("%H:%M")})
            
        else:  # error
            message_card.pack(padx=10, pady=5, fill="x")
            
            # Фрейм для ошибки
            error_frame = tk.Frame(message_card, bg="#FFEBEE", padx=15, pady=10,
                                 highlightbackground="#B71C1C", highlightthickness=1)
            error_frame.pack()
            
            # Иконка ошибки
            error_icon = tk.Label(error_frame, text="⚠️", font=("Helvetica", 14))
            error_icon.pack(side=tk.LEFT, padx=(0, 10))
            
            # Текст ошибки
            error_label = tk.Label(error_frame, text=message, wraplength=500, font=FONT, 
                                 justify="left", bg="#FFEBEE", fg="#B71C1C")
            error_label.pack(side=tk.LEFT)
            
            # Кнопка повтора
            retry_btn = tk.Button(error_frame, text="Повторить", font=("Helvetica", 10), 
                                bg=PRIMARY_COLOR, fg=TEXT_COLOR, bd=0, padx=10, pady=5,
                                command=self.retry_last_request)
            retry_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Обновляем прокрутку
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)  # Прокручиваем до конца

    def copy_to_clipboard(self, text):
        """Копирует текст в буфер обмена, используя встроенные функции tkinter"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        
        # Показываем уведомление
        notification = tk.Label(self.root, text="Текст скопирован в буфер обмена", 
                              font=("Helvetica", 10), bg=SECONDARY_COLOR, fg=TEXT_COLOR,
                              padx=10, pady=5)
        notification.place(relx=0.5, rely=0.1, anchor="center")
        
        # Удаляем уведомление через 2 секунды
        self.root.after(2000, notification.destroy)

    def feedback(self, feedback_type):
        """Обрабатываем обратную связь от пользователя"""
        message = "Спасибо за вашу обратную связь! Мы используем её для улучшения качества ответов."
        messagebox.showinfo("Обратная связь", message)

    def retry_last_request(self):
        """Повторяем последний запрос"""
        if len(self.message_history) > 1:
            # Удаляем последнее сообщение пользователя из истории (чтобы избежать дублирования)
            user_message = self.message_history[-1]["content"]
            self.message_history = self.message_history[:-1]
            
            # Отправляем сообщение снова
            self.input_box.delete("1.0", tk.END)
            self.input_box.insert(tk.END, user_message)
            self.send_message()

    def scroll_to_bottom(self):
        """Прокручивает чат до последнего сообщения"""
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)

    def new_conversation(self):
        """Начинаем новый разговор"""
        if self.conversation_started:
            if messagebox.askyesno("Новый разговор", "Начать новый разговор? Текущий разговор будет удален."):
                # Сохраняем текущий разговор автоматически, если он не пустой
                if self.chat_messages:
                    self.save_conversation(auto=True)
                
                # Очищаем контейнер сообщений
                for widget in self.message_container.winfo_children():
                    widget.destroy()
                
                # Сбрасываем историю сообщений, оставляя системное сообщение
                self.message_history = [self.message_history[0]]
                self.chat_messages = []
                self.conversation_started = False
                
                # Показываем приветственное сообщение
                self.show_welcome_message()
        else:
            # Если разговор еще не начат, просто показываем приветственное сообщение
            for widget in self.message_container.winfo_children():
                widget.destroy()
            self.show_welcome_message()

    def save_conversation(self, auto=False):
        """Сохраняет текущий разговор в файл"""
        if not self.chat_messages:
            if not auto:
                messagebox.showinfo("Информация", "Нет сообщений для сохранения.")
            return
            
        # Генерируем имя файла на основе даты и времени
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"chat_history/chat_{timestamp}.json"
        
        filename = default_filename
        if not auto:
            filename = filedialog.asksaveasfilename(
                initialdir="chat_history",
                title="Сохранить разговор",
                filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*")),
                defaultextension=".json",
                initialfile=f"chat_{timestamp}.json"
            )
            
        if filename:
            try:
                # Создаем структуру данных для сохранения
                chat_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "messages": self.chat_messages
                }
                
                # Сохраняем в JSON файл
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(chat_data, f, ensure_ascii=False, indent=4)
                    
                if not auto:
                    messagebox.showinfo("Успех", f"Разговор сохранен в файл:\n{filename}")
            except Exception as e:
                if not auto:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить разговор: {str(e)}")

    def show_history(self):
        """Показывает историю сохраненных разговоров"""
        # Проверяем наличие файлов истории
        chat_files = []
        try:
            for file in os.listdir("chat_history"):
                if file.endswith(".json"):
                    chat_files.append(file)
        except Exception:
            pass
            
        if not chat_files:
            messagebox.showinfo("История чатов", "История чатов пуста.")
            return
            
        # Создаем окно истории
        history_window = tk.Toplevel(self.root)
        history_window.title("История чатов")
        history_window.geometry("600x400")
        history_window.configure(bg=BG_COLOR)
        
        # Заголовок
        tk.Label(history_window, text="История чатов", font=("Helvetica", 16, "bold"), 
               bg=BG_COLOR, fg=PRIMARY_COLOR).pack(pady=10)
        
        # Фрейм для списка с прокруткой
        list_frame = tk.Frame(history_window, bg=BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Создаем Listbox с прокруткой
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        chat_listbox = tk.Listbox(list_frame, font=FONT, bg=TEXT_COLOR, fg=SECONDARY_COLOR,
                                 selectbackground=PRIMARY_COLOR, selectforeground=TEXT_COLOR,
                                 height=15, width=50)
        chat_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        chat_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=chat_listbox.yview)
        
        # Заполняем список данными
        for file in sorted(chat_files, reverse=True):
            try:
                with open(os.path.join("chat_history", file), 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                    timestamp = chat_data.get("timestamp", "Неизвестно")
                    message_count = len(chat_data.get("messages", []))
                    
                    # Получаем первый обмен сообщениями для превью
                    preview = ""
                    for msg in chat_data.get("messages", []):
                        if msg.get("sender") == "user":
                            preview = msg.get("message", "")[:50]
                            if len(preview) > 47:
                                preview += "..."
                            break
                            
                    chat_listbox.insert(tk.END, f"{timestamp} ({message_count} сообщ.): {preview}")
                    # Сохраняем имя файла как данные элемента
                    chat_listbox.itemconfig(tk.END, {'filename': file})
            except Exception:
                chat_listbox.insert(tk.END, f"{file} (ошибка чтения)")
        
        # Кнопки действий
        buttons_frame = tk.Frame(history_window, bg=BG_COLOR)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Функция для загрузки выбранного чата
        def load_selected_chat():
            selection = chat_listbox.curselection()
            if not selection:
                messagebox.showinfo("Выбор чата", "Выберите чат для загрузки.")
                return
                
            filename = getattr(chat_listbox, 'itemcget')(selection[0], 'filename')
            if not filename:
                return
                
            try:
                with open(os.path.join("chat_history", filename), 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                    
                # Спрашиваем подтверждение
                if messagebox.askyesno("Загрузка чата", 
                                     "Загрузить выбранный чат? Текущий разговор будет заменен."):
                    try:
                        # Очищаем текущий чат
                        for widget in self.message_container.winfo_children():
                            widget.destroy()
                            
                        # Сбрасываем историю сообщений, оставляя системное сообщение
                        self.message_history = [self.message_history[0]]
                        self.chat_messages = []
                        
                        # Загружаем сообщения из файла с обработкой ошибок
                        loaded_messages = chat_data.get("messages", [])
                        
                        if not loaded_messages:
                            messagebox.showinfo("Информация", "Загружаемый чат не содержит сообщений.")
                            return
                            
                        for msg in loaded_messages:
                            try:
                                sender = msg.get("sender")
                                message = msg.get("message", "")
                                
                                if not sender or not message:
                                    continue
                                
                                # Отображаем сообщение
                                self.display_message(message, sender)
                                
                                # Добавляем в историю для API
                                if sender == "user":
                                    self.message_history.append({"role": "user", "content": message})
                                elif sender == "ai":
                                    self.message_history.append({"role": "assistant", "content": message})
                            except Exception as e:
                                print(f"Ошибка загрузки сообщения: {str(e)}")
                                continue
                        
                        history_window.destroy()
                        self.conversation_started = True
                        
                        # Прокручиваем до последнего сообщения
                        self.scroll_to_bottom()
                        
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Ошибка при загрузке чата: {str(e)}")
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить чат: {str(e)}")
        
        # Функция для удаления выбранного чата
        def delete_selected_chat():
            selection = chat_listbox.curselection()
            if not selection:
                messagebox.showinfo("Выбор чата", "Выберите чат для удаления.")
                return
                
            filename = getattr(chat_listbox, 'itemcget')(selection[0], 'filename')
            if not filename:
                return
                
            # Спрашиваем подтверждение
            if messagebox.askyesno("Удаление чата", 
                                 f"Вы уверены, что хотите удалить:\n{filename}?"):
                try:
                    os.remove(os.path.join("chat_history", filename))
                    chat_listbox.delete(selection)
                    messagebox.showinfo("Успех", "Чат успешно удален.")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить чат: {str(e)}")
        
        # Добавляем кнопки
        load_btn = tk.Button(buttons_frame, text="Загрузить", font=BUTTON_FONT, 
                           bg=PRIMARY_COLOR, fg=TEXT_COLOR, command=load_selected_chat)
        load_btn.pack(side=tk.LEFT, padx=20)
        
        delete_btn = tk.Button(buttons_frame, text="Удалить", font=BUTTON_FONT, 
                             bg=SECONDARY_COLOR, fg=TEXT_COLOR, command=delete_selected_chat)
        delete_btn.pack(side=tk.LEFT, padx=20)
        
        close_btn = tk.Button(buttons_frame, text="Закрыть", font=BUTTON_FONT, 
                            bg=LIGHT_GRAY, fg=SECONDARY_COLOR, command=history_window.destroy)
        close_btn.pack(side=tk.RIGHT, padx=20)

    def ask_faq(self, question):
        """Задает частый вопрос в чате"""
        self.input_box.delete("1.0", tk.END)
        self.input_box.insert(tk.END, question)
        self.input_box.config(fg=SECONDARY_COLOR)
        self.send_message()

def open_chat():
    """Запуск окна чата"""
    chat_window = tk.Toplevel()
    ChatApp(chat_window)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    open_chat()
    root.mainloop()