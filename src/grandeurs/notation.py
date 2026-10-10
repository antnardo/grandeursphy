"""Traduction des notations d'unités « de manuel et de copie » vers la syntaxe de pint.

pint lit ``kg*m/s**2``, ``kg m s^-2`` ou ``kg·m·s⁻²``, mais refuse ``m.s-1``,
l'écriture la plus courante dans les manuels et les copies françaises. Plutôt
que de réécrire un analyseur d'unités complet, on traduit le texte vers la
syntaxe de pint, et c'est pint qui reconnaît les noms d'unités et les préfixes.
La traduction est branchée comme *préprocesseur* du registre : elle s'applique à
toute chaîne que pint analyse, donc aussi à ``Quantity(1, "m.s-1")`` et à
``q.to("km.h-1")``.

Règles :

- produit : ``.``, ``·``, ``*`` ou une simple juxtaposition (``kg m``) ;
- puissance : entier signé collé au nom (``m2``, ``s-1``), ``^n``, ``^(n)``,
  ``**n``, exposants Unicode (``s⁻¹``) ; ``n`` est un entier ou un décimal
  (``m^0.5``, racine d'une unité) ;
- quotient : ``/``. Un produit écrit avec un point ou une juxtaposition après
  une barre reste au dénominateur : ``J/mol.K`` se lit J/(mol·K), comme le lit
  un physicien, alors que ``J/mol*K`` garde la priorité de Python, (J/mol)·K.
  La norme ISO 80000-1 déclare la première écriture ambiguë ; on la lit dans le
  seul sens qui ait un usage (W/m.K pour une conductivité thermique, etc.) ;
- signes Unicode ``−`` (moins), ``µ``/``μ``, ``Ω``/``Ω``, ``Å``/``Å`` ramenés à
  une seule forme.

La traduction ne lève jamais d'exception : un texte qu'elle ne comprend pas est
rendu tel quel, et pint le refuse ou le lit avec sa propre grammaire (sommes,
constantes nommées…).
"""

import re
from functools import lru_cache

__all__ = ["traduire_notation"]

_EQUIVALENTS = str.maketrans(
    {
        "μ": "µ",  # mu grec → signe micro
        "Ω": "Ω",  # signe ohm → oméga
        "Å": "Å",  # signe angström → A rond
        "−": "-",  # signe moins typographique
        "⋅": "·",
    }
)

_EXPOSANTS_UNICODE = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")

_JETONS = re.compile(
    r"""
      (?P<espace>\s+)
    | (?P<nombre>\d+(?:[.,]\d+)?(?:[eE][-+]?\d+)?)
    | (?P<nom>(?:°[^\W\d_⁰¹²³⁴⁵⁶⁷⁸⁹]*|[^\W\d⁰¹²³⁴⁵⁶⁷⁸⁹])(?:_\d+|[^\W\d⁰¹²³⁴⁵⁶⁷⁸⁹])*)
    | (?P<puissance>\*\*|\^)
    | (?P<etoile>\*)
    | (?P<point>[.·])
    | (?P<barre>/)
    | (?P<ouvrante>\()
    | (?P<fermante>\))
    | (?P<exposant_unicode>[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)
    | (?P<entier_signe>[-+]\d+)
    """,
    re.VERBOSE,
)

_ARGUMENT_PUISSANCE = re.compile(
    r"\s*(?:\(\s*(?P<p>[-+]?\d+(?:\.\d+)?)\s*\)|(?P<n>[-+]?\d+(?:\.\d+)?))"
)


class _NotationIllisibleError(ValueError):
    """Texte hors de la grammaire de manuel : on le rend tel quel à pint."""


