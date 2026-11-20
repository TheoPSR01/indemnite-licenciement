"""indemnite_licenciement : indemnité légale de licenciement (droit du travail français).

- Droit ouvert aux salariés en CDI comptant au moins 8 mois d'ancienneté
  ininterrompue, sauf faute grave ou lourde (article L1234-9).
- Montant (article R1234-2) : 1/4 de mois de salaire par année d'ancienneté
  jusqu'à 10 ans, puis 1/3 de mois par année au-delà.
- Années incomplètes : prorata des mois complets (article R1234-1).
- Salaire de référence (article R1234-4) : le plus favorable entre la moyenne
  des 12 derniers mois et celle des 3 derniers mois, les primes annuelles
  versées dans ces 3 mois n'étant retenues que pour un quart.

L'indemnité spécifique de rupture conventionnelle ne peut pas être inférieure
à ce montant. Une convention collective ou le contrat peut prévoir plus.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable, Union

__version__ = "0.1.0"

Montant = Union[int, float, str, Decimal]
ANCIENNETE_MINIMUM_MOIS = 8
CENT = Decimal("0.01")


def _d(x: Montant) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


@dataclass(frozen=True)
class Resultat:
    montant: Decimal
    salaire_reference: Decimal
    anciennete_mois: int
    mois_de_salaire: Decimal      # nombre de mois de salaire accordés
    ouvre_droit: bool
    detail: str

    def __str__(self) -> str:
        m = f"{self.montant:,.2f}".replace(",", " ").replace(".", ",")
        return f"{m} € ({self.detail})"


def anciennete_mois(entree: date, fin_contrat: date) -> int:
    """Nombre de mois complets entre l'entrée et la fin du contrat (préavis inclus).

    Le dernier jour du contrat est compté : un contrat du 1er janvier au
    31 décembre fait 12 mois complets.
    """
    if fin_contrat < entree:
        raise ValueError("la fin du contrat précède l'entrée")
    lendemain = fin_contrat + timedelta(days=1)
    mois = (lendemain.year - entree.year) * 12 + (lendemain.month - entree.month)
    if lendemain.day < entree.day:
        mois -= 1
    return max(mois, 0)


def salaire_reference(salaires: Iterable[Montant], primes_annuelles_3_mois: Montant = 0) -> Decimal:
    """Salaire de référence (article R1234-4).

    ``salaires`` : salaires bruts mensuels, du plus ancien au plus récent, sur
    les 12 derniers mois (ou tous les mois travaillés si moins de 12).
    ``primes_annuelles_3_mois`` : primes annuelles ou exceptionnelles comprises
    dans les 3 derniers salaires, à proratiser.
    """
    s = [_d(x) for x in salaires][-12:]
    if not s:
        raise ValueError("au moins un salaire mensuel est nécessaire")
    primes = _d(primes_annuelles_3_mois)
    moyenne_12 = sum(s) / len(s)
    trois = s[-3:]
    total_3 = sum(trois) - primes + primes * Decimal(3) / Decimal(12)
    moyenne_3 = total_3 / len(trois)
    return max(moyenne_12, moyenne_3)


def indemnite_legale(salaire_ref: Montant, anciennete: int, faute_grave: bool = False) -> Resultat:
    """Indemnité légale pour ``anciennete`` mois complets et un salaire de référence mensuel."""
    sal = _d(salaire_ref)
    if sal < 0 or anciennete < 0:
        raise ValueError("salaire et ancienneté doivent être positifs")
    if faute_grave:
        return Resultat(Decimal(0), sal, anciennete, Decimal(0), False, "pas d'indemnité en cas de faute grave ou lourde")
    if anciennete < ANCIENNETE_MINIMUM_MOIS:
        return Resultat(Decimal(0), sal, anciennete, Decimal(0), False,
                        f"ancienneté inférieure à {ANCIENNETE_MINIMUM_MOIS} mois")
    annees = Decimal(anciennete) / Decimal(12)
    jusqua_10 = min(annees, Decimal(10))
    au_dela = max(annees - Decimal(10), Decimal(0))
    mois_salaire = jusqua_10 / 4 + au_dela / 3
    montant = (sal * mois_salaire).quantize(CENT, rounding=ROUND_HALF_UP)
    a, m = divmod(anciennete, 12)
    detail = f"{a} an(s) et {m} mois : {_fr(jusqua_10)} × 1/4"
    if au_dela:
        detail += f" + {_fr(au_dela)} × 1/3"
    detail += f" = {_fr(mois_salaire)} mois de salaire"
    return Resultat(montant, sal, anciennete, mois_salaire, True, detail)


def _fr(x: Decimal) -> str:
    return f"{x.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP):f}".rstrip("0").rstrip(".").replace(".", ",")


def calculer(entree: date, fin_contrat: date, salaires: Iterable[Montant],
             primes_annuelles_3_mois: Montant = 0, faute_grave: bool = False) -> Resultat:
    """Raccourci : ancienneté à partir des dates, salaire de référence à partir des salaires."""
    return indemnite_legale(
        salaire_reference(salaires, primes_annuelles_3_mois),
        anciennete_mois(entree, fin_contrat),
        faute_grave,
    )


__all__ = ["ANCIENNETE_MINIMUM_MOIS", "Resultat", "anciennete_mois", "calculer", "indemnite_legale", "salaire_reference"]
