"""Intégration pythontex : un document minimal compilé de bout en bout.

Le test demande ``lualatex`` et ``pythontex`` (TeX Live) ; sans eux il est
sauté. pythontex est lancé avec l'interpréteur de la suite de tests, pour que
le document importe le paquet en cours de test et non un autre.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

DOCUMENT = r"""
\documentclass{article}
\usepackage{siunitx}
\usepackage{pythontex}
\begin{document}
\begin{pycode}
from grandeurs import grandeur, qty, num
from grandeurs.flottants import R_GP
v = grandeur("1.20 m.s-1")
\end{pycode}
$v = \py{qty(v)}$, $R = \py{num(R_GP)}$, $g = \py{qty(grandeur(9.79828, "m/s2"))}$

$v = \py{qty(v, style="pm")}$, $\rho = \py{qty(grandeur("1.20e3 kg.m-3"), style="pm")}$

$\py{qty(v, style="u", nom="v")}$ ; $\py{qty(v, style="U", nom="v")}$
\end{document}
"""


def _compiler(dossier: Path, *commande: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        commande, cwd=dossier, capture_output=True, text=True, check=False, timeout=300
    )


@pytest.mark.latex
def test_document_pythontex_minimal(tmp_path: Path) -> None:
    if not shutil.which("lualatex") or not shutil.which("pythontex"):
        pytest.skip("lualatex ou pythontex absent")
    (tmp_path / "doc.tex").write_text(DOCUMENT, encoding="utf-8")
    lualatex = ("lualatex", "-interaction=nonstopmode", "-halt-on-error", "doc.tex")
    assert _compiler(tmp_path, *lualatex).returncode == 0
    pythontex = _compiler(
        tmp_path, "pythontex", "--interpreter", f"python:{sys.executable}", "doc.tex"
    )
    assert pythontex.returncode == 0, pythontex.stdout + pythontex.stderr
    assert "0 error(s)" in pythontex.stdout
    assert _compiler(tmp_path, *lualatex).returncode == 0
    assert (tmp_path / "doc.pdf").exists()
    macros = (tmp_path / "pythontex-files-doc" / "doc.pytxmcr").read_text(encoding="utf-8")
    assert r"\qty{1.20(1)}{m.s^{-1}}" in macros
    assert r"\qty{1.20 \pm 0.02}{m.s^{-1}}" in macros
    assert r"\qty{1.20 \pm 0.02 e3}{kg.m^{-3}}" in macros
    assert r"v = \qty{1.20}{m.s^{-1}} ; u(v) = \qty{0.01}{m.s^{-1}}" in macros
    assert r"v = \qty{1.20}{m.s^{-1}} ; U(v) = \qty{0.02}{m.s^{-1}}" in macros
    assert r"\num{8.31}" in macros
    assert r"\qty{9.80}{m.s^{-2}}" in macros
