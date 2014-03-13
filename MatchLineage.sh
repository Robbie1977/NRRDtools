#!/bin/bash
# Example script for use of MatchIndex.py
for file in ./*SG-aligned.nrrd
do
    python ~/GIT/NRRDtools/MatchIndex.py ~/BTSync/LineageIndex.nrrd 200 ${file} ~/BTSync/LineageScanResults.csv
done
    