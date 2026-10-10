# grandeursphy

Grandeurs physiques pour la classe et les corrigés : une valeur, son incertitude et
son unité, écrites comme dans un manuel (`m.s-1`, `J.mol-1.K-1`), comparées
physiquement (`unit("N") == unit("kg.m.s^(-2)")`), simplifiées en SI et sorties pour
siunitx depuis pythontex. Le paquet s'appelle `grandeurs` ; il est une couche au-dessus
de [pint](https://github.com/hgrecco/pint) (unités),
[uncertainties](https://github.com/lmfit/uncertainties) (propagation des
incertitudes) et `scipy.constants` (CODATA 2022). Il remplace les anciens paquets
`cs`, `units`, `constantes` et `angles`.

```python
from grandeurs import grandeur, unit, qty
from grandeurs import constantes as cst

unit("N") == unit("kg.m.s^(-2)")       # True
v = grandeur("1.20 m.s-1")             # « 1.20 » : trois chiffres significatifs
d = v * grandeur("2.0 s")
print(d)                               # (2.4 ± 0.1) m
print(v.vers("km/h"))                  # (4.32 ± 0.04) km·h⁻¹
F = grandeur("2.0 kg") * grandeur("9.81 m.s-2")
print(F.si())                          # (20 ± 1) N
print((cst.R_GP * grandeur(20, "°C")).si())   # 2437.38471651162 J·mol⁻¹
qty(d)                                 # '\qty{2.4(1)}{m}'
```

## Installation

Dépendances : pint ≥ 0.25, numpy, scipy ≥ 1.15 (première version qui fournit
CODATA 2022), uncertainties ≥ 3.2. pint 0.26 exige Python 3.12 ; sous Python 3.11,
c'est pint 0.25 qui s'installe, et le paquet fonctionne avec les deux.

Le paquet sert hors de tout environnement virtuel par le `PYTHONPATH`, qui contient
`/Users/elessar/pyphysique/grandeursphy/src`. Les dépendances doivent alors être
installées dans l'interpréteur qui exécute le code :

```bash
~/Envs/Main/bin/python -m pip install "pint>=0.25" "uncertainties>=3.2" "scipy>=1.15"
~/Envs/pythontex/bin/python -m pip install "pint>=0.25" "uncertainties>=3.2" "scipy>=1.15"
```

Pour le développement :

```bash
uv sync
uv run pytest
UV_PROJECT_ENVIRONMENT=.venv311 uv run --python 3.11 pytest
uv run ruff format src tests && uv run ruff check src tests && uv run mypy
```

## Ce qui existait déjà, et ce qui manquait

L'étude d'antériorité du 8 octobre 2026 (`../AUDIT.md`) a conclu qu'il ne fallait
pas réécrire un système d'unités : pint couvre les unités, les préfixes, les unités
affines (°C), les conversions et les tableaux numpy ; uncertainties propage les
incertitudes au premier ordre, corrélations comprises ; scipy fournit CODATA. Ce qui
manquait, et que ce paquet ajoute :

- la lecture des notations françaises : pint refuse `m.s-1` ;
- l'égalité physique des unités : pour pint, `Unit("N") == Unit("kg*m/s**2")` est
  faux ;
- les chiffres significatifs d'après l'écriture (« 1.20 ») et l'arrondi de
  l'affichage d'après l'incertitude ;
- une simplification en SI qui choisit les unités dérivées (N, J, W, V, Ω…) ;
- les constantes hors de scipy (astronomie UAI, CGS, Terre, Lune, masse du W) ;
- les angles en degrés-minutes-secondes ;
- la sortie siunitx pour pythontex.

## Choix de conception

### Une grandeur est une quantité pint

`grandeur(...)` rend une `Grandeur`, sous-classe de la `Quantity` de pint, déclarée
comme classe des quantités d'un registre pint unique (`grandeurs.ureg`, aussi
registre d'application de pint). Une grandeur est donc une quantité pint à part
entière : conversions, numpy, unités affines et compatibilité avec les bibliothèques
qui connaissent pint viennent sans code. Une classe qui envelopperait une quantité
aurait dû réexposer tout cela, opérateur par opérateur. La valeur d'une grandeur
peut être un nombre, un tableau, un `ufloat` ou un tableau de `ufloat` : pint les
transporte, uncertainties propage.

```python
from grandeurs import grandeur

g = grandeur("1.20 m.s-1")      # incertitude d'après l'écriture
g = grandeur(1.2, "m/s")        # exacte
g = grandeur(1.2, "m", incertitude=0.05)
g = grandeur(1.2, "m", incertitude="5 cm")
g = grandeur([1.0, 2.0], "m", incertitude=[0.1, 0.2])
g = grandeur("1.20 km", "m")    # lue puis convertie
g.valeur, g.incertitude, g.incertitude_relative, g.chiffres, g.valeur_si
```

### Notations de manuel

La traduction des notations est branchée comme préprocesseur du registre : elle
s'applique à toute chaîne que pint lit, donc aussi à `q.to("km.h-1")`. Sont lus le
produit par `.`, `·`, `*` ou une espace ; les puissances `^n`, `**n`, `^(n)`, `^{n}`,
`s⁻¹`, et l'entier collé au nom (`m2`, `s-1`) ; les variantes Unicode (µ/μ, Ω/Ω).
Une juxtaposition ou un point après une barre reste au dénominateur : `J/mol.K` se
lit J/(mol·K), le seul sens qu'on lui donne en physique, alors que `J/mol*K` garde
la priorité de Python. Quelques noms français sont ajoutés : `j` (jour), `an`, `tr`
(`tr/min`), `Torr`. On n'ajoute pas `ua` ni `al`, que pint lit déjà comme
micro-année et attolitre : on écrit `au` et `ly`.

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

Une grandeur créée sans unité (`grandeur(3)`) est presque toujours un oubli : elle
passe, sans dimension, et l'oubli est signalé selon le réglage `sans_unite` ; pour
une grandeur réellement sans dimension, on l'écrit, `grandeur(0.5, "")`. Tout le
reste suit les règles de pint : `longueur + 2` est refusé, 1 m n'est pas le nombre
1, deux dimensions incompatibles ne s'additionnent pas. Les réglages sont un objet
figé (`Reglages`) qu'on change par `configurer(**champs)` ou, le temps d'un bloc,
par `with reglages_temporaires(**champs):`.

| Réglage | Défaut | Rôle |
| --- | --- | --- |
| `sans_unite` | `"avertissement"` | grandeur créée sans unité : `"silence"`, `"avertissement"` ou `"erreur"` |
| `chiffres_significatifs` | `True` | « 1.20 » porte une incertitude de 0,01 ; sinon il est exact |
| `chiffres_incertitude` | `1` | chiffres significatifs gardés sur l'incertitude à l'affichage |
| `afficher_incertitude` | `True` | sinon, valeur seule, arrondie à ses chiffres significatifs |
| `style_incertitude` | `"pm"` | à l'écran : `(1.20 ± 0.01) m` ou `"courte"` : `1.20(1) m` |
| `decimale` | `"."` | `","` pour la virgule française |
| `notation` | `"auto"` | `"fixe"`, `"scientifique"`, `"ingenieur"` |

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
fixe les chiffres significatifs. L'arrondi se fait en décimal, au plus proche, demi
vers le haut (2,675 donne 2,68). Une valeur exacte s'écrit avec 15 chiffres au plus,
ce qui efface le bruit des conversions (1 mol/L donne 1000 mol/m³).

uncertainties déprécie les comparaisons d'ordre, `abs`, `%` et `//` sur ses
nombres. Les comparaisons d'ordre portent donc sur les valeurs centrales, `abs`
change le signe des valeurs centrales négatives (l'incertitude et les corrélations
restent), et `round` refuse une grandeur incertaine : ce sont ses incertitudes qui
fixent ses chiffres, et on l'écrit avec `.texte(chiffres=…)`. L'égalité `==` de deux
mesures indépendantes de même valeur est fausse : pour uncertainties, deux variables
aléatoires ne sont égales que si leur différence est exactement nulle.

`np.sqrt` échoue sur un `ufloat` ; `grandeurs.fonctions` fournit `sqrt`, `exp`,
`ln`, `log10`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, qui acceptent nombres,
`ufloat`, tableaux et grandeurs, et vérifient les unités (un sinus prend un angle).

### Simplification en SI

`to_preferred` de pint, essayé avec les unités dérivées, écrit une accélération
« Hz·W/N ». `.si()` suit une règle plus étroite et prévisible : passer en unités de
base ; si cette écriture est celle d'une unité de la table des préférées (N, Pa, J,
W, C, V, F, Ω, S, Wb, T, H, lm, lx, Bq, N/m, C/kg, S/m, Ω·m, V/m, A/m, H/m, F/m,
Pa·s, W/(m·K), J/(kg·K), J/(mol·K), J/K, J/mol, W/m²), l'écrire ainsi ; sinon, si
la dimension ne contient ni masse ni courant, s'arrêter (m·s⁻², m²·s⁻¹, mol·m⁻³) ;
sinon essayer chaque unité dérivée à la puissance ±1, complétée par des unités de
base, et garder l'écriture la plus courte. Exemples : kg·m·s⁻² → N, V/A → Ω,
mS/cm → S·m⁻¹, kg·s⁻² → N·m⁻¹, N/C → V·m⁻¹, kBq → Bq. Le hertz n'est jamais
choisi : une dimension temps⁻¹ est une fréquence ou une vitesse angulaire (le radian
est sans dimension), et seul l'utilisateur sait laquelle ; `2π rad × f` donne
rad·s⁻¹, `1/T` donne s⁻¹. Le gray et le sievert (J/kg, soit m²·s⁻²) ne le sont pas
non plus. On convertit explicitement par `.vers("Hz")`, `.vers("Gy")`.

