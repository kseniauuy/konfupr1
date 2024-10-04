import os
import tarfile
import io
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog

class ShellEmulatorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Shell Emulator")
        self.vfs_data = None
        self.current_dir = None
        self.log_file_path = os.path.join(os.getcwd(), 'log.txt')  # Путь к log.txt в текущей директории

        self.output_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=20)
        self.output_area.pack(padx=10, pady=10)
        
        self.input_area = tk.Entry(master, width=50)
        self.input_area.pack(padx=10, pady=10)
        self.input_area.bind("<Return>", self.process_command)
        
        self.start_button = tk.Button(master, text="Start VFS", command=self.start_vfs)
        self.start_button.pack(pady=5)

        self.display_output(f"Log file created at: {self.log_file_path}")

    def log_action(self, action):
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(action + '\n')

    def start_vfs(self):
        vfs_path = filedialog.askopenfilename(title="Select VFS Archive", filetypes=[("Tar files", "*.tar")])
        if vfs_path:
            with open(vfs_path, 'rb') as f:
                self.vfs_data = io.BytesIO(f.read())
            self.current_dir = '/'
            self.output_area.insert(tk.END, "Welcome to the Shell Emulator! Current directory: /\n")
            self.log_action("Started VFS: " + vfs_path)

    def process_command(self, event):
        command = self.input_area.get()
        self.input_area.delete(0, tk.END)
        try:
            if command.startswith("ls"):
                output = self.ls()
                self.display_output("\n".join(output))
                self.log_action("Executed command: " + command)
            elif command.startswith("cd "):
                _, new_dir = command.split(maxsplit=1)
                result = self.cd(new_dir)
                self.display_output(result)
                self.log_action("Executed command: " + command)
            elif command == "exit":
                self.exit_emulator()
                self.log_action("Exited emulator")
            elif command.startswith("echo "):
                _, message = command.split(maxsplit=1)
                self.display_output(message)
                self.log_action("Executed command: " + command)
            elif command.startswith("cp "):
                _, source, destination = command.split(maxsplit=2)
                self.cp(source, destination)
                self.display_output(f"Copied {source} to {destination}")
                self.log_action("Executed command: " + command)
            else:
                self.display_output(f"Command not found: {command}")
                self.log_action("Command not found: " + command)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log_action("Error: " + str(e))

    def display_output(self, text):
        self.output_area.insert(tk.END, text + "\n")

    def ls(self):
        with tarfile.open(fileobj=self.vfs_data, mode='r') as tar:
            return [member.name for member in tar.getmembers() if member.isdir() or member.isfile()]

    def cd(self, new_dir):
        new_path = os.path.join(self.current_dir, new_dir)
        if os.path.isdir(new_path):
            self.current_dir = new_path
            return f"Changed directory to: {self.current_dir}"
        else:
            return f"{new_dir} not found"

    def exit_emulator(self):
        self.output_area.insert(tk.END, "Exiting emulator.\n")
        self.master.quit()

    def cp(self, source, destination):
        source_path = os.path.join(self.current_dir, source)
        destination_path = os.path.join(self.current_dir, destination)

        # Проверяем, существует ли источник
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"{source} not found.")
        
        # Копируем файл
        with open(source_path, 'rb') as src_file:
            with open(destination_path, 'wb') as dest_file:
                dest_file.write(src_file.read())

if __name__ == "__main__":
    root = tk.Tk()
    app = ShellEmulatorGUI(root)
    root.mainloop()

