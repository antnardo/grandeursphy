# coding: utf8
UNIT_MULTIPLIERS = {'k': 1e3, 'M': 1e6, 'm': 1e-3, 'G': 1e9, 'n': 1e-9, 'µ': 1e-6}
VERBOSE = False


def mult_function(v):
    # obligatoire pour rendre local v, sinon vglobal dans un lambda...
    return lambda x: x*v


class UnitBase:
    def __init__(self, symbole=None):
        self.symbole = symbole

    def set_symbole(self, symbole):
        self.symbole = symbole

    @property
    def nom(self):
        return NotImplemented

    def __call__(self, value, unit, verbose=VERBOSE):
        if verbose:
            print(f'{value} {unit} -> {self.nom}')
        return self.convert(value, unit)

    def convert(self, value, nom=None):
        return NotImplemented

    @staticmethod
    def merge_dict(dict1, dict2):
        keys = set(list(dict1.keys())+list(dict2.keys()))
        return {k: dict1.get(k, 0)+dict2.get(k, 0) for k in keys}

    @property
    def latex(self):
        s = self.nom
        s = s.replace('(', '{')
        s = s.replace(')', '}')
        return r"$\mathrm{"+s+r"}$"

    def __str__(self):
        return f"{self.symbole}({self.nom})"

    def __repr__(self):
        if type(self) is Unit:
            cls_name = 'Unit'
        elif type(self) is UnitCompound:
            cls_name = 'UnitCompound'
        return f'{cls_name}(symbole={self.symbole}, nom={self.nom})'

    def __mul__(self, unit):
        if type(self) is Unit and type(unit) is Unit:
            if unit == self:
                return UnitCompound({self.copy(): 2})
            return UnitCompound({self.copy(): 1, unit.copy(): 1})
        elif type(self) is UnitCompound and type(unit) is Unit:
            p = self.powers.copy()
            if unit in p:
                p[unit] += 1
            else:
                p[unit] = 1
            return UnitCompound(p)
        elif type(self) is UnitCompound and type(unit) is UnitCompound:
            p = self.merge_dict(self.powers, unit.powers)
            return UnitCompound(p)
        elif type(unit) is int:
            return self
        return NotImplemented

    def __truediv__(self, unit):
        return self*(unit**(-1))

    def __pow__(self, p):
        if type(self) is Unit:
            return UnitCompound({self.copy(): p})
        elif type(self) is UnitCompound:
            powers = {k: v*p for k, v in self.powers.items()}
            return UnitCompound(powers)
        else:
            return NotImplemented

    def __rmul__(self, unit):
        return self*unit

    def __rtruediv__(self, unit):
        return self**(-1)*unit


class Unit(UnitBase):
    def __init__(self, symbole='', SI='', conversions=None, default=None, collapse=False, inverse_conversions=None):
        super().__init__(symbole)
        self.SI = SI
        # default behavior :
        if default is None:
            default = SI
        self.default = default
        # conversions d'unités
        if conversions is None:
            conversions = dict()
        self.conversions = conversions.copy()
        if inverse_conversions is None:
            inverse_conversions = dict()
        self.inverse_conversions = inverse_conversions.copy()
        self.conversions[self.SI] = 1
        self.provided_conversions = set()
        for k, v in self.conversions.items():
            if type(v) in [int, float]:
                self.conversions[k] = mult_function(v)
            elif callable(v):
                self.conversions[k] = v
                self.provided_conversions.add(k)
                self.provided_conversions.add(self.SI)
            else:
                raise NotImplementedError
        # generates unit multipliers conversions
        self.collapse = collapse  # special treatment of kg
        if not collapse:
            for mult, v in UNIT_MULTIPLIERS.items():
                self.conversions[mult+self.SI] = mult_function(v)
        else:
            # special treatment of kg
            first_mult = self.SI[0]
            base = self.SI[1:]
            main_v = UNIT_MULTIPLIERS[first_mult]
            self.conversions[base] = mult_function(1/main_v)
            for mult, v in UNIT_MULTIPLIERS.items():
                for km, vm in UNIT_MULTIPLIERS.items():
                    if vm == v*main_v:
                        self.conversions[km+base] = mult_function(v)

    def convert(self, value, unit):
        if unit == self.default:
            return value
        elif unit not in self.provided_conversions:
            facteur = self.conversions[self.default](1)
            return self.conversions[unit](value)/facteur
        elif self.default == self.SI:
            return self.conversions[unit](value)
        else:
            return self.inverse_conversions[self.default](value)

    def copy(self):
        return Unit(symbole=self.symbole, SI=self.SI, conversions=self.conversions, default=self.default,
                    collapse=self.collapse, inverse_conversions=self.inverse_conversions)

    def set_default(self, nom=None):
        if nom is None:
            self.default = self.SI
        else:
            assert nom in self.conversions
            self.default = nom

    @property
    def nom(self):
        return self.default

    def __hash__(self):
        # in order to be usable in dict keys
        return hash(self.SI)

    def part_of(self, nom):
        return nom in self.conversions.keys()


class UnitCompound(UnitBase):
    unit_powers = {'*', '^', '/'}

    def __init__(self, powers):
        super().__init__('')
        self.powers = powers  # dict of Unit->power
        to_pop = [k for k, v in self.powers.items() if v == 0]
        for k in to_pop:
            self.powers.pop(k)
        # sort
        L = sorted([(k, v) for k, v in self.powers.items()], key=lambda x: x[1], reverse=True)
        self.powers = {k: v for k, v in L}

    @property
    def nom(self):
        fmt = UnitCompound.develop_nameformat(list(self.powers.values()))
        unit_names = [unit.default for unit in self.powers.keys()]
        return fmt.format(*unit_names)

    @staticmethod
    def develop_nameformat(powers):
        return '*'.join(['{}'+('' if p == 1 else (f'^{p:d}' if p > 0 else f'^({p:d})')) for p in powers])

    def convert(self, value, nom_unit):
        v = 1
        for unit, nom_unit, p in self.iterate(nom_unit):
            v *= unit(1, nom_unit)**p
        return v

    @staticmethod
    def cut_name(nom):
        # regex with / and ^ and * and mult
        cur_unit = ''
        cur_pow = 1
        d = dict()
        nom = ''.join([c for c in nom if c != ' '])
        i = 0
        while i < len(nom):
            c = nom[i]
            if c in ['*', '/']:
                d[cur_unit] = cur_pow
                cur_unit = ''
                cur_pow = 1 if c == '*' else -1
                i += 1
            elif c == '^':
                j = i+1
                c = nom[j]
                while j < len(nom) and (c.isdigit() or c == '-'):
                    j += 1
                    c = nom[j]
                cur_pow = int(nom[i+1:j])
                i = j-1
            else:
                cur_unit += c
                i += 1
        if cur_unit != '':
            d[cur_unit] = cur_pow
        return d

    def iterate(self, nom):
        if nom is None:
            for unit, p in self.powers.items():
                yield unit, unit.default, p
        else:
            d = UnitCompound.cut_name(nom)
            test = False
            for nom_unit, power in d.items():
                for unit, p in self.powers.items():
                    if unit.part_of(nom_unit):
                        assert p == power
                        test = True
                        yield unit, nom_unit, p
                        break
            assert test

    def set_unit_default(self, unit_symbole, default):
        for unit in self.powers.keys():
            if unit.symbole == unit_symbole:
                unit.set_default(default)
                break

    def set_default(self, nom=None):
        for unit, nom_unit, p in self.iterate(nom):
            if nom is None:
                nom_unit = None
            unit.set_default(nom_unit)

