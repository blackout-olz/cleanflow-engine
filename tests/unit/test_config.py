import pytest
from app.config import get_settings


def test_settings_load_from_environment(monkeypatch):
    """Deve carregar as configurações corretamente a partir de variáveis de ambiente."""
    monkeypatch.setenv("SPREADSHEET_ID", "sheet_xyz_999")
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", "config/credentials.json")

    settings = get_settings()

    assert settings.SPREADSHEET_ID == "sheet_xyz_999"
    assert settings.GOOGLE_CREDENTIALS_PATH == "config/credentials.json"
    assert settings.APP_NAME == "MaidPad Lead Automation"


def test_settings_missing_required_vars(monkeypatch):
    """Deve falhar se a variável obrigatória SPREADSHEET_ID não for fornecida."""
    monkeypatch.delenv("SPREADSHEET_ID", raising=False)
    
    # Limpa o cache do lru_cache para forçar releitura
    get_settings.cache_clear()

    with pytest.raises(Exception):
        get_settings()