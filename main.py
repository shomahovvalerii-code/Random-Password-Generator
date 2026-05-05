import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime
import pyperclip  # Для копирования в буфер обмена

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных паролей")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Данные истории
        self.history = []
        self.history_file = "password_history.json"
        
        # Загрузка истории
        self.load_history()
        
        # Стилизация
        self.setup_styles()
        
        # Создание GUI
        self.create_widgets()
        
    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))
        style.configure("Password.TLabel", font=("Courier", 14, "bold"), foreground="darkblue")
        
    def create_widgets(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Генератор случайных паролей", 
                               style="Title.TLabel")
        title_label.pack(pady=10)
        
        # Фрейм настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки пароля", padding=15)
        settings_frame.pack(fill="x", pady=10)
        
        # Длина пароля
        length_frame = ttk.Frame(settings_frame)
        length_frame.pack(fill="x", pady=5)
        
        ttk.Label(length_frame, text="Длина пароля:").pack(side="left", padx=5)
        
        self.length_var = tk.IntVar(value=12)
        self.length_scale = ttk.Scale(length_frame, from_=4, to=64, 
                                     orient="horizontal", variable=self.length_var,
                                     command=self.update_length_display)
        self.length_scale.pack(side="left", fill="x", expand=True, padx=10)
        
        self.length_display = ttk.Label(length_frame, text="12", width=3)
        self.length_display.pack(side="left", padx=5)
        
        # Чекбоксы для выбора символов
        checkboxes_frame = ttk.Frame(settings_frame)
        checkboxes_frame.pack(fill="x", pady=10)
        
        # Верхний ряд чекбоксов
        upper_frame = ttk.Frame(checkboxes_frame)
        upper_frame.pack(fill="x", pady=5)
        
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(upper_frame, text="Заглавные буквы (A-Z)", 
                       variable=self.use_uppercase).pack(side="left", padx=10)
        ttk.Checkbutton(upper_frame, text="Строчные буквы (a-z)", 
                       variable=self.use_lowercase).pack(side="left", padx=10)
        
        # Нижний ряд чекбоксов
        lower_frame = ttk.Frame(checkboxes_frame)
        lower_frame.pack(fill="x", pady=5)
        
        ttk.Checkbutton(lower_frame, text="Цифры (0-9)", 
                       variable=self.use_digits).pack(side="left", padx=10)
        ttk.Checkbutton(lower_frame, text="Спецсимволы (!@#$%^&*)", 
                       variable=self.use_special).pack(side="left", padx=10)
        
        # Дополнительные настройки
        options_frame = ttk.Frame(settings_frame)
        options_frame.pack(fill="x", pady=5)
        
        self.exclude_similar = tk.BooleanVar(value=False)
        self.avoid_ambiguous = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="Исключить похожие символы (i, l, 1, L, o, 0, O)", 
                       variable=self.exclude_similar).pack(side="left", padx=10)
        ttk.Checkbutton(options_frame, text="Избегать неоднозначных символов ({ } [ ] ( ) / \\ ' \" ` ~ , ; : . < >)", 
                       variable=self.avoid_ambiguous).pack(side="left", padx=10)
        
        # Кнопки действий
        buttons_frame = ttk.Frame(settings_frame)
        buttons_frame.pack(fill="x", pady=15)
        
        generate_btn = ttk.Button(buttons_frame, text="Сгенерировать пароль", 
                                 command=self.generate_password, width=20)
        generate_btn.pack(side="left", padx=5)
        
        copy_btn = ttk.Button(buttons_frame, text="Копировать в буфер", 
                             command=self.copy_to_clipboard, width=20)
        copy_btn.pack(side="left", padx=5)
        
        clear_btn = ttk.Button(buttons_frame, text="Очистить", 
                              command=self.clear_password, width=15)
        clear_btn.pack(side="left", padx=5)
        
        # Отображение сгенерированного пароля
        password_display_frame = ttk.LabelFrame(main_frame, text="Сгенерированный пароль", padding=10)
        password_display_frame.pack(fill="x", pady=10)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_display_frame, textvariable=self.password_var,
                                       font=("Courier", 14, "bold"), justify="center",
                                       state="readonly")
        self.password_entry.pack(fill="x", pady=5)
        
        # Критерии надежности пароля
        strength_frame = ttk.Frame(password_display_frame)
        strength_frame.pack(fill="x", pady=5)
        
        ttk.Label(strength_frame, text="Надёжность:").pack(side="left", padx=5)
        self.strength_var = tk.StringVar(value="Ожидание генерации...")
        self.strength_label = ttk.Label(strength_frame, textvariable=self.strength_var,
                                       font=("Arial", 10, "bold"))
        self.strength_label.pack(side="left", padx=5)
        
        # Прогресс-бар надёжности
        self.strength_bar = ttk.Progressbar(strength_frame, length=200, mode="determinate")
        self.strength_bar.pack(side="left", padx=10)
        
        # История паролей
        history_frame = ttk.LabelFrame(main_frame, text="История паролей", padding=10)
        history_frame.pack(fill="both", expand=True, pady=10)
        
        # Таблица истории
        columns = ("date", "password", "length", "strength")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, 
                                         show="headings", height=8)
        
        self.history_tree.heading("date", text="Дата")
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("strength", text="Надёжность")
        
        self.history_tree.column("date", width=150)
        self.history_tree.column("password", width=250)
        self.history_tree.column("length", width=80)
        self.history_tree.column("strength", width=100)
        
        # Скроллбар для истории
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", 
                                         command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления историей
        history_buttons_frame = ttk.Frame(main_frame)
        history_buttons_frame.pack(fill="x", pady=5)
        
        ttk.Button(history_buttons_frame, text="Копировать выбранный пароль", 
                  command=self.copy_selected_from_history).pack(side="left", padx=5)
        ttk.Button(history_buttons_frame, text="Очистить историю", 
                  command=self.clear_history).pack(side="left", padx=5)
        ttk.Button(history_buttons_frame, text="Экспорт истории", 
                  command=self.export_history).pack(side="left", padx=5)
        
        # Загрузка истории в таблицу
        self.display_history()
        
    def update_length_display(self, *args):
        """Обновление отображения длины пароля"""
        length = int(self.length_var.get())
        self.length_display.config(text=str(length))
    
    def get_characters(self):
        """Получение набора символов для генерации"""
        characters = ""
        
        if self.use_uppercase.get():
            characters += string.ascii_uppercase
        if self.use_lowercase.get():
            characters += string.ascii_lowercase
        if self.use_digits.get():
            characters += string.digits
        if self.use_special.get():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Исключение похожих символов
        if self.exclude_similar.get():
            similar = "il1Lo0O"
            characters = ''.join(c for c in characters if c not in similar)
        
        # Исключение неоднозначных символов
        if self.avoid_ambiguous.get():
            ambiguous = "{}[]()/\'\"`~,;:.<>"
            characters = ''.join(c for c in characters if c not in ambiguous)
        
        return characters
    
    def generate_password(self):
        """Генерация пароля"""
        characters = self.get_characters()
        
        if not characters:
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return
        
        length = int(self.length_var.get())
        
        if length < 4 or length > 64:
            messagebox.showerror("Ошибка", "Длина пароля должна быть от 4 до 64 символов!")
            return
        
        # Генерация пароля
        password = ''.join(random.choice(characters) for _ in range(length))
        
        # Отображение пароля
        self.password_var.set(password)
        
        # Оценка надёжности
        strength = self.calculate_strength(password)
        
        # Сохранение в историю
        self.add_to_history(password, strength)
        
        return password
    
    def calculate_strength(self, password):
        """Расчёт надёжности пароля"""
        score = 0
        
        # Длина
        length = len(password)
        if length >= 12:
            score += 3
        elif length >= 8:
            score += 2
        else:
            score += 1
        
        # Разнообразие символов
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        diversity = sum([has_upper, has_lower, has_digit, has_special])
        score += diversity * 2
        
        # Определение уровня надёжности
        if score >= 8:
            strength = "Очень надёжный"
            color = "green"
            bar_value = 100
        elif score >= 6:
            strength = "Надёжный"
            color = "darkgreen"
            bar_value = 75
        elif score >= 4:
            strength = "Средний"
            color = "orange"
            bar_value = 50
        else:
            strength = "Слабый"
            color = "red"
            bar_value = 25
        
        # Обновление отображения
        self.strength_var.set(strength)
        self.strength_label.config(foreground=color)
        self.strength_bar["value"] = bar_value
        
        return strength
    
    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            try:
                pyperclip.copy(password)
                # Самостоятельная реализация без pyperclip
                self.root.clipboard_clear()
                self.root.clipboard_append(password)
                messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
            except:
                pass
    
    def copy_selected_from_history(self):
        """Копирование выбранного пароля из истории"""
        selected_item = self.history_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите пароль из истории!")
            return
        
        password = self.history_tree.item(selected_item[0])['values'][1]
        try:
            pyperclip.copy(password)
            # Альтернативный способ
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        except:
            pass
    
    def clear_password(self):
        """Очистка поля с паролем"""
        self.password_var.set("")
        self.strength_var.set("Ожидание генерации...")
        self.strength_bar["value"] = 0
    
    def add_to_history(self, password, strength):
        """Добавление пароля в историю"""
        history_entry = {
            "date": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "password": password,
            "length": len(password),
            "strength": strength
        }
        
        self.history.append(history_entry)
        
        # Ограничение истории (храним последние 100 записей)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        self.save_history()
        self.display_history()
    
    def display_history(self):
        """Отображение истории в таблице"""
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Добавление записей (в обратном порядке - новые сверху)
        for entry in reversed(self.history):
            self.history_tree.insert("", "end", values=(
                entry["date"],
                entry["password"],
                entry["length"],
                entry["strength"]
            ))
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_history()
            self.display_history()
            messagebox.showinfo("Успех", "История очищена!")
    
    def export_history(self):
        """Экспорт истории в текстовый файл"""
        try:
            export_file = "passwords_export.txt"
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write("История сгенерированных паролей\n")
                f.write("=" * 50 + "\n\n")
                
                for entry in self.history:
                    f.write(f"Дата: {entry['date']}\n")
                    f.write(f"Пароль: {entry['password']}\n")
                    f.write(f"Длина: {entry['length']} символов\n")
                    f.write(f"Надёжность: {entry['strength']}\n")
                    f.write("-" * 30 + "\n")
            
            messagebox.showinfo("Успех", f"История экспортирована в файл {export_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать: {str(e)}")
    
    def save_history(self):
        """Сохранение истории в JSON"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    
    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except:
                self.history = []
        else:
            self.history = []

# Пасхальное яйцо - альтернативная версия без pyperclip для универсальности
def create_clipboard_copy(text):
    """Создание временного окна для копирования текста"""
    temp_root = tk.Tk()
    temp_root.withdraw()
    temp_root.clipboard_clear()
    temp_root.clipboard_append(text)
    temp_root.update()
    temp_root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()