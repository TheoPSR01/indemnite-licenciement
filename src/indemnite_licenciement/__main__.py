"""Ligne de commande : ``indemnite-licenciement 2500 --entree 2015-03-01 --fin 2026-02-28``."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from decimal import Decimal, InvalidOperation

from . import __version__, anciennete_mois, indemnite_legale, salaire_reference


def _date(v: str) -> date:
    try:
        if "/" in v:
            j, m, a = v.split("/")
            return date(int(a), int(m), int(j))
        return date.fromisoformat(v)
    except ValueError:
        raise argparse.ArgumentTypeError(f"date invalide : {v!r} (AAAA-MM-JJ ou JJ/MM/AAAA)")


def _nombre(v: str) -> Decimal:
    try:
        return Decimal(v.replace(",", ".").replace(" ", ""))
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"nombre invalide : {v!r}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="indemnite-licenciement",
        description="Indemnité légale de licenciement (Code du travail). "
                    "Donner soit un salaire de référence, soit --salaires.",
    )
    p.add_argument("--version", action="version", version=f"indemnite-licenciement {__version__}")
    p.add_argument("salaire", type=_nombre, nargs="?", help="salaire de référence mensuel brut")
    p.add_argument("--salaires", type=_nombre, nargs="+", help="salaires bruts des 12 derniers mois, du plus ancien au plus récent")
    p.add_argument("--primes", type=_nombre, default=Decimal(0), help="primes annuelles comprises dans les 3 derniers mois")
    p.add_argument("--entree", type=_date, help="date d'entrée dans l'entreprise")
    p.add_argument("--fin", type=_date, help="date de fin du contrat, préavis inclus")
    p.add_argument("--mois", type=int, help="ancienneté en mois complets (à la place des dates)")
    p.add_argument("--faute-grave", action="store_true", help="licenciement pour faute grave ou lourde")
    args = p.parse_args(argv)

    if args.salaires:
        sal = salaire_reference(args.salaires, args.primes)
    elif args.salaire is not None:
        sal = args.salaire
    else:
        p.error("indiquer le salaire de référence ou --salaires")
    if args.mois is not None:
        anc = args.mois
    elif args.entree and args.fin:
        try:
            anc = anciennete_mois(args.entree, args.fin)
        except ValueError as exc:
            p.error(str(exc))
    else:
        p.error("indiquer --entree et --fin, ou --mois")

    r = indemnite_legale(sal, anc, args.faute_grave)
    sal_txt = f"{r.salaire_reference:,.2f}".replace(",", " ").replace(".", ",")
    print(f"Salaire de référence : {sal_txt} €")
    print(f"Indemnité légale     : {r}")
    if r.ouvre_droit:
        print("Votre convention collective ou votre contrat peut prévoir davantage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
