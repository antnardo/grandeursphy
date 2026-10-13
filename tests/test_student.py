import numpy as np
import pytest

from grandeurs import coefficient_student, grandeur, reglages_temporaires


@pytest.mark.parametrize(
    ("n", "attendu"),
    [(2, 12.71), (5, 2.776), (10, 2.262), (30, 2.045), (10**6, 1.960)],
)
def test_valeurs_de_table_a_95_pour_cent(n, attendu):
    assert coefficient_student(n) == pytest.approx(attendu, rel=5e-4)


def test_niveau_de_confiance_de_99_pour_cent():
    assert coefficient_student(5, niveau=0.99) == pytest.approx(4.604, abs=5e-4)


def test_entier_numpy_accepte():
    assert coefficient_student(np.int64(5)) == pytest.approx(2.776, abs=5e-4)


@pytest.mark.parametrize("n", [1, 0, -3, 2.5, True, "5"])
def test_nombre_de_mesures_invalide_refuse(n):
    with pytest.raises(ValueError, match="mesures"):
        coefficient_student(n)


@pytest.mark.parametrize("niveau", [0, 1, 1.5, -0.5])
def test_niveau_invalide_refuse(niveau):
    with pytest.raises(ValueError, match="niveau"):
        coefficient_student(5, niveau=niveau)


def test_k_de_student_a_l_appel():
    g = grandeur(1.2, "m", incertitude=0.01)
    assert g.texte(k=coefficient_student(5)) == "(1.20 ± 0.03) m"
    assert g.texte(k=coefficient_student(2)) == "(1.2 ± 0.1) m"
    assert g.texte(k=coefficient_student(5), style="U") == "x = 1.20 m ; U(x) = 0.03 m"
    assert g.texte(k=coefficient_student(5), style="courte") == "1.20(1) m"


def test_k_de_student_en_reglage_ecrit_et_lit():
    k = coefficient_student(5)
    with reglages_temporaires(facteur_elargissement=k):
        assert str(grandeur(1.2, "m", incertitude=0.01)) == "(1.20 ± 0.03) m"
        assert grandeur("1.20 ± 0.03 m").incertitude == pytest.approx(0.03 / k)
        assert grandeur("x = 1.20 m ; U(x) = 0.03 m").incertitude == pytest.approx(0.03 / k)
        assert grandeur("1.20(3) m").incertitude == pytest.approx(0.03)
