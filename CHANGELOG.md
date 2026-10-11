# Journal des modifications

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) ; versions :
[SemVer](https://semver.org/lang/fr/).

## Non publié

Décision du 11 octobre 2026 : une écriture « x ± a » signifie désormais
l'incertitude élargie a = k·u, avec k = 2 par défaut. Le paquet calcule toujours
avec l'incertitude-type u (`std_dev`) ; seul ce qui s'écrit ou se lit derrière un
« ± » change.

### Ajouté

- Réglage `facteur_elargissement` (2 par défaut, nombre fini > 0) : le facteur k
  de l'incertitude élargie.
- `arrondir(..., facteur=k)`, `arrondir_valeur(..., elargie=True)` et
  `Grandeur.arrondi(elargie=True)` arrondissent sur l'incertitude élargie ;
  `NombreArrondi` porte un champ `facteur` (`None` pour l'incertitude-type).

### Modifié (incompatible)

- Écriture « ± » (`str`, `texte(style="pm")`) : l'incertitude écrite est k·u,
  arrondie sur k·u, et la valeur à son rang : `grandeur("1.20 m")` s'écrit
  `(1.20 ± 0.02) m` (u = 0,01) au lieu de `(1.20 ± 0.01) m`. Le rang peut changer
  par rapport à l'écriture courte : u = 0,06 donne `1.23(6)` mais `1.2 ± 0.1`.
- Lecture « ± » (`grandeur`, `lire_nombre`, `lire_qty`) : « 1.20 ± 0.03 »,
  « 1.20+/-0.03 », « (1.20 ± 0.03)e3 », « 1.20e3 ± 30 » donnent u = a/k (0,015,
  15), pour que l'écriture se relise.
- `NombreArrondi.ecrire` choisit par défaut (`incertitude="auto"`) la forme qui
  convient à l'arrondi, et refuse d'écrire entre parenthèses une incertitude
  élargie, ou derrière « ± » une incertitude-type (`ValueError`).

### Inchangé

- La notation courte « 1.20(1) » et toute la sortie siunitx (`qty`, `num`, qui
  n'écrivent que la forme courte) restent en u ; « 1.20(3) » et `\qty{1.20(3)}{m}`
  se lisent toujours u = 0,03. Les chiffres significatifs (« 1.20 » → u = 0,01),
  l'argument `incertitude=` de `grandeur` et les constantes (u de CODATA, créées
  par `ufloat` et non lues dans un texte) ne changent pas ; seul leur affichage
  « ± » montre 2u.

## 0.2.0 - 2026-10-10

Simplification : l'API permissive et
l'algèbre des unités disparaissent, l'écriture gagne un réglage `chiffres`, `.si()`
une table d'unités préférées, les constantes une organisation en sous-modules.

### Ajouté

- Les symétriques qui manquaient : `lire_qty` relit ce que `qty` écrit
  (`\qty{1.20(1)}{m.s^{-1}}`, `\SI`, `\num`) ; `derouler` déroule une suite
  d'angles, l'inverse de `ramener` ; `cles_codata` liste les clés de `codata` ;
  `equivalentes(a, b)` est l'égalité physique derrière `unit(a) == unit(b)`. Des
  tests d'aller-retour couvrent `grandeur(str(g))`, `lire_qty(qty(g))` et
  `derouler(ramener(…))`.
- Réglage `chiffres` (3 par défaut) : chiffres significatifs d'une valeur exacte
  à l'écriture, appliqué par `str`, `texte`, `qty` et `num` ; une valeur incertaine
  reste arrondie d'après son incertitude. `grandeurs.chiffres.arrondir_valeur` est
  le point d'arrondi commun.

### Modifié

- La suite de tests exécute les doctests des modules (`--doctest-modules`) ; le
  doctest de `codata` était faux. Un test d'intégration (`tests/test_pythontex.py`,
  marqué `latex`) compile un document pythontex minimal, sauté sans `lualatex` ou
  `pythontex`.
- Le sdist ne contient plus `uv.lock` ni `tests/` ; la version vit dans
  `grandeurs.__version__`. Intégration continue (`.github/workflows/ci.yml` :
  pytest sous 3.11 et 3.14, ruff, mypy, `uv build`) et publication des artefacts
  sur la release GitHub (`publish.yml`), sans PyPI.
- `grandeurs.constantes` devient un paquet : le module principal garde les
  constantes fondamentales et les unités en usage avec le SI ; `constantes.astro`,
  `constantes.cgs` et `constantes.us` reçoivent l'astronomie, le CGS et les unités
  anglo-saxonnes. `grandeurs.flottants` a la même structure, générée depuis les
  grandeurs (un test vérifie que les listes de noms coïncident). Les huit noms des
  corrigés (`R_GP`, `NA`, `E`, `M_E`, `EPS_0`, `HBAR`, `H`, `C`) sont inchangés.
- Cinq constantes renommées sans alias : `HA` → `HARTREE`, `G_0` → `G_N`,
  `KN` → `NOEUD`, `NM` → `MILLE_MARIN`, `GAL` → `cgs.GAL_CGS` (aucun document ne
  les employait).
- `cles_codata(motif)` liste les clés que `codata(clé)` accepte.
- `.si()` consulte une table d'unités préférées (N/m, S/m, C/kg, lm, lx, Bq, V/m,
  A/m, H/m, F/m, Pa·s, W/(m·K), J/(kg·K), J/(mol·K)…) avant le coût minimal, qui
  écrivait T·A pour une raideur, Ω⁻¹·m⁻¹ pour une conductivité, T⁻¹·s⁻¹ pour un
  C/kg, cd·rad² pour un lumen et count·s⁻¹ pour un becquerel. Hz, Gy et Sv ne sont
  jamais choisis.
- Un tableau s'écrit élément par élément, arrondi comme un scalaire :
  `[1.00; 2.00] m`, `[1.0 ± 0.1; 2.00 ± 0.02] m`.

### Supprimé

- Notation : les exposants entre accolades (`m^{-1}`) et fractionnaires (`m^(1/2)`),
  et les produits `×` et `•`, que rien n'employait.
- `Unite` réduite à l'égalité physique (`==`, `equivalentes(a, b)`) et à l'écriture
  (`ecrire`) : `identique`, `dimension`, `affine`, `facteur_si`, `decalage_si`,
  `si()`, `latex()` et l'algèbre des unités (`3 * unit("m")`) disparaissent ; on
  passe par les grandeurs.
- L'API permissive : les réglages `melange` et `lecture_nombre`, et la lecture
  d'un nombre nu dans l'unité de l'autre opérande (`12 cm + 3`). Les règles de
  pint s'appliquent : `longueur + 2` est refusé. Seul `sans_unite` reste, pour
  une grandeur créée sans unité. L'avertissement désigne la ligne qui a appelé
  `grandeur(...)`, sans parcours de la pile.

## 0.1.0 - 2026-10-08

Première version du paquet `grandeurs` : une couche au-dessus de pint, uncertainties
et scipy.constants.

### Ajouté

- Licence MIT.
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
- Arithmétique des incertitudes (soustraction, division, puissance, opérations avec
  un flottant, opérateurs en place, comparaisons).

