#!/bin/bash


echo "Delete old .idx files"
rm *.idx

echo "Initialize new .idx files"
python3 dbc.py

echo "Populate .idx files"
echo "em.idx"
sort -u emails.txt | perl break.pl | db_load -c duplicates=1 -T -t btree em.idx

echo "da.idx"
sort -u dates.txt | perl break.pl | db_load -c duplicates=1 -T -t btree da.idx

echo "te.idx"
sort -u terms.txt | perl break.pl | db_load -c duplicates=1 -T -t btree te.idx

echo "re.idx"
sort -u recs.txt | perl break.pl | db_load -c duplicates=1 -T -t hash re.idx
