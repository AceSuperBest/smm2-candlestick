import json
import sys
import os


def get_executable_directory(path: str | None = None):
    if getattr(sys, 'frozen', False):
        # If PyInstaller
        application_path = os.path.dirname(sys.executable)
    else:
        # Python Direct
        entry_script_path = os.path.abspath(sys.argv[0])
        application_path = os.path.dirname(entry_script_path)
    if path:
        return os.path.join(application_path, path)
    return application_path


def get_i18n(iso639: str, file: str) -> dict[str, str]:
    """
    获取国际化文件 (如果不存在则使用英文文件)
    
    :param iso639: 语言代码
    :param file: 文件名
    """
    i18n_path = get_executable_directory('assets/i18n')
    lang_dirpath = os.path.join(i18n_path, iso639)
    lang_json_file = file.lower().removesuffix('.json') + '.json'
    if not os.path.exists(os.path.join(lang_dirpath, lang_json_file)):
        if not os.path.exists(os.path.join(i18n_path, 'en', lang_json_file)):
            raise FileNotFoundError("i18n file not found")
        lang_dirpath = os.path.join(i18n_path, 'en')
    with open(os.path.join(lang_dirpath, lang_json_file), 'r', encoding='utf-8') as f:
        return json.load(f)


def get_assets_path(filename: str) -> str:
    return get_executable_directory(f'assets/{filename.removeprefix("assets/")}')
