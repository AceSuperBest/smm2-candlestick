import ctypes
from ctypes import wintypes

class OPENFILENAME(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HINSTANCE),
        ("lpstrFilter", wintypes.LPCWSTR),
        ("lpstrCustomFilter", wintypes.LPWSTR),
        ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD),
        ("lpstrFile", wintypes.LPWSTR),
        ("nMaxFile", wintypes.DWORD),
        ("lpstrFileTitle", wintypes.LPWSTR),
        ("nMaxFileTitle", wintypes.DWORD),
        ("lpstrInitialDir", wintypes.LPCWSTR),
        ("lpstrTitle", wintypes.LPCWSTR),
        ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD),
        ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", wintypes.LPCWSTR),
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", wintypes.LPVOID),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("pvReserved", wintypes.LPVOID),
        ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD),
    ]

OFN_FILEMUSTEXIST = 0x00001000
OFN_PATHMUSTEXIST = 0x00000800


def create_selector(title: str, filters: list[tuple[str, str]], selected_filter: int = 1) -> str | None:
    """
    创建文件选择对话框
    """
    # 定义缓冲区大小
    buffer_size = wintypes.MAX_PATH

    # 创建文件名缓冲区
    file_buffer = ctypes.create_unicode_buffer(buffer_size)

    # 初始化 OPENFILENAME 结构体
    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    ofn.lpstrFile = ctypes.addressof(file_buffer)
    ofn.nMaxFile = buffer_size
    ofn.lpstrFilter = '\0'.join([f"{name}\0{ext}" for name, ext in filters]) + '\0'
    ofn.nFilterIndex = selected_filter
    ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST
    ofn.lpstrTitle = title

    # 返回文件路径
    if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        filepath = str(file_buffer.value)
        return filepath
    return None


def message_box(message: str, title: str = "提示", style: int = 0):
    """
    创建消息框
    """
    ctypes.windll.user32.MessageBoxW(0, message, title, style)
