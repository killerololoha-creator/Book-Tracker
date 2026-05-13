import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class Book:
    """Класс модели книги"""

    def __init__(self, title: str, author: str, genre: str, pages: int):
        self.title = title
        self.author = author
        self.genre = genre
        self.pages = pages
        self.date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict:
        """Преобразование в словарь для JSON"""
        return {
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "pages": self.pages,
            "date_added": self.date_added
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Book':
        """Создание книги из словаря"""
        book = cls(data["title"], data["author"], data["genre"], data["pages"])
        book.date_added = data.get("date_added", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return book


class BookTracker:
    """Главное приложение"""

    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x600")
        self.root.resizable(True, True)

        # Данные
        self.books = []
        self.data_file = "books.json"

        # Загрузка сохраненных книг
        self.load_books()

        # Создание интерфейса
        self.create_widgets()

        # Обновление отображения
        self.refresh_book_list()

    def create_widgets(self):
        """Создание GUI интерфейса"""

        # Главная рамка
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Заголовок
        title_label = ttk.Label(main_frame, text="📚 Book Tracker - Мои прочитанные книги",
                                font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Левая панель - форма добавления книги
        left_frame = ttk.LabelFrame(main_frame, text="Добавить новую книгу", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Поля ввода
        ttk.Label(left_frame, text="Название книги:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(left_frame, width=30, font=("Arial", 10))
        self.title_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(left_frame, text="Автор:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.author_entry = ttk.Entry(left_frame, width=30, font=("Arial", 10))
        self.author_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(left_frame, text="Жанр:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.genre_combo = ttk.Combobox(left_frame, values=[
            "Роман", "Детектив", "Фантастика", "Научная литература",
            "Поэзия", "Биография", "Приключения", "Ужасы", "Другое"
        ], width=27, state="readonly")
        self.genre_combo.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Label(left_frame, text="Количество страниц:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.pages_entry = ttk.Entry(left_frame, width=30, font=("Arial", 10))
        self.pages_entry.grid(row=3, column=1, pady=5, padx=(10, 0))

        # Кнопки
        ttk.Button(left_frame, text="➕ Добавить книгу", command=self.add_book, width=25).grid(row=4, column=0, columnspan=2, pady=20)

        # Статистика
        stats_frame = ttk.LabelFrame(left_frame, text="📊 Статистика", padding="10")
        stats_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 10))
        self.stats_label.pack()

        # Правая панель - список книг и фильтры
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # Фильтры
        filter_frame = ttk.LabelFrame(right_frame, text="🔍 Фильтрация", padding="10")
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Фильтр по жанру
        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, padx=5)
        self.filter_genre = ttk.Combobox(filter_frame, values=["Все"] + [
            "Роман", "Детектив", "Фантастика", "Научная литература",
            "Поэзия", "Биография", "Приключения", "Ужасы", "Другое"
        ], width=15, state="readonly")
        self.filter_genre.grid(row=0, column=1, padx=5)
        self.filter_genre.set("Все")

        # Фильтр по страницам
        ttk.Label(filter_frame, text="Страниц:").grid(row=0, column=2, padx=5)
        self.filter_pages = ttk.Combobox(filter_frame, values=["Все", "> 200", "≤ 200", "> 300", "≤ 300"],
                                         width=10, state="readonly")
        self.filter_pages.grid(row=0, column=3, padx=5)
        self.filter_pages.set("Все")

        ttk.Button(filter_frame, text="Применить фильтр", command=self.refresh_book_list).grid(row=0, column=4, padx=10)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).grid(row=0, column=5)

        # Таблица книг
        table_frame = ttk.LabelFrame(right_frame, text="📖 Список книг", padding="10")
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Создание таблицы
        columns = ("Название", "Автор", "Жанр", "Страниц", "Дата добавления")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Настройка колонок
        self.tree.heading("Название", text="Название")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Страниц", text="Страниц")
        self.tree.heading("Дата добавления", text="Дата добавления")

        self.tree.column("Название", width=200)
        self.tree.column("Автор", width=150)
        self.tree.column("Жанр", width=120)
        self.tree.column("Страниц", width=80)
        self.tree.column("Дата добавления", width=150)

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Кнопки управления
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=2, column=0, pady=10)

        ttk.Button(button_frame, text="🗑️ Удалить выбранную книгу", command=self.delete_book).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="💾 Сохранить данные", command=self.save_books).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📁 Загрузить данные", command=self.load_books).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Показать статистику", command=self.show_statistics).pack(side=tk.LEFT, padx=5)

        # Привязка двойного щелчка для редактирования
        self.tree.bind("<Double-1>", self.edit_book)

        # Привязка Enter для добавления книги
        self.pages_entry.bind('<Return>', lambda event: self.add_book())

    def add_book(self):
        """Добавление новой книги"""
        # Получение данных из полей
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_combo.get()
        pages_str = self.pages_entry.get().strip()

        # Валидация полей
        if not title:
            messagebox.showerror("Ошибка", "Название книги не может быть пустым!")
            return

        if not author:
            messagebox.showerror("Ошибка", "Имя автора не может быть пустым!")
            return

        if not genre:
            messagebox.showerror("Ошибка", "Выберите жанр!")
            return

        # Негативный тест: проверка количества страниц
        try:
            pages = int(pages_str)
            if pages <= 0:
                messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
                return
            if pages > 10000:
                if not messagebox.askyesno("Подтверждение", "Количество страниц очень большое (>10000). Продолжить?"):
                    return
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")
            return

        # Создание книги
        book = Book(title, author, genre, pages)
        self.books.append(book)

        # Очистка полей
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_combo.set('')
        self.pages_entry.delete(0, tk.END)

        # Сохранение и обновление
        self.save_books()
        self.refresh_book_list()

        messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")

    def delete_book(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return

        item = self.tree.item(selected[0])
        title = item['values'][0]

        if messagebox.askyesno("Подтверждение", f"Удалить книгу '{title}'?"):
            # Удаление из списка
            for i, book in enumerate(self.books):
                if book.title == title and book.author == item['values'][1]:
                    del self.books[i]
                    break

            self.save_books()
            self.refresh_book_list()
            messagebox.showinfo("Успех", f"Книга '{title}' удалена!")

    def edit_book(self, event):
        """Редактирование книги по двойному щелчку"""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        old_title = item['values'][0]
        old_author = item['values'][1]

        # Поиск книги
        book = None
        for b in self.books:
            if b.title == old_title and b.author == old_author:
                book = b
                break

        if not book:
            return

        # Диалог редактирования
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактирование книги")
        edit_window.geometry("400x350")
        edit_window.resizable(False, False)

        # Центрирование окна
        edit_window.transient(self.root)
        edit_window.grab_set()

        # Поля редактирования
        ttk.Label(edit_window, text="Название книги:", font=("Arial", 10)).pack(pady=(20, 5))
        title_entry = ttk.Entry(edit_window, width=40, font=("Arial", 10))
        title_entry.insert(0, book.title)
        title_entry.pack(pady=5)

        ttk.Label(edit_window, text="Автор:", font=("Arial", 10)).pack(pady=5)
        author_entry = ttk.Entry(edit_window, width=40, font=("Arial", 10))
        author_entry.insert(0, book.author)
        author_entry.pack(pady=5)

        ttk.Label(edit_window, text="Жанр:", font=("Arial", 10)).pack(pady=5)
        genre_combo = ttk.Combobox(edit_window, values=[
            "Роман", "Детектив", "Фантастика", "Научная литература",
            "Поэзия", "Биография", "Приключения", "Ужасы", "Другое"
        ], width=37, state="readonly")
        genre_combo.set(book.genre)
        genre_combo.pack(pady=5)

        ttk.Label(edit_window, text="Количество страниц:", font=("Arial", 10)).pack(pady=5)
        pages_entry = ttk.Entry(edit_window, width=40, font=("Arial", 10))
        pages_entry.insert(0, str(book.pages))
        pages_entry.pack(pady=5)

        def save_edit():
            try:
                new_title = title_entry.get().strip()
                new_author = author_entry.get().strip()
                new_genre = genre_combo.get()
                new_pages = int(pages_entry.get().strip())

                if not new_title:
                    messagebox.showerror("Ошибка", "Название не может быть пустым!")
                    return
                if not new_author:
                    messagebox.showerror("Ошибка", "Автор не может быть пустым!")
                    return
                if not new_genre:
                    messagebox.showerror("Ошибка", "Выберите жанр!")
                    return
                if new_pages <= 0:
                    messagebox.showerror("Ошибка", "Страниц должно быть положительным числом!")
                    return

                book.title = new_title
                book.author = new_author
                book.genre = new_genre
                book.pages = new_pages

                self.save_books()
                self.refresh_book_list()
                edit_window.destroy()
                messagebox.showinfo("Успех", "Книга обновлена!")

            except ValueError:
                messagebox.showerror("Ошибка", "Количество страниц должно быть числом!")

        ttk.Button(edit_window, text="Сохранить", command=save_edit).pack(pady=20)

    def refresh_book_list(self):
        """Обновление списка книг с учетом фильтров"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Фильтрация книг
        filtered_books = self.apply_filters()

        # Добавление книг в таблицу
        for book in filtered_books:
            self.tree.insert("", tk.END, values=(
                book.title,
                book.author,
                book.genre,
                book.pages,
                book.date_added
            ))

        # Обновление статистики
        self.update_stats()

    def apply_filters(self):
        """Применение фильтров к списку книг"""
        filtered = self.books.copy()

        # Фильтр по жанру
        genre_filter = self.filter_genre.get()
        if genre_filter != "Все":
            filtered = [b for b in filtered if b.genre == genre_filter]

        # Фильтр по количеству страниц
        pages_filter = self.filter_pages.get()
        if pages_filter == "> 200":
            filtered = [b for b in filtered if b.pages > 200]
        elif pages_filter == "≤ 200":
            filtered = [b for b in filtered if b.pages <= 200]
        elif pages_filter == "> 300":
            filtered = [b for b in filtered if b.pages > 300]
        elif pages_filter == "≤ 300":
            filtered = [b for b in filtered if b.pages <= 300]

        return filtered

    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_genre.set("Все")
        self.filter_pages.set("Все")
        self.refresh_book_list()

    def update_stats(self):
        """Обновление статистики в левой панели"""
        total_books = len(self.books)
        total_pages = sum(book.pages for book in self.books)
        avg_pages = total_pages // total_books if total_books > 0 else 0

        genres = {}
        for book in self.books:
            genres[book.genre] = genres.get(book.genre, 0) + 1

        most_common_genre = max(genres, key=genres.get) if genres else "Нет"

        stats_text = f"📚 Всего книг: {total_books}\n📖 Всего страниц: {total_pages}\n📊 Средняя длина: {avg_pages} стр.\n⭐ Популярный жанр: {most_common_genre}"
        self.stats_label.config(text=stats_text)

    def show_statistics(self):
        """Показать подробную статистику в отдельном окне"""
        if not self.books:
            messagebox.showinfo("Статистика", "Нет добавленных книг!")
            return

        stats_window = tk.Toplevel(self.root)
        stats_window.title("Детальная статистика")
        stats_window.geometry("500x400")
        stats_window.resizable(False, False)

        # Центрирование
        stats_window.transient(self.root)
        stats_window.grab_set()

        # Подсчет статистики
        total_books = len(self.books)
        total_pages = sum(book.pages for book in self.books)
        avg_pages = total_pages // total_books

        # Подсчет по жанрам
        genre_stats = {}
        for book in self.books:
            genre_stats[book.genre] = genre_stats.get(book.genre, 0) + 1

        # Подсчет по авторам
        author_stats = {}
        for book in self.books:
            author_stats[book.author] = author_stats.get(book.author, 0) + 1

        # Формирование текста
        stats_text = f"""📊 ДЕТАЛЬНАЯ СТАТИСТИКА
{'='*40}

📚 Общее количество книг: {total_books}
📖 Общее количество страниц: {total_pages}
📊 Среднее количество страниц: {avg_pages}

📚 ПО ЖАНРАМ:
{'-'*40}
"""
        for genre, count in sorted(genre_stats.items(), key=lambda x: x[1], reverse=True):
            stats_text += f"  • {genre}: {count} книг\n"

        stats_text += f"\n✍️ ПО АВТОРАМ:\n{'-'*40}\n"
        for author, count in sorted(author_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            stats_text += f"  • {author}: {count} книг\n"

        # Текстовое поле
        text_widget = tk.Text(stats_window, wrap=tk.WORD, font=("Courier", 10))
        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Button(stats_window, text="Закрыть", command=stats_window.destroy).pack(pady=10)

    def save_books(self):
        """Сохранение книг в JSON файл"""
        try:
            data = [book.to_dict() for book in self.books]
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
            return False

    def load_books(self):
        """Загрузка книг из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.books = [Book.from_dict(item) for item in data]
                self.refresh_book_list()
                messagebox.showinfo("Успех", "Данные загружены!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Файл с данными не найден!")


def main():
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
