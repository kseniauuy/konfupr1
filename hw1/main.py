import os
import tarfile
import io
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog


class ShellEmulatorGUI:
    def __init__(self, master):
        """Инициализация графического интерфейса и начальных настроек."""
        self.master = master
        self.master.title("Shell Emulator")  # Устанавливаем заголовок окна
        self.vfs_data = None  # Данные для виртуальной файловой системы (VFS)
        self.current_dir = None  # Текущая директория в виртуальной файловой системе
        self.log_file_path = os.path.join(os.getcwd(), 'log.txt')  # Путь к лог-файлу в текущей директории

        # Область вывода (отображение результатов команд)
        self.output_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=20)
        self.output_area.pack(padx=10, pady=10)

        # Область ввода команд пользователем
        self.input_area = tk.Entry(master, width=50)
        self.input_area.pack(padx=10, pady=10)
        self.input_area.bind("<Return>", self.process_command)  # Обработчик нажатия Enter для ввода команд

        # Кнопка для запуска виртуальной файловой системы
        self.start_button = tk.Button(master, text="Start VFS", command=self.start_vfs)
        self.start_button.pack(pady=5)

        # Отображение сообщения о создании лог-файла
        self.display_output(f"Log file created at: {self.log_file_path}")

    def log_action(self, action):
        """Записывает действие в лог файл."""
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(action + '\n')  # Добавляем действие в лог

    def start_vfs(self):
        """Открывает VFS-архив (файл .tar), выбранный пользователем."""
        vfs_path = filedialog.askopenfilename(title="Select VFS Archive", filetypes=[("Tar files", "*.tar")])
        if vfs_path:
            # Открываем файл как бинарные данные и загружаем в память
            with open(vfs_path, 'rb') as f:
                self.vfs_data = io.BytesIO(f.read())
            self.current_dir = '/'  # Начальная директория - корень VFS
            self.output_area.insert(tk.END, "Welcome to the Shell Emulator! Current directory: /\n")
            self.log_action("Started VFS: " + vfs_path)

    def process_command(self, event):
        """Обрабатывает команды, введенные пользователем."""
        command = self.input_area.get()  # Получаем команду из ввода
        self.input_area.delete(0, tk.END)  # Очищаем поле ввода
        try:
            # Проверяем, какую команду ввел пользователь и выполняем соответствующие действия
            if command.startswith("ls"):
                output = self.ls()  # Получаем список файлов и директорий
                self.display_output("\n".join(output))
                self.log_action("Executed command: " + command)
            elif command.startswith("cd "):
                _, new_dir = command.split(maxsplit=1)  # Извлекаем имя новой директории
                result = self.cd(new_dir)  # Пытаемся перейти в новую директорию
                self.display_output(result)
                self.log_action("Executed command: " + command)
            elif command == "exit":
                self.exit_emulator()  # Выход из эмулятора
                self.log_action("Exited emulator")
            elif command.startswith("echo "):
                _, message = command.split(maxsplit=1)  # Извлекаем сообщение для вывода
                self.display_output(message)  # Отображаем сообщение
                self.log_action("Executed command: " + command)
            elif command.startswith("cp "):
                _, source, destination = command.split(maxsplit=2)  # Извлекаем исходный файл и место назначения
                self.cp(source, destination)  # Копирование файла
                self.display_output(f"Copied {source} to {destination}")
                self.log_action("Executed command: " + command)
            else:
                self.display_output(f"Command not found: {command}")  # Если команда не распознана
                self.log_action("Command not found: " + command)
        except Exception as e:
            # В случае ошибки, отображаем сообщение об ошибке
            messagebox.showerror("Error", str(e))
            self.log_action("Error: " + str(e))

    def display_output(self, text):
        """Отображает вывод в области вывода (скроллируемое текстовое поле)."""
        self.output_area.insert(tk.END, text + "\n")

    def ls(self):
        """Отображает список файлов и директорий в текущем каталоге внутри архива (VFS)."""
        output = []  # Список для хранения имен файлов и директорий
        with tarfile.open(fileobj=self.vfs_data, mode='r') as tar:
            # Получаем список всех элементов архива
            members = tar.getmembers()
            for member in members:
                # Проверяем, является ли элемент директорией или файлом
                if member.isdir() or member.isfile():
                    output.append(member.name)
        return output  # Возвращаем список имен файлов и директорий

    def cd(self, new_dir):
        """Переходит в указанную директорию внутри архива (VFS)."""
        with tarfile.open(fileobj=self.vfs_data, mode='r') as tar:
            members = tar.getmembers()
            # Получаем все директории в архиве
            dirs = [member.name for member in members if member.isdir()]
            if new_dir in dirs:
                self.current_dir = new_dir  # Меняем текущую директорию
                return f"Changed directory to: {self.current_dir}"
            else:
                return f"{new_dir} not found"  # Если директория не найдена

    def exit_emulator(self):
        """Выход из эмулятора, закрытие окна и завершение работы программы."""
        self.output_area.insert(tk.END, "Exiting emulator.\n")
        self.master.quit()

    def cp(self, source, destination):
        """Копирует файл внутри архива (VFS)."""
        with tarfile.open(fileobj=self.vfs_data, mode='r') as tar:
            members = tar.getmembers()
            source_member = None
            # Ищем исходный файл в архиве
            for member in members:
                if member.name == source:
                    source_member = member
                    break

            if source_member:
                # Открываем временный архив для записи
                new_vfs_data = io.BytesIO()

                # Копируем все элементы из старого архива в новый, включая исходный файл
                with tarfile.open(fileobj=new_vfs_data, mode='w') as new_tar:
                    # Копируем все элементы из старого архива в новый
                    for member in members:
                        if member != source_member:
                            new_tar.addfile(member, tar.extractfile(member))
                    # Добавляем файл в новое место
                    new_tar.addfile(source_member, tar.extractfile(source_member))

                # Теперь обновляем текущие данные VFS на новый архив
                self.vfs_data = new_vfs_data
                self.log_action(f"Copied {source} to {destination}")
            else:
                raise FileNotFoundError(f"Source file {source} not found in VFS.")


if __name__ == "__main__":
    # Создаем главное окно и запускаем приложение
    root = tk.Tk()
    app = ShellEmulatorGUI(root)
    root.mainloop()  # Запускаем цикл обработки событий Tkinter
