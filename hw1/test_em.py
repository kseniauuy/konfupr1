import os
import tarfile
import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from main import ShellEmulatorGUI  # Замените на правильный путь к вашему классу

@pytest.fixture
def setup_vfs(tmpdir):
    # Создаем временный tar-файл для тестов
    vfs_path = tmpdir.join("test_vfs.tar")
    with tarfile.open(vfs_path, "w") as tar:
        # Добавляем несколько файлов в архив
        tarinfo = tarfile.TarInfo(name="file1.txt")
        tarinfo.size = 10
        tar.addfile(tarinfo, BytesIO(b"1234567890"))
        tarinfo = tarfile.TarInfo(name="file2.txt")
        tarinfo.size = 10
        tar.addfile(tarinfo, BytesIO(b"abcdefghij"))
    return str(vfs_path)

def test_start_vfs(setup_vfs):
    gui = ShellEmulatorGUI(MagicMock())
    gui.start_vfs()

    # Проверяем, что vfs_data не пустое
    assert gui.vfs_data is not None

def test_ls(setup_vfs):
    gui = ShellEmulatorGUI(MagicMock())
    gui.vfs_data = BytesIO()
    
    with tarfile.open(setup_vfs, "r") as tar:
        gui.vfs_data = BytesIO(tar.read())
    
    output = gui.ls()
    assert "file1.txt" in output
    assert "file2.txt" in output

def test_cd_valid(setup_vfs):
    gui = ShellEmulatorGUI(MagicMock())
    gui.current_dir = "/"
    
    # Поскольку у нас нет реальной структуры каталогов, просто проверяем логику
    result = gui.cd("some_directory")
    assert "not found" in result

def test_cp(setup_vfs):
    gui = ShellEmulatorGUI(MagicMock())
    gui.current_dir = os.path.dirname(setup_vfs)

    # Копируем файл
    gui.cp("file1.txt", "file1_copy.txt")
    
    # Проверяем, что файл был скопирован
    assert os.path.exists(os.path.join(gui.current_dir, "file1_copy.txt"))

def test_exit_emulator():
    gui = ShellEmulatorGUI(MagicMock())
    gui.exit_emulator()  # Проверяем, что метод вызывается без ошибок

if __name__ == "__main__":
    pytest.main()