class _Traducteur:
    """Parcourt le texte jeton par jeton et écrit l'expression équivalente pour pint.

    Une pile suit, pour chaque niveau de parenthèses, si l'on est dans un
    dénominateur ouvert par ``/`` : les produits « faibles » (point,
    juxtaposition) y restent, un produit « fort » (``*``) le referme.
    """

    def __init__(self, texte: str) -> None:
        self._texte = texte
        self._sortie: list[str] = []
        self._denominateurs: list[bool] = [False]
        self._apres_operande = False
        self._fin_nom = -1

    def traduire(self) -> str:
        position = 0
        while position < len(self._texte):
            jeton = _JETONS.match(self._texte, position)
            if jeton is None:
                raise _NotationIllisibleError(self._texte)
            position = self._traiter(
                jeton.lastgroup or "", jeton.group(), jeton.start(), jeton.end()
            )
        self._fermer_denominateur()
        if len(self._denominateurs) != 1:
            raise _NotationIllisibleError(self._texte)
        return "".join(self._sortie)

    def _traiter(self, genre: str, valeur: str, debut: int, fin: int) -> int:
        colle_au_nom = debut == self._fin_nom
        if genre == "espace":
            return fin
        if genre == "nombre" and colle_au_nom and valeur.isdigit():
            self._exposant(valeur)  # m2, s3 : entier collé à un nom
        elif genre == "entier_signe":
            if not colle_au_nom:  # s-1 : exposant ; ailleurs, une soustraction
                raise _NotationIllisibleError(self._texte)
            self._exposant(valeur)
        elif genre == "nom":
            self._operande(valeur)
            self._fin_nom = fin
        elif genre == "nombre":
            self._operande(valeur.replace(",", "."))
        elif genre == "ouvrante":
            self._produit_implicite()
            self._sortie.append("(")
            self._denominateurs.append(False)
            self._apres_operande = False
        elif genre == "fermante":
            self._fermer_denominateur()
            if len(self._denominateurs) == 1:
                raise _NotationIllisibleError(self._texte)
            self._denominateurs.pop()
            self._sortie.append(")")
            self._apres_operande = True
        elif genre == "puissance":
            return self._puissance(fin)
        elif genre == "exposant_unicode":
            self._exposant(valeur.translate(_EXPOSANTS_UNICODE))
        elif genre == "etoile":
            self._fermer_denominateur()
            self._sortie.append("*")
            self._apres_operande = False
        elif genre == "point":
            self._sortie.append("*")
            self._apres_operande = False
        elif genre == "barre":
            self._fermer_denominateur()
            self._sortie.append("/(")
            self._denominateurs[-1] = True
            self._apres_operande = False
        return fin

    def _operande(self, valeur: str) -> None:
        self._produit_implicite()
        self._sortie.append(valeur)
        self._apres_operande = True

    def _produit_implicite(self) -> None:
        if self._apres_operande:
            self._sortie.append("*")

    def _fermer_denominateur(self) -> None:
        if self._denominateurs[-1]:
            self._sortie.append(")")
            self._denominateurs[-1] = False

    def _puissance(self, fin: int) -> int:
        argument = _ARGUMENT_PUISSANCE.match(self._texte, fin)
        if argument is None:
            raise _NotationIllisibleError(self._texte)
        self._exposant(argument.group("p") or argument.group("n"))
        return argument.end()

    def _exposant(self, brut: str) -> None:
        if not self._apres_operande:
            raise _NotationIllisibleError(self._texte)
        valeur = float(brut)
        texte = str(int(valeur)) if valeur.is_integer() else repr(valeur)
        self._sortie.append(f"**({texte})")


@lru_cache(maxsize=1024)
def traduire_notation(texte: str) -> str:
    """Traduit une notation de manuel en expression lisible par pint.

    >>> traduire_notation("kg.m.s^(-2)")
    'kg*m*s**(-2)'
    >>> traduire_notation("J/mol.K")
    'J/(mol*K)'

    Un texte hors de la grammaire est rendu inchangé.
    """
    normal = texte.translate(_EQUIVALENTS)
    try:
        return _Traducteur(normal).traduire()
    except (_NotationIllisibleError, ValueError):
        return texte
