# Ramberg–Osgood Buckling: ML-Assisted Stability Prediction

MSc Advanced Structural Engineering dissertation, Imperial College London.

This project extends Köllner, Gardner & Wadee (2023) by applying machine 
learning to predict global flexural buckling loads of Ramberg–Osgood material 
columns (stainless steel, aluminium alloys, cold-formed steel).

Stage 1 predicts critical buckling load directly from material and geometric 
inputs. Stage 2 learns a physics-informed correction factor β fed back into 
the governing equation to account for real-world imperfections.

## Repository structure

    data/raw/            one CSV per source, as reported
    data/processed/      harmonised master dataset
    data/source_log.csv  provenance record for every source
    notebooks/           data extraction, EDA, modelling
    report/              LaTeX dissertation
    references/          Zotero BibTeX export
    notes/               per-source reading notes and decisions log

## Setup

    conda env create -f environment.yml
    conda activate stainless-steel
    jupyter lab

## Data

See `data/data_dictionary.md` for column definitions and 
`data/source_log.csv` for the provenance record of every source used.