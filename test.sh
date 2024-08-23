#!/bin/bash

# copied from https://github.com/joapaspe/tesismometro/blob/master/client/scripts/tesismometro.sh

ROOT=/home/timoh/projects/ma/main
USER=timoh
TOKEN=Token 799b4f00dc601f1d4183bb0f701a1deeb78ae539
SERVER=https://trackmythesis.dynv6.net  

words=1
figures=1
inlines=1
equations=1
cites=1
pages=2


#curl -X POST -d '{"username": "$USER","words":$words, "figures": $figures, "inlines": $inlines, "equations": $equations, "pages": $pages, "cites": $cites}' $SERVER/api/track-progress/ -H 'Authorization: Token 799b4f00dc601f1d4183bb0f701a1deeb78ae539' -o .post_out
curl -X POST -d "{\"username\": \"$USER\",\"words\": $words, \"figures\": $figures, \"inlines\": $inlines, \"equations\": $equations, \"pages\": $pages, \"cites\": $cites}" $SERVER/api/track-progress/ -H 'Authorization: Token 799b4f00dc601f1d4183bb0f701a1deeb78ae539' -o .post_out
