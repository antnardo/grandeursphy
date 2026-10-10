# grandeursphy

[![CI](https://github.com/antnardo/grandeursphy/actions/workflows/ci.yml/badge.svg)](https://github.com/antnardo/grandeursphy/actions/workflows/ci.yml)
[![Licence MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

Grandeurs physiques pour la classe et les corrigés : une valeur, son incertitude et
son unité, lues comme dans un manuel (`1.20 m.s-1`, `J.mol-1.K-1`), écrites avec
les bons chiffres significatifs, simplifiées en SI et sorties pour siunitx depuis
pythontex ; plus les constantes (CODATA 2022, UAI, CGS) avec leur source, en
grandeurs ou en flottants. Le paquet s'appelle `grandeurs` ; c'est une couche au-dessus
de [pint](https://github.com/hgrecco/pint) (unités),
[uncertainties](https://github.com/lmfit/uncertainties) (propagation des
incertitudes) et `scipy.constants` (CODATA 2022).

```python
from grandeurs import grandeur, qty, unit
from grandeurs import constantes as cst

v = grandeur("1.20 m.s-1")             # « 1.20 » : trois chiffres significatifs
d = v * grandeur("2.0 s")
print(d)                               # (2.4 ± 0.1) m
print(v.vers("km/h"))                  # (4.32 ± 0.04) km·h⁻¹
F = grandeur("2.0 kg") * grandeur("9.81 m.s-2")
print(F.si())                          # (20 ± 1) N
print((cst.R_GP * grandeur(20, "°C")).si())   # 2.44e3 J·mol⁻¹
qty(d)                                 # '\qty{2.4(1)}{m}'
unit("N") == unit("kg.m.s^(-2)")       # True
```

Le paquet s'installe depuis GitHub (ci-dessous). PyPI : à venir.

## Sommaire

- [Ce qu'il fait](#ce-quil-fait)
- [Installation](#installation)
- [Prérequis](#prérequis)
- [Prise en main](#prise-en-main)
- [Pièges](#pièges)
- [Les modules](#les-modules)
- [Choix de conception](#choix-de-conception)
- [Tester](#tester)
- [Antériorité](#antériorité)
- [Licence](#licence)

## Ce qu'il fait

- **La notation des manuels.** pint refuse `m.s-1` ; ici `grandeur("1.20 m.s-1")`,
  `v.vers("km.h-1")` et `J/mol.K` (lu J/(mol·K), le seul sens qu'on lui donne en
  physique) passent, parce qu'un préprocesseur traduit la notation avant que pint
  ne lise.
- **Les chiffres significatifs d'après l'écriture.** Une chaîne porte sa précision :
  « 1.20 » a trois chiffres significatifs, donc une incertitude-type de 0,01 ;
  uncertainties la propage, corrélations comprises, et l'affichage arrondit la
  valeur au rang de l'incertitude : `(2.4 ± 0.1) m`. Une valeur exacte s'écrit à
  `chiffres` chiffres significatifs (3 par défaut, réglable) : fini les
  `9.79828445167129`.
- **La simplification en SI** avec les unités dérivées, par une table de ce qu'un
  physicien attend (N, J, W, V, Ω, N/m, S/m, V/m, J/(mol·K)…) puis par l'écriture
  la plus courte, là où `to_preferred` de pint écrit « Hz·W/N » pour une accélération.
- **La sortie siunitx pour pythontex** : `qty(v)` donne `\qty{1.20(1)}{m.s^{-1}}`,
  avec l'unité littérale des documents existants (`\micro m`, `k\ohm`,
  `\degreeCelsius`), la virgule française en option, `\qtylist` pour un tableau ;
  `lire_qty` fait le chemin inverse.
- **Les constantes avec leur source** : CODATA 2022 par scipy (exactes ou avec leur
  incertitude), constantes astronomiques de l'UAI, Terre, Lune, unités CGS et
  anglo-saxonnes, chacune décrite par `decrire("G")` ; en grandeurs
  (`grandeurs.constantes`) ou en flottants SI (`grandeurs.flottants`).
- **Les angles sexagésimaux** avec la retenue faite avant le découpage (30° s'écrit
  30°00'00", pas 29°59'60"), la réduction modulo un tour et le déroulement d'une
  phase.
- **L'égalité physique des unités** : `unit("N") == unit("kg.m.s^(-2)")`, `°C ≠ K`
  mais un écart de 1 °C vaut 1 K.

## Installation

Trois façons, selon le poste.

**Avec pip depuis GitHub**, quand le réseau et pip sont disponibles :

```bash
pip install git+https://github.com/antnardo/grandeursphy
```

**Avec la roue d'une release**, pour un poste qui a pip mais pas git : chaque
[release](https://github.com/antnardo/grandeursphy/releases) porte
`grandeursphy-<version>-py3-none-any.whl` (et le sdist `.tar.gz`), qui s'installe
par `pip install grandeursphy-0.2.0-py3-none-any.whl`.

**Pour développer**, un clone et [uv](https://docs.astral.sh/uv/) :

```bash
git clone https://github.com/antnardo/grandeursphy
cd grandeursphy && uv sync && uv run pytest
```

Pour pythontex, le paquet doit être installé dans l'interpréteur que `pythontex`
appelle (le `python` du `PATH`, ou celui de `--interpreter`) : c'est souvent un
autre que celui du terminal.

## Prérequis

Python 3.11 ou plus récent, avec pint (0.25 ou plus ; pint 0.26 exige Python 3.12,
sous 3.11 c'est pint 0.25 qui s'installe et le paquet fonctionne avec les deux),
uncertainties (3.2 ou plus), numpy et scipy (1.15 ou plus, première version qui
fournit CODATA 2022 ; avec scipy 1.14, `grandeurs.constantes` refuse de se charger
plutôt que de donner d'autres valeurs). Le paquet est testé sous Python 3.11 et
3.14. La sortie LaTeX demande siunitx 3 (`\qty`) ; `macro="SI"` écrit `\SI` pour
siunitx 2.

## Prise en main

Deux règles valent partout. **Une chaîne est une mesure, un nombre est exact** :
`grandeur("50 Hz")` vaut (50 ± 1) Hz, `grandeur(50, "Hz")` vaut 50,0 Hz tout rond.
**Un `float` pour un scalaire, un tableau numpy pour un tableau** : `g.valeur` et
`g.incertitude` sont des `float` (des tableaux pour un tableau), `g.unite` une
`Unite`.

```python
import numpy as np
from grandeurs import grandeur, qty, num, unit, configurer, reglages_temporaires
from grandeurs import constantes as cst
from grandeurs.fonctions import sqrt, sin

# Créer
g = grandeur("1.20 m.s-1")            # incertitude d'après l'écriture : 0,01
g = grandeur(1.2, "m/s")              # exacte
g = grandeur(1.2, "m", incertitude=0.05)
g = grandeur(1.2, "m", incertitude="5 cm")
g = grandeur([1.0, 2.0], "m", incertitude=[0.1, 0.02])
g = grandeur("1.20 km", "m")          # lue puis convertie
g.valeur, g.incertitude, g.unite, g.chiffres, g.valeur_si

# Calculer : pint convertit, uncertainties propage, les fonctions usuelles aussi
h = grandeur(20, "cm")
v = sqrt(2 * cst.G_N * h).si()         # 1.98 m·s⁻¹
s = sin(grandeur("30.0 °"))           # 0.500 ± 0.002
print(grandeur("1.20 m") + grandeur("3.0 cm"))   # (1.23 ± 0.01) m

# Écrire
print(grandeur(36, "km/h").vers("m.s-1"))        # 10.0 m·s⁻¹
print(grandeur(9.79828445167129, "m/s2"))        # 9.80 m·s⁻²  (chiffres = 3)
print(grandeur(2, "m").texte(chiffres=1))        # 2 m
print(grandeur("1.20 m").texte(style="courte", decimale=","))   # 1,20(1) m
configurer(decimale=",", chiffres=4)             # pour tout le processus
with reglages_temporaires(chiffres=5):           # le temps d'un bloc
    print(grandeur(9.79828445167129, "m/s2"))    # 9,7983 m·s⁻²

# Pour pythontex
qty(cst.EPS_0)                        # '\qty{8.854187819(1)e-12}{F.m^{-1}}'
qty(grandeur("1.20 m.s-1"), "km/h")   # '\qty{4.32(4)}{km.h^{-1}}'
qty(grandeur(20, "°C"), chiffres=2)   # '\qty{20}{\degreeCelsius}'
num(cst.ALPHA)                        # '\num{0.007297352564(1)}'
qty(grandeur(np.array([1.0, 2.5]), "m"))   # '\qtylist{1.00;2.50}{m}'
```

Dans un document pythontex :

```latex
\begin{pycode}
from grandeurs import grandeur, qty, num
from grandeurs import constantes as cst
v = grandeur("1.20 m.s-1")
\end{pycode}
$v = \py{qty(v)}$, $\varepsilon_0 = \py{qty(cst.EPS_0)}$, $\alpha = \py{num(cst.ALPHA)}$
```

## Pièges

**Une chaîne est une valeur incertaine.** `grandeur("50 Hz")` vaut (50 ± 1) Hz,
parce que « 50 » a deux chiffres significatifs ; une donnée d'énoncé qu'on veut
exacte se passe en nombre, `grandeur(50, "Hz")`, ou avec le réglage
`chiffres_significatifs=False`. L'affichage le montre : `(50 ± 1) Hz` contre
`50.0 Hz`.

**Une valeur exacte s'écrit à `chiffres` chiffres significatifs, trois par
défaut** : `grandeur(2, "m")` s'affiche `2.00 m` et `qty(grandeur(20, "°C"))` donne
`\qty{20.0}{\degreeCelsius}`. Pour une donnée qui n'en a qu'un ou deux,
`texte(chiffres=1)`, `qty(T, chiffres=2)`, ou le réglage `chiffres`. Une valeur
incertaine ignore ce réglage : son incertitude fixe ses chiffres.

**`.si()` après une racine.** `sqrt(2 * g * h)` avec h en centimètres donne
`19.8 m^0.5·cm^0.5·s⁻¹` : pint ne mélange pas deux unités de même dimension sous
une puissance. Un `.si()` (ou un `.vers("m/s")`) après la racine règle tout :
`1.98 m·s⁻¹`.

**`np.sqrt` échoue sur une grandeur incertaine** (« loop of ufunc does not support
argument 0 of type Variable ») : numpy cherche une méthode `sqrt` que le `ufloat`
d'uncertainties n'a pas. `grandeurs.fonctions` fournit `sqrt`, `exp`, `ln`,
`log10`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, qui acceptent nombres,
`ufloat`, tableaux et grandeurs, propagent les incertitudes et vérifient les unités
(un sinus prend un angle, une exponentielle un nombre sans dimension).

**Les règles de pint restent entières.** `longueur + 2` est refusé
(`DimensionalityError`), 1 m n'est pas le nombre 1, deux dimensions incompatibles
ne s'additionnent pas. Seule une grandeur créée sans unité, `grandeur(3)`, passe,
sans dimension, avec un `SansUniteWarning` (réglage `sans_unite`) ; pour une
grandeur réellement sans dimension, on l'écrit : `grandeur(0.5, "")`.

**Le hertz n'est jamais choisi par `.si()`** : une dimension temps⁻¹ est une
fréquence ou une vitesse angulaire, et seul l'utilisateur sait laquelle ; `3 kHz`
devient `3.00e3 s⁻¹`, `2π rad × 50 Hz` devient `314 rad·s⁻¹`. De même J/kg reste
m²·s⁻² (ni Gy ni Sv) et N·m devient J. On convertit explicitement : `.vers("Hz")`,
`.vers("Gy")`.

**`.vers("j")` écrit `d`** : le jour est `day` pour pint, et `j`, `an`, `tr`,
`Torr` ne sont que des alias de lecture. On n'ajoute pas `ua` ni `al`, que pint
lit déjà comme micro-année et attolitre : on écrit `au` et `ly`.

## Les modules

| Module | Rôle |
| --- | --- |
| `grandeurs` | `grandeur`, `unit`, `qty`, `num`, `lire_qty`, les angles, les réglages : tout ce qu'un corrigé importe |
| `grandeurs.constantes` | constantes fondamentales et unités en usage avec le SI, en grandeurs ; `codata`, `cles_codata`, `decrire`, `FICHES` |
| `grandeurs.constantes.astro`, `.cgs`, `.us` | astronomie (UAI, Terre, Lune), unités CGS, unités anglo-saxonnes |
| `grandeurs.flottants` (et `.astro`, `.cgs`, `.us`) | les mêmes noms en `float` SI, pour les calculs sans unités |
| `grandeurs.fonctions` | `sqrt`, `exp`, `ln`, `log10`, trigonométrie, avec incertitudes et unités |
| `grandeurs.chiffres` | `lire_nombre`, `arrondir`, `arrondir_valeur`, `NombreArrondi` : chiffres significatifs et arrondi décimal |
| `grandeurs.angles` | `dms`, `DMS`, `lire_angle`, `ecrire_angle`, `ramener`, `derouler` |
| `grandeurs.reglages` | `Reglages`, `configurer`, `reglages_temporaires` |
| `grandeurs.registre` | le registre pint unique, `ureg` |

Chaque fonction qui lit a son inverse qui écrit : `grandeur(str(g))`,
`lire_qty(qty(g))`, `lire_angle(ecrire_angle(a))`, `derouler(ramener(…))`,
`codata(clé)` et `cles_codata()`, `.si()` et `.vers(unité)`, `constantes` et
`flottants` ; les tests vérifient ces allers-retours.

## Choix de conception

### Une grandeur est une quantité pint

`grandeur(...)` rend une `Grandeur`, sous-classe de la `Quantity` de pint, déclarée
comme classe des quantités d'un registre pint unique (`grandeurs.ureg`, aussi
registre d'application de pint). Une grandeur est donc une quantité pint à part
entière : conversions, numpy, unités affines et compatibilité avec les bibliothèques
qui connaissent pint viennent sans code. Une classe qui envelopperait une quantité
aurait dû réexposer tout cela, opérateur par opérateur. La valeur d'une grandeur
peut être un nombre, un tableau, un `ufloat` ou un tableau de `ufloat` : pint les
transporte, uncertainties propage. Ce que la sous-classe ajoute : `valeur`,
`incertitude`, `incertitude_relative`, `valeur_si`, `unite`, `chiffres`, `vers`,
`si`, `texte`, `latex`, `arrondi`, et les opérations qu'uncertainties déprécie sur
ses nombres (les comparaisons d'ordre portent sur les valeurs centrales, `abs`
change le signe des valeurs centrales négatives, `round` refuse une grandeur
incertaine).

### Notations de manuel

La traduction des notations est branchée comme préprocesseur du registre : elle
s'applique à toute chaîne que pint lit, donc aussi à `q.to("km.h-1")`. Sont lus le
produit par `.`, `·`, `*` ou une espace ; les puissances `^n`, `^(n)`, `**n`, `s⁻¹`
et l'entier collé au nom (`m2`, `s-1`) ; les variantes Unicode (µ/μ, Ω/Ω).
Une juxtaposition ou un point après une barre reste au dénominateur : `J/mol.K` se
lit J/(mol·K), le seul sens qu'on lui donne en physique, alors que `J/mol*K` garde
la priorité de Python. Quelques noms français sont ajoutés : `j` (jour), `an`, `tr`
(`tr/min`), `Torr`.

### Égalité physique des unités

`unit(...)` rend une `Unite`, qui enveloppe l'unité pint et ne sert qu'à deux
choses : l'égalité physique et l'écriture (`ecrire("texte")`, `"ascii"`,
`"siunitx"`). Deux unités sont égales (`equivalentes(a, b)`) quand elles ont la même
dimension et que la conversion de l'une vers l'autre est l'identité (0 donne 0, 1
donne 1) ; la règle couvre les unités affines : °C ≠ K, mais un écart de 1 °C vaut
1 K. On n'a pas changé l'égalité de la classe `Unit` de pint : pint s'en sert pour
ses caches d'écriture, où « N » et « kg·m·s⁻² » doivent rester distincts. Tout le
reste (dimension, conversion, algèbre) passe par les grandeurs.

Cas limites, qui viennent de la définition du SI :

| Égalité | Résultat | Raison |
| --- | --- | --- |
| `unit("Hz") == unit("Bq")` | `True` | même dimension, facteur 1 |
| `unit("Hz") == unit("rad/s")` | `True` | le radian est sans dimension |
| `unit("J") == unit("N.m")` | `True` | un moment a la dimension d'une énergie |
| `unit("rad") == unit("")` | `True` | rad = 1 (de même sr) |
| `unit("°") == unit("")` | `False` | facteur π/180 |
| `unit("°C") == unit("K")` | `False` | 0 °C ≠ 0 K |
| `unit("delta_degC") == unit("K")` | `True` | un écart de 1 °C vaut 1 K |

### Réglages

Les réglages sont un objet figé (`Reglages`) qu'on change par
`configurer(**champs)` ou, le temps d'un bloc, par
`with reglages_temporaires(**champs):`.

| Réglage | Défaut | Rôle |
| --- | --- | --- |
| `chiffres` | `3` | chiffres significatifs d'une valeur exacte à l'écriture (`str`, `texte`, `qty`, `num`) |
| `chiffres_significatifs` | `True` | « 1.20 » porte une incertitude de 0,01 ; sinon il est exact |
| `chiffres_incertitude` | `1` | chiffres significatifs gardés sur l'incertitude à l'affichage |
| `afficher_incertitude` | `True` | sinon, valeur seule, arrondie à ses chiffres significatifs |
| `style_incertitude` | `"pm"` | à l'écran : `(1.20 ± 0.01) m` ou `"courte"` : `1.20(1) m` |
| `decimale` | `"."` | `","` pour la virgule française |
| `notation` | `"auto"` | `"fixe"`, `"scientifique"`, `"ingenieur"` |
| `sans_unite` | `"avertissement"` | grandeur créée sans unité : `"silence"`, `"avertissement"` ou `"erreur"` |

L'avertissement est un `SansUniteWarning`, que le module `warnings` filtre comme
tout avertissement ; l'erreur est une `SansUniteError`.

### Incertitudes et chiffres significatifs

Une chaîne porte sa précision, selon la convention de `ufloat_fromstr`, qui est
aussi celle de l'enseignement : l'incertitude-type vaut une unité du dernier chiffre
écrit, et les zéros de droite comptent (« 1200 » a quatre chiffres significatifs,
« 1.2e3 » deux). Sont lus « 1.20(3) », « 1.20 ± 0.03 », « (1.20 ± 0.03)e3 »,
« 1,20 », « 1.20×10^3 » et « 1.20×10⁻³ ». Un nombre Python est exact.

La propagation est celle d'uncertainties, au premier ordre, corrélations comprises :
`a - a` vaut exactement 0. À l'affichage, l'incertitude est arrondie à
`chiffres_incertitude` chiffres et la valeur au même rang : c'est l'incertitude qui
fixe les chiffres significatifs. Une valeur exacte est arrondie au réglage
`chiffres`. L'arrondi se fait en décimal, au plus proche, demi vers le haut (2,675
donne 2,68, là où `round(2.675, 2)` donne 2,67). Un tableau s'écrit élément par
élément avec la même règle : `[1.0 ± 0.1; 2.00 ± 0.02] m`. L'égalité `==` de deux
mesures indépendantes de même valeur est fausse : pour uncertainties, deux variables
aléatoires ne sont égales que si leur différence est exactement nulle.

### Simplification en SI

`to_preferred` de pint, essayé avec les unités dérivées, écrit une accélération
« Hz·W/N ». `.si()` suit une règle plus étroite et prévisible : passer en unités de
base ; si cette écriture est celle d'une unité de la table des préférées (N, Pa, J,
W, C, V, F, Ω, S, Wb, T, H, lm, lx, Bq, N/m, C/kg, S/m, Ω·m, V/m, A/m, H/m, F/m,
Pa·s, W/(m·K), J/(kg·K), J/(mol·K), J/K, J/mol, W/m²), l'écrire ainsi ; sinon, si
la dimension ne contient ni masse ni courant, s'arrêter (m·s⁻², m²·s⁻¹, mol·m⁻³) ;
sinon essayer chaque unité dérivée à la puissance ±1, complétée par des unités de
base, et garder l'écriture la plus courte. Exemples : kg·m·s⁻² → N, V/A → Ω,
mS/cm → S·m⁻¹, kg·s⁻² → N·m⁻¹, N/C → V·m⁻¹, kBq → Bq. Hz, Gy et Sv ne sont jamais
choisis (voir [Pièges](#pièges)).

### Constantes

`grandeurs.constantes` donne les constantes en grandeurs, `grandeurs.flottants` les
mêmes noms en flottants SI (valeur centrale en unités de base). Les corrigés
existants calculent en flottants et formatent le résultat : ils importent
`grandeurs.flottants`, et leurs résultats ne changent pas. Le module principal
tient les constantes fondamentales et les unités en usage avec le SI ; trois
sous-modules, miroités dans `flottants`, tiennent le reste : `constantes.astro`
(UAI, Soleil, Terre, Lune), `constantes.cgs`, `constantes.us` (unités
anglo-saxonnes). `decrire("G")` donne la description et la source d'une constante,
`FICHES` les recense toutes, `codata(clé)` rend n'importe quelle constante de scipy
en grandeur et `cles_codata("Rydberg")` liste les clés.

| Groupe | Module | Source |
| --- | --- | --- |
| c, h, e, k, N_A, ΔνCs, K_cd et ce qui s'en déduit (ħ, R, F, K_J, R_K…) | `constantes` | CODATA 2022, exactes |
| G, ε₀, μ₀, α, masses, magnétons, Rydberg, Planck… | `constantes` | CODATA 2022 par scipy |
| minute, heure, degré, litre, hectare, bar, torr, mille marin, nœud… | `constantes` | brochure SI du BIPM |
| masse du W | `constantes` | Particle Data Group 2024 |
| R☉, L☉, S☉, T☉, (GM)☉, (GM)⊕ | `constantes.astro` | UAI 2015, résolution B3 (nominales) |
| ua, pc, année julienne, année-lumière | `constantes.astro` | UAI 2012 B2, UAI 2015 B2 |
| M☉, M⊕ | `constantes.astro` | (GM)/G, avec l'incertitude de G |
| R⊕, aplatissement ; orbite terrestre ; Lune ; H₀ | `constantes.astro` | WGS 84 ; Standish (JPL) ; UAI, NASA ; Planck 2018 |
| erg, dyne, poise, gauss, œrsted, gal… | `constantes.cgs` | brochure SI du BIPM, tableau 9 |
| pouce, pied, yard, mile, gallon, livre, once | `constantes.us` | NIST Handbook 44 |

Les incertitudes CODATA sont traitées comme indépendantes : scipy ne fournit pas les
corrélations. Le rapport de deux constantes mesurées a donc une incertitude
surestimée ; `codata("proton-electron mass ratio")` donne la valeur ajustée.

Noms : ceux de l'ancien `constantes` (`NA`, `H`, `HBAR`, `E`, `C`, `EPS_0`, `M_E`,
`R_GP`…), sauf cinq qu'un physicien lisait de travers, renommés sans alias :

| Ancien | Nouveau | Ce qu'on lisait |
| --- | --- | --- |
| `HA` | `HARTREE` | un hectare (`HECTARE`) |
| `G_0` | `G_N` | le quantum de conductance (`G_CONDUCTANCE`) |
| `KN` | `NOEUD` | un kilonewton |
| `NM` | `MILLE_MARIN` | un nanomètre |
| `GAL` | `cgs.GAL_CGS` | un gallon (`us.GAL_US`) |

### Angles

pint convertit les unités d'angle (`rad`, `°`, `arcmin`, `arcsec`, `tr`) ; un angle
est une grandeur. `grandeurs` ajoute la lecture et l'écriture sexagésimales, avec la
retenue faite sur le nombre total de secondes avant le découpage, la réduction
modulo un tour et son inverse sur une suite, le déroulement :

```python
from grandeurs import DMS, derouler, dms, ecrire_angle, grandeur, lire_angle, ramener

ecrire_angle(grandeur(30, "°").to("rad"))   # 30°00'00" (et non 29°59'60")
ecrire_angle(dms(-10, 30))                  # -10°30'00" : le signe vaut pour tout l'angle
lire_angle("30°15'20\"")                    # 30.3°
ramener(grandeur(370, "°"))                 # 10.0°, dans [0, 360°[ ; symetrique=True : ]-180°, 180°]
derouler(grandeur([350, 10, 20], "°"))      # [350; 370; 380]°
DMS.depuis(lire_angle("-10°30'")).latex()   # '\ang{-10;30;0}'
```

Un nombre nu passé à ces fonctions est en radians, comme dans pint.

### Sortie LaTeX pour pythontex

Aucun pont entre pythontex et siunitx n'existe ; `qty` et `num` écrivent la commande
siunitx depuis Python : `\qty{1.20(1)}{m.s^{-1}}`,
`\qty{8.854187819(1)e-12}{F.m^{-1}}`, `\num{0.007297352564(1)}`. L'incertitude est
en notation courte (siunitx l'affiche selon `uncertainty-mode`), la valeur arrondie
au rang de l'incertitude ou au réglage `chiffres`, l'exposant écrit `e3`. L'unité
est littérale, comme dans les documents existants (`kg.m^{-3}`, `\micro m`,
`k\ohm`, `\degreeCelsius`). Options : `incertitude=False`, `chiffres=3`,
`decimale=","` (siunitx lit les deux ; `output-decimal-marker` décide de
l'affichage), `notation`, une unité de conversion (`qty(v, "km/h")`) et
`macro="SI"` pour siunitx 2. Un tableau donne `\qtylist`. `lire_qty` relit
`\qty`, `\SI` et `\num`, unité littérale comprise.

## Tester

```bash
uv run pytest                                 # tout, doctests et document pythontex compris quand TeX est là
uv run pytest -m "not latex"                  # sans compiler le document pythontex
uv run --python 3.11 pytest                   # sous pint 0.25
uv run ruff check src tests && uv run ruff format --check src tests && uv run mypy
```

Les doctests des modules font partie de la suite (`--doctest-modules`). Le test
marqué `latex` (`tests/test_pythontex.py`) compile un document minimal par
`lualatex` et `pythontex`, avec l'interpréteur de la suite ; il est sauté quand TeX
manque. Aucun avertissement n'est toléré (`filterwarnings = error`). L'intégration
continue (`.github/workflows/ci.yml`) rejoue tout cela à chaque push, sous Python
3.11 et 3.14, puis construit la roue et le sdist ; à chaque release publiée,
`publish.yml` les joint à la release.

## Antériorité

L'étude d'antériorité d'octobre 2026 a conclu qu'il ne fallait pas réécrire un
système d'unités : pint couvre les unités, les préfixes, les unités affines (°C),
les conversions et les tableaux numpy ; uncertainties propage les incertitudes au
premier ordre, corrélations comprises ; scipy fournit CODATA. Ce qui manquait, et
que ce paquet ajoute : la lecture de `m.s-1` et de `J/mol.K` (pint les refuse, ou
lit le second comme J·K/mol) ; une sortie siunitx utilisable (le format `Lx` de pint
écrit `\SI[]{9.8+/-0.2}{…}`, que siunitx 3 refuse, et `\degree_Celsius`) ; les
chiffres significatifs d'après l'écriture et l'arrondi de l'affichage ; une
simplification en SI prévisible ; les constantes hors de scipy, sourcées ; les
angles sexagésimaux avec retenue.
[physpyx](https://physpyx.readthedocs.io/fr/latest/) (GPL) suit un autre flux (un
script autonome écrit un `.pyx` lu par LaTeX), sans pythontex, sans incertitudes ni
chiffres significatifs.

Ce paquet remplace les anciens modules `cs`, `units`, `constantes` et `angles` ;
les corrigés qui faisaient `from constantes import R_GP` font
`from grandeurs.flottants import R_GP`.

## Licence

Licence MIT (`LICENSE`).
