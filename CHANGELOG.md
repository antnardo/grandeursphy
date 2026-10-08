# Journal des modifications

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) ; versions :
[SemVer](https://semver.org/lang/fr/).

## 0.1.0 - 2026-10-08

Première version du paquet `grandeurs`, qui fusionne les anciens paquets `cs`,
`units`, `constantes` et `angles` en une couche au-dessus de pint, uncertainties et
scipy.constants.

### Ajouté

- `grandeur(...)` : grandeur à unité, sous-classe de la quantité pint, lue depuis
  une chaîne (« 1.20 m.s-1 », « 1.20(3) m », « (1.20 ± 0.03)e3 m », « 1,20 m »), un
  nombre, un tableau ou une autre quantité, avec incertitude éventuelle.
- Registre pint unique (`ureg`), qui lit les notations de manuel (`m.s-1`,
  `kg.m.s^(-2)`, `J.mol-1.K-1`, `J/mol.K`…) et les noms `j`, `an`, `tr`, `Torr`.
- `unit(...)` : unités à égalité physique, `unit("N") == unit("kg.m.s^(-2)")`.
- API permissive réglable (`Reglages`, `configurer`, `reglages_temporaires`) : une
  valeur sans unité passe, avec un `SansUniteWarning` ou une `SansUniteError` selon
  le niveau choisi ; un nombre nu ajouté à une grandeur est lu dans l'unité de
  l'autre opérande ou en SI.
- Chiffres significatifs d'après l'écriture et propagation des incertitudes par
  uncertainties, corrélations comprises ; affichage arrondi d'après l'incertitude.
- `.si()` : simplification en SI avec unités dérivées ; `.vers(...)` : conversion
  dans une unité écrite comme dans un manuel.
- `grandeurs.constantes` (grandeurs) et `grandeurs.flottants` (flottants SI) :
  CODATA 2022 par scipy, constantes UAI 2015, Terre, Lune, unités CGS et
  anglo-saxonnes, masse du W, avec leur source (`decrire`, `FICHES`) ;
  `codata(clé)` pour toute constante de scipy.
- Angles : `dms`, `lire_angle`, `ecrire_angle`, `DMS`, `ramener`.
- Sortie siunitx : `qty`, `num`, `unite_siunitx`, `Grandeur.latex`.
- `grandeurs.fonctions` : `sqrt`, `exp`, `ln`, `log10`, fonctions trigonométriques
  qui propagent les incertitudes et vérifient les unités.

### Modifié

- Noms de constantes qui se masquaient : `G_0` est la pesanteur normale (le quantum
  de conductance devient `G_CONDUCTANCE`), `HA` l'énergie de Hartree (l'hectare
  devient `HECTARE`), `GAL` le gal CGS (le gallon américain devient `GAL_US`).
- Les constantes ne sont plus des `decimal.Decimal` : les calculs en flottants
  (`R_GP * T`) fonctionnent de nouveau, par `grandeurs.flottants`.
- Un entier écrit garde ses zéros de droite comme chiffres significatifs
  (« 1200 » en a quatre), comme `ufloat_fromstr`.

### Corrigé

- Pouce, pied, yard, mile (facteur 10), gallon (en m³ et non en litres), zéro
  Celsius (273,15 K), rayon lunaire (1 737,4 km), température de Planck (masse de
  Planck), magnéton nucléaire (masse du proton), G (CODATA 2022), `K_CD`
  (683 lm/W), œrsted (A/m), valeurs astronomiques (UAI 2015).
- Écriture des angles : 30° s'écrit 30°00'00" ; −10°30' vaut −10,5°.
- Arithmétique des incertitudes de l'ancienne classe `CS` (soustraction, division,
  puissance, opérations avec un flottant, opérateurs en place, comparaisons).

### Supprimé

- Le code d'origine (`ancien/`), qui reste dans l'historique git et dans
  `_archives/ancien-2026-10-08/`.