### Constantes

`grandeurs.constantes` donne les constantes en grandeurs, `grandeurs.flottants` les
mêmes noms en flottants SI (valeur centrale en unités de base). Les corrigés
existants calculent en flottants et formatent le résultat : ils importent
`grandeurs.flottants`, et leurs résultats ne changent pas. `decrire("G")` donne la
description et la source d'une constante, `FICHES` les recense toutes, `codata(clé)`
rend n'importe quelle constante de scipy en grandeur.

| Groupe | Source |
| --- | --- |
| c, h, e, k, N_A, ΔνCs, K_cd et ce qui s'en déduit (ħ, R, F, K_J, R_K…) | CODATA 2022, exactes |
| G, ε₀, μ₀, α, masses, magnétons, Rydberg, Planck… | CODATA 2022 par scipy |
| R☉, L☉, S☉, T☉, (GM)☉, (GM)⊕ | UAI 2015, résolution B3 (nominales) |
| ua, pc, année julienne, année-lumière | UAI 2012 B2, UAI 2015 B2 |
| M☉, M⊕ | (GM)/G, avec l'incertitude de G |
| R⊕, aplatissement | WGS 84 |
| orbite terrestre (a, e) | Standish, JPL, positions approchées des planètes |
| Lune : masse, rayon, orbite | rapport des masses UAI 2009, rayon UAI/WGCCRE, NASA |
| masse du W | Particle Data Group 2024 |
| H₀ | Planck 2018 |
| unités CGS, anglo-saxonnes, hors SI | brochure SI du BIPM, NIST Handbook 44 |

