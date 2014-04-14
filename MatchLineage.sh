#!/bin/bash
# Example script for use of MatchIndex.py
for file in ./*SG-aligned.nrrd
do
    echo ${file}
    python ~/GIT/NRRDtools/MatchIndex.py ~/BTSync/LineageIndex.nrrd 254 ${file} ~/BTSync/LineageScanResults.csv
done
    