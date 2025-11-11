from backend.app.services.search_service import search_modules


def test_search_modules_returns_list():
    assert isinstance(search_modules("odoo"), list)


