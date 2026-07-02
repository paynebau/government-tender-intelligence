import importlib


def test_app_module_imports_without_running_streamlit_page():
    module = importlib.import_module("app")

    assert callable(module.main)
    assert module.TITLE == "政府標案情資查詢系統"
