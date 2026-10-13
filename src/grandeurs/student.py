"""Coefficient de Student : le facteur d'élargissement d'une série de mesures.

L'incertitude élargie ``U = k·u`` au niveau de confiance de 95 % se calcule
avec ``k = 2`` quand l'incertitude-type est bien connue (loi normale). Pour une
série de ``n`` mesures dont on prend la moyenne et l'écart-type expérimental,
le quantile de la loi de Student à ``n − 1`` degrés de liberté le remplace :
12,7 pour deux mesures, 2,78 pour cinq, 2,26 pour dix, et 1,96 à la limite des
grands nombres. ``g.texte(k=coefficient_student(n))`` l'applique à une
écriture, ``configurer(facteur_elargissement=coefficient_student(n))`` à
toutes, lecture comprise.
"""

from numbers import Integral

__all__ = ["coefficient_student"]


def coefficient_student(n: int, niveau: float = 0.95) -> float:
    """Quantile bilatéral de la loi de Student à ``n − 1`` degrés de liberté.

    ``n`` est le nombre de mesures (au moins 2), ``niveau`` le niveau de
    confiance (0,95 par défaut) ; la loi est celle de ``scipy.stats.t``.

    >>> round(coefficient_student(5), 3)
    2.776
    >>> round(coefficient_student(10, niveau=0.99), 2)
    3.25
    """
    if isinstance(n, bool) or not isinstance(n, Integral) or n < 2:
        raise ValueError(f"il faut au moins deux mesures, n entier ≥ 2 (reçu {n!r})")
    if not 0 < niveau < 1:
        raise ValueError(f"le niveau de confiance est strictement entre 0 et 1 (reçu {niveau!r})")
    from scipy.stats import t  # import tardif : scipy.stats est long à charger

    return float(t.ppf((1 + niveau) / 2, int(n) - 1))