Les incertitudes CODATA sont traitées comme indépendantes : scipy ne fournit pas les
corrélations. Le rapport de deux constantes mesurées a donc une incertitude
surestimée ; `codata("proton-electron mass ratio")` donne la valeur ajustée.

Noms : ceux de l'ancien `constantes` (`NA`, `H`, `HBAR`, `E`, `C`, `EPS_0`, `M_E`,
`R_GP`…), sans masquage. Trois noms désignaient deux grandeurs ; ils gardent le sens
qu'`import constantes` leur donnait, et l'autre sens reçoit un nom :

| Nom | Sens | Ancien sens masqué, renommé |
| --- | --- | --- |
| `G_0` | pesanteur normale | quantum de conductance : `G_CONDUCTANCE` |
| `HA` | énergie de Hartree | hectare : `HECTARE` |
| `GAL` | gal, unité CGS d'accélération | gallon américain : `GAL_US` |

Valeurs corrigées par rapport à l'ancien paquet : pouce (0,0254 m et non 0,254 m,
et avec lui pied, yard et mile), gallon (en m³), zéro Celsius `T0` (273,15 K et non
273,16 K), rayon lunaire (1 737,4 km et non 1,737 km), température de Planck (avec
la masse de Planck), magnéton nucléaire (avec la masse du proton), G (CODATA 2022 au
lieu de 2014), `K_CD` (683 lm/W ; les 540 THz sont `NU_CD`, et `CD` est l'intensité
énergétique de 1 cd, 1/683 W/sr), œrsted (en A/m), `mmHG` (millimètre de mercure
conventionnel ; le torr est `TORR`), valeurs astronomiques datées (UAI 2015). Ajouts :
`NU_CD`, `TORR`, `STATC`, `GM_sun`, `GM_earth`, `S_sun`, `T_sun`.

