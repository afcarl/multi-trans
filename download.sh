#!/bin/bash

langs="
bn
ca
da
de
en
eo
es
fi
fr
hi
hu
id
it
jv
ko
ms
nl
nn
no
pl
pt
ru
sv
sw
tl
tr
vi
zh
"

for lang1 in $langs; do
	for lang2 in $langs; do
		if [ "$lang1" != "$lang2" ]
		then
			echo ${lang1}, ${lang2}
			wget http://opus.lingfil.uu.se/download.php?f=OpenSubtitles2016/${lang1}-${lang2}.txt.zip -P data
			unzip data/*.zip -d data/
			rm data/*.zip
			rm data/*.ids
		fi
	done
done
