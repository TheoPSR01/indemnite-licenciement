# indemnite-licenciement

Calculer l'indemnité légale de licenciement (et le minimum de l'indemnité de rupture conventionnelle) en France, en ligne de commande ou en Python. Aucune dépendance.

Salariés, représentants du personnel, services RH et étudiants en droit social peuvent vérifier un montant en quelques secondes, avec le détail du calcul.

## Installation

```bash
pip install git+https://github.com/TheoPSR01/indemnite-licenciement.git
```

Python 3.10 ou plus récent.

## En ligne de commande

Avec un salaire de référence et les dates du contrat (préavis inclus) :

```bash
indemnite-licenciement 2500 --entree 2015-03-01 --fin 2026-02-28
```

```
Salaire de référence : 2 500,00 €
Indemnité légale     : 7 083,33 € (11 an(s) et 0 mois : 10 × 1/4 + 1 × 1/3 = 2,833 mois de salaire)
Votre convention collective ou votre contrat peut prévoir davantage.
```

Avec les 12 derniers salaires bruts, l'outil calcule lui-même le salaire de référence :

```bash
indemnite-licenciement --salaires 2400 2400 2400 2400 2400 2400 2400 2400 2400 2400 2400 4800 --primes 2400 --mois 60
```

Options : `--mois` pour donner directement l'ancienneté en mois complets, `--primes` pour les primes annuelles versées dans les 3 derniers mois, `--faute-grave` pour un licenciement pour faute grave ou lourde.

## En Python

```python
from datetime import date
from indemnite_licenciement import calculer, indemnite_legale

r = indemnite_legale(salaire_ref=1500, anciennete=12 * 12 + 9)
print(r.montant)   # Decimal('5125.00')

r = calculer(date(2013, 6, 1), date(2026, 2, 28), salaires=[1500] * 12)
print(r)           # 5 125,00 € (12 an(s) et 9 mois : 10 × 1/4 + 2,75 × 1/3 = 3,417 mois de salaire)
```

## Règles appliquées

Droit à l'indemnité (article L1234-9 du Code du travail) : salarié en CDI comptant au moins 8 mois d'ancienneté ininterrompue, licencié pour un autre motif qu'une faute grave ou lourde.

Montant (article R1234-2) : un quart de mois de salaire par année d'ancienneté jusqu'à dix ans, un tiers de mois par année au-delà. Les années incomplètes comptent au prorata des mois complets (article R1234-1).

Salaire de référence (article R1234-4) : le plus favorable entre la moyenne des 12 derniers mois et celle des 3 derniers mois. Une prime annuelle versée pendant ces 3 mois n'est retenue que pour 3/12. Si le salarié a moins de 12 mois d'ancienneté, la moyenne porte sur tous les mois travaillés.

Ancienneté : de la date d'entrée à la fin du contrat, préavis inclus même s'il n'est pas effectué.

## Limites

Ce calcul donne le minimum légal. Beaucoup de conventions collectives prévoient une indemnité plus élevée, et c'est alors elle qui s'applique. Les périodes de suspension du contrat (certains congés, arrêts maladie) peuvent ne pas compter dans l'ancienneté ; l'outil ne les déduit pas. Les cas particuliers (temps partiel alterné avec du temps plein, inaptitude d'origine professionnelle qui double l'indemnité, salariés de particuliers employeurs) ne sont pas traités. En cas de doute, demandez à un avocat, à un défenseur syndical ou à l'inspection du travail.

## Contribuer

```bash
git clone https://github.com/TheoPSR01/indemnite-licenciement.git
cd indemnite-licenciement
pip install -e ".[dev]"
pytest
```

## Licence

MIT
