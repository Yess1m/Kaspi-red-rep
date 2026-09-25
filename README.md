# Replication package: Consumer Credit and the Kaspi Red Rollout in Kazakhstan

This package rebuilds both panels from the raw public files and reproduces every estimate, table and figure in the paper (version v8, 25 September 2026). The numerical authority for the paper is the results ledger (ledger v7, including amendments M10 and M11).

## Layout

- `raw/` Raw files as downloaded. National Bank of Kazakhstan monthly regional tables of consumer-purpose loans issued (`потребрегионывыдача2015рус1.xls` to `...2019рус.xls`) and end-of-period balances (`остаткипотребрегионы2015рус.xls` to `...2019рус.xls`). Bureau of National Statistics quarterly bulletins "Расходы и доходы домашних хозяйств Республики Казахстан", one folder or file per quarter, 2015Q1 to 2019Q4 (table 1.1).
- `code/` All scripts. Run every script from inside `code/`; outputs are written to `code/`.
- `patches/` A two-line compatibility patch for honestdid 0.1.1 under NumPy 2.
- `requirements.txt` Package versions used.

## Sources

- National Bank of Kazakhstan: https://nationalbank.kz/ru/news/loans-to-economy-from-second-tier-banks (archived by year).
- Bureau of National Statistics (formerly Committee on Statistics, Ministry of National Economy): https://stat.gov.kz/ru/industries/labor-and-income/stat-life/publications/
- Launch dates: see Table 1 and the Data sources list in the paper.

## Run order

1. `python build_panel.py` builds `lending_full.csv`, `balances_full.csv` and `lending_specA.csv` (fifteen regions plus South Kazakhstan) from `../raw/`. Values are in thousands of tenge; 2019 tables published in millions are rescaled.
2. `python build_hh.py` builds `hh_repayment_panel.csv` from the BNS bulletins in `../raw/` (column "погашение кредитов и долгов", all households and urban).
3. `python run_new.py` lending rows: primary CS estimate, December 2017 window, date checks, leave-one-out, samples, trends, balances, Almaty and Astana diagnostics. Writes `new_rows_lending.csv`, `loo.json`.
4. `python run_hh_v5.py` household rows and household diagnostics. Writes `v5_rows_hh.csv`, `v5_hh_diagnostics.csv`.
5. `python run_es_v6.py` fixed effects event study (Table 4, Panel A) and F tests. Writes `es_twfe_window.csv`, `es_ftests.json`.
6. `python ri_twfe.py`, `python ri_cs.py 1000`, `python wild_boot.py` randomization inference and wild cluster bootstrap (Table C1). `ri_cs.py` takes about 20 minutes on two cores.
7. `python seedcheck.py` bootstrap-seed check for the urban households excluding Mangistau row.
8. `python task1_cs_es.py` then `python task1_bins.py` Callaway and Sant'Anna event study with a universal base period (Table 4, Panel B).
9. `python task2_run.py TWFE`, `python task2_run.py CS`, `python task2_run.py TWFE_t14scaled` Rambachan and Roth sensitivity (Table 5). About 25 minutes each.
10. `python task3_step.py` cohort decomposition of the pre-launch step; `python task4_share.py` Almaty share series (descriptive).
11. `python desc_v8.py` Table 2; `python figs_v8.py` Figures 1 and 2; `python fig1.py` Figure 3 (event study).

Every bootstrap and permutation exercise uses seed 20260924. Treatment dates are set in `common.py` (`NEW`); Kyzylorda is coded to April 2018.

## Checks

After step 3 the primary estimate should read 0.0028 (SE 0.0181, 95% CI [-0.0327, +0.0382]) and the gate row (fixed effects to December 2017) 0.0056 (SE 0.0183). After step 4 the primary household estimate should read 0.2343 (SE 0.1737). These were reproduced from the raw files when the package was assembled.

## Notes

- honestdid 0.1.1 is an unofficial Python translation of the authors' R package HonestDiD. Two lines call float() on one-element arrays, which NumPy 2 rejects; `patches/honestdid_0.1.1_numpy2.diff` replaces them with .item(). The change does not alter the computation.
- The Callaway and Sant'Anna rows use csdid 0.4.2 (multiplier bootstrap, 20,000 draws); intervals use the package's 1.96 critical value.
