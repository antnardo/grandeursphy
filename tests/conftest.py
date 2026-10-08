import pytest

from grandeurs import reglages_temporaires


@pytest.fixture
def silence():
    """Accepte les nombres nus sans avertir, le temps d'un test."""
    with reglages_temporaires(sans_unite="silence", melange="silence") as r:
        yield r
