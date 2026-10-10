import pytest

from grandeurs import reglages_temporaires


@pytest.fixture
def silence():
    """Accepte une grandeur créée sans unité sans avertir, le temps d'un test."""
    with reglages_temporaires(sans_unite="silence") as r:
        yield r
