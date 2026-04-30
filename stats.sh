#!/bin/bash

endc=$'\e[1;0m'
green=$'\e[1;32m'
cyan=$'\e[1;36m'

wait_msg="Press Enter to continue"

w(){
	echo "$cyan$1$endc"
	read -p "$wait_msg"
	clear
}

# Enables alternet buffer (https://gist.github.com/ConnerWill/d4b6c776b509add763e17f9f113fd25b#common-private-modes)
echo $'\e[?1049h'

spells(){
	./parse_spells.py -p -a $@
}

spells | jq 'map(.name)'
w "Spell Names"

spells | jq 'map(.cost) | reduce .[] as $tag ({}; .[$tag] += 1)'
w "Count unique costs"

spells | jq 'map(.duration) | reduce .[] as $tag ({}; .[$tag] += 1)'
w "Count unique durations"

spells | jq 'map(.tags) | flatten | reduce .[] as $tag ({}; .[$tag] += 1)'
w "Count tags"

spells -r | jq 'map(select(.items | any(.font == "f22")) | .name)'
w "List all spells that have a table in them"

# Restores the original buffer
echo $'\e[?1049l'
