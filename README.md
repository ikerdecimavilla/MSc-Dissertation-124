# MSc Dissertation — Machine Learning for Flexural Buckling of Ramberg–Osgood Struts

Machine-learning study of the critical flexural (global) buckling load of stainless steel struts where the stress–strain behaviour follows the Ramberg–Osgood law. The work extends the analytical framework of Köllner, Gardner & Wadee (2023).

- **Programme:** MSc Advanced Structural Engineering, Imperial College London
- **Supervisors:** Prof. Anton Köllner & Prof. Ahmer Wadee
- **Scope:** global (flexural) buckling only — local buckling is explicitly out of scope

---

## 1. What the project is

The dissertation builds a two-stage, physics-informed machine-learning framework on top of the Köllner–Gardner–Wadee (KGW) analytical solution:

- **Stage 1 — Direct prediction.** Predict the critical flexural buckling load from material and geometric inputs using ML.
- **Stage 2 — Physics-informed correction (the core contribution).** Extend the correction
  factor beta from a univariate function of slenderness into a multivariate function of the physical imperfection drivers where mechanics stay central.

---

## 2. Current stage 

**Phase: foundational dataset construction.**

I am building the experimental dataset that the whole framework depends on, one published source at a
time. The data-handling infrastructure is in place (a tiered data dictionary, a master dataset with an
agreed schema, a source log keyed to Zotero citation keys, and per-source extraction notes),
and I am now populating it source by source.

**Progress so far**

- **3 sources fully extracted:** `afshan2013`, `behzadi2021`, `theofanous2009`
  (each has an extraction note in `notes/sources/`, an extracted CSV in `data/extracted/`, and its PDF
  moved into `data/pdfs/processed/`).
- **7 sources queued** in `data/pdfs/` awaiting extraction: `behzadi2023`, `behzadi2024`,
  `buchanan2018`, `huang2013`, `li2021`, `li2024`, `zhao2016`.

**Next steps**

- Continue data extraction
- Generate reusable python script that will calculate geometric properties (I,A,r,lambda,lambda_bar) for all sources and adds data to master_dataset.csv
- Write short methodlogy notebook to note down logic, decisions and implement src code
- Run light exploratory data analysis once a first clean dataset version exists.

---

## 3. Repository structure

```
MSC-DISSERTATION-124/
├── data/
│   ├── extracted/              # one clean CSV per source, as extracted from its paper
│   │   ├── afshan2013.csv
│   │   ├── behzadi2021.csv
│   │   └── theofanous2009.csv
│   ├── pdfs/                   # source PDFs (the ingestion queue)
│   │   ├── processed/
│   │   │  ├── afshan2013.pdf   # PDFs that have already been extracted
│   │   │  ├── behzadi2023.pdf
│   │   │  ├── theofanous2009.pdf        
│   │   ├── behzadi2023.pdf
│   │   ├── behzadi2024.pdf
│   │   ├── buchanan2018.pdf
│   │   ├── huang2013.pdf
│   │   ├── li2021.pdf
│   │   ├── li2024.pdf
│   │   └── zhao2016.pdf
│   ├── processed/              # cleaned / derived dataset versions, splits (later)
│   ├── data_dictionary.md      # schema: column definitions, tiers, units, flags
│   ├── master_dataset.csv      # the combined dataset (all sources, one row per specimen)
│   └── source_log.csv          # registry of every source, keyed to Zotero citation keys
├── notebooks/
│   └── 00_methodology.ipynb    # methodology narrative + reproducible steps (to be completed)
├── notes/
│   └── sources/                # per-source extraction notes (one .md per source)
│       ├── afshan2013.md
│       ├── behzadi2021.md
│       └── theofanous2009.md
├── references/
│   └── library.bib             # Zotero / Better BibTeX export (single source of truth for citations)
├── report/                     # LaTeX dissertation
├── src/                        # ingestion + analysis + ML pipeline code
├── .gitignore
├── environment.yml             # conda environment specification
└── README.md
```
