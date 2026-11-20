from datetime import date
from decimal import Decimal

import pytest

from indemnite_licenciement import anciennete_mois, calculer, indemnite_legale, salaire_reference
from indemnite_licenciement.__main__ import main


@pytest.mark.parametrize("salaire,mois,attendu", [
    (1500, 12 * 12 + 9, "5125.00"),    # exemple de service-public.fr : 12 ans et 9 mois
    (2000, 36, "1500.00"),             # 3 ans
    (2500, 120, "6250.00"),            # 10 ans pile
    (3500, 12 * 12 + 6, "11666.67"),   # 12 ans et 6 mois
    (2500, 8, "416.67"),               # 8 mois : le minimum
    (3000, 7 * 12 + 4, "5500.00"),     # 7 ans et 4 mois
])
def test_montants(salaire, mois, attendu):
    assert indemnite_legale(salaire, mois).montant == Decimal(attendu)


def test_moins_de_8_mois():
    r = indemnite_legale(2500, 7)
    assert r.montant == 0 and not r.ouvre_droit


def test_faute_grave():
    r = indemnite_legale(2500, 120, faute_grave=True)
    assert r.montant == 0 and not r.ouvre_droit


@pytest.mark.parametrize("entree,fin,attendu", [
    (date(2020, 1, 1), date(2020, 12, 31), 12),
    (date(2015, 3, 15), date(2025, 3, 14), 120),
    (date(2015, 3, 15), date(2025, 3, 13), 119),
    (date(2025, 5, 10), date(2026, 1, 9), 8),
    (date(2025, 5, 10), date(2026, 1, 8), 7),
])
def test_anciennete(entree, fin, attendu):
    assert anciennete_mois(entree, fin) == attendu


def test_anciennete_dates_inversees():
    with pytest.raises(ValueError):
        anciennete_mois(date(2025, 1, 1), date(2024, 1, 1))


def test_salaire_reference_12_mois_plus_favorable():
    salaires = [3000] * 6 + [2000] * 6
    assert salaire_reference(salaires) == Decimal(2500)


def test_salaire_reference_3_mois_plus_favorable():
    salaires = [2000] * 9 + [2600] * 3
    assert salaire_reference(salaires) == Decimal(2600)


def test_salaire_reference_prime_annuelle_proratisee():
    # 13e mois de 2 400 € versé en décembre : retenu pour 3/12 sur les 3 derniers mois
    salaires = [2400] * 11 + [4800]
    assert salaire_reference(salaires, primes_annuelles_3_mois=2400) == Decimal(2600)


def test_salaire_reference_moins_de_12_mois():
    assert salaire_reference([2000, 2100, 2200, 2300]) == Decimal(2200)


def test_calculer():
    r = calculer(date(2013, 6, 1), date(2026, 2, 28), [1500] * 12)
    assert r.anciennete_mois == 12 * 12 + 9
    assert r.montant == Decimal("5125.00")


def test_cli(capsys):
    assert main(["1500", "--mois", "153"]) == 0
    assert "5 125,00 €" in capsys.readouterr().out
    assert main(["--salaires", *["2000"] * 12, "--entree", "2023-01-01", "--fin", "2025-12-31"]) == 0
    assert "1 500,00 €" in capsys.readouterr().out


def test_cli_aide(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
