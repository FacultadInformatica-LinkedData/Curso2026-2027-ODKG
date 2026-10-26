head -n 1 2019-aparcamientos-ocupa-historico.csv > 2019-2026-aparcamientos-ocupa-historico.csv

for f in [0-9][0-9][0-9][0-9]-aparcamientos-ocupa-historico.csv; do
    tail -n +2 "$f" >> 2019-2026-aparcamientos-ocupa-historico.csv
done