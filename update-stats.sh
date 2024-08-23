#!/bin/bash

# copied from https://github.com/joapaspe/tesismometro/blob/master/client/scripts/tesismometro.sh

ROOT=/home/timoh/projects/ma
USER=timoh
TOKEN=Token 799b4f00dc601f1d4183bb0f701a1deeb78ae539
SERVER=https://trackmythesis.dynv6.net  

if [ -z "$USER" ]
then
    echo "You have to fill the user name"
    exit
fi


# Check if the specified repository path exists
if [ ! -d "$ROOT/" ]; then
    echo "Error: Repository path '$ROOT' does not exist."
    exit 1
fi

# Perform a git pull in the specified repository
echo "Updating repository at '$ROOT'..."
git -C "$ROOT/" pull

texcount -dir $ROOT/main.tex -merge > .tesiscount

words=$(grep "Words in text" .tesiscount | cut -d ' ' -f 4)
figures=$(grep "Number of floats" .tesiscount | cut -d ' ' -f 4)
inlines=$(grep "math inlines" .tesiscount | cut -d ' ' -f 5)
equations=$(grep "math displayed" .tesiscount | cut -d ' ' -f 5)
pages=$(python3 count_pdf_pages.py "$ROOT/main.pdf")

echo "words $words" 
echo "figures $figures" 
echo "inlines $inlines" 
echo "equations $equations"
echo "pages $pages"

echo "#Uploading server"
echo "curl -X POST -d "{\"username\": \"$USER\",\"words\": $words, \"figures\": $figures, \"inlines\": $inlines, \"equations\": $equations, \"pages\": $pages}" $SERVER/api/track-progress/ -H 'Authorization: Token 799b4f00dc601f1d4183bb0f701a1deeb78ae539' -o .post_out"
curl -X POST -d "{\"username\": \"$USER\",\"words\": $words, \"figures\": $figures, \"inlines\": $inlines, \"equations\": $equations, \"pages\": $pages}" $SERVER/api/track-progress/ -H 'Authorization: Token 799b4f00dc601f1d4183bb0f701a1deeb78ae539' -o .post_out