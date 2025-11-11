from backend.app.services.embedding_service import generate_module_embedding


def test_generate_module_embedding_returns_list():
    assert isinstance(generate_module_embedding("text"), list)