Les constantes exactes ont les mêmes flottants qu'avec CODATA 2018 ; les constantes
mesurées ont leur valeur CODATA 2022. Il faut scipy ≥ 1.15 : avec scipy 1.14 et
avant (CODATA 2018), `grandeurs.constantes` refuse de se charger plutôt que de donner
d'autres valeurs.

### Angles

pint convertit les unités d'angle (`rad`, `°`, `arcmin`, `arcsec`, `tr`) ; un angle
est une grandeur. `grandeurs` ajoute la lecture et l'écriture sexagésimales, avec la
retenue faite sur le nombre total de secondes avant le découpage :

```python
from grandeurs import DMS, dms, ecrire_angle, grandeur, lire_angle, ramener

ecrire_angle(grandeur(30, "°").to("rad"))   # 30°00'00" (et non 29°59'60")
ecrire_angle(dms(-10, 30))                  # -10°30'00" : le signe vaut pour tout l'angle
lire_angle("30°15'20\"")                    # 30.2555555555556°
ramener(grandeur(370, "°"))                 # 10°, dans [0, 360°[ ; symetrique=True : ]-180°, 180°]
DMS.depuis(lire_angle("-10°30'")).latex()   # '\ang{-10;30;0}'
```

Un nombre nu passé à ces fonctions est en radians, comme dans pint.

### Sortie LaTeX pour pythontex

Aucun pont entre pythontex et siunitx n'existe ; `qty` et `num` écrivent la commande
siunitx depuis Python :

```latex
\begin{pycode}
from grandeurs import grandeur, qty, num
from grandeurs import constantes as cst
v = grandeur("1.20 m.s-1")
\end{pycode}
$v = \py{qty(v)}$, $\varepsilon_0 = \py{qty(cst.EPS_0)}$, $\alpha = \py{num(cst.ALPHA)}$
```

donne `\qty{1.20(1)}{m.s^{-1}}`, `\qty{8.854187819(1)e-12}{F.m^{-1}}`,
`\num{0.007297352564(1)}`. L'incertitude est en notation courte (siunitx l'affiche
selon `uncertainty-mode`), la valeur arrondie au rang de l'incertitude, l'exposant
écrit `e3`. L'unité est littérale, comme dans les documents existants (`kg.m^{-3}`,
`\micro m`, `k\ohm`, `\degreeCelsius`). Options : `incertitude=False`, `chiffres=3`,
`decimale=","` (siunitx lit les deux ; `output-decimal-marker` décide de
l'affichage), `notation`, une unité de conversion (`qty(v, "km/h")`) et
`macro="SI"` pour siunitx 2. Un tableau donne `\qtylist`.

## Correspondance avec l'ancien code

| Ancien | Nouveau |
| --- | --- |
| `from constantes import R_GP` (flottants) | `from grandeurs.flottants import R_GP` |
| `constantes.X` comme grandeur | `from grandeurs.constantes import X` |
| `CS("1.20")` | `grandeur("1.20")`, ou `grandeur("1.20", "m")` |
| `SI("5.00", "mm")` | `grandeur("5.00 mm")` |
| `set_confiance`, `set_warnings` | `configurer(...)` |
| `units.Unit`, `vitesse(36, "km/h")` | `grandeur(36, "km/h").vers("m/s")` |
| `Angle(deg=30).format("dms")` | `ecrire_angle(dms(30))` |

`cs`, `units` et `angles` n'avaient aucun utilisateur ; leur code est dans
l'historique git (premier commit) et dans `../_archives/ancien-2026-10-08/`.

## Licence

Licence MIT (`LICENSE`).
