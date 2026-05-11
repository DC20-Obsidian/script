#!/usr/bin/env bash

endc=$'\e[1;0m'
green=$'\e[1;32m'
cyan=$'\e[1;36m'

wait_msg="Press Enter to continue"

w(){
	echo "$cyan$1$endc"
	read -p "$wait_msg"
	# clear
}

spells(){
	./main.py -t spells -p -a $@ 2>/dev/null
}

maneuvers(){
	./main.py -t maneuvers -p -a $@ 2>/dev/null
}

ancestries(){
	./main.py -t ancestries -p -a $@ 2>/dev/null
}

talents(){
	./main.py -t talents -p -a $@ 2>/dev/null
}


stats=(
	'Spell Names'
	'Count Unique Costs'
	'Count Unique Durations'
	'Count Tags'
	'All spells that have a table in them'
	'Spells mp_cost >= 2'
	'Maneuver Names'
	'Maneuvers sp_cost >= 2'
	'Ancestry Traits'
	'Talent Names'
	'Talents lv >= 3'
	'Exit'
)

options=(
	'--cycle'
	'--reverse'
	'--border=sharp'
	'--pointer='
	'--highlight-line'
	'--ghost=Search'
	'--border-label= Statistic Menu '
	'--height=~100%'
)


while true
do
	stat=$(printf "%s\n" "${stats[@]}" | fzf "${options[@]}")
	if [ $? -ne 0 ]; then
		echo 'No option selected. Exiting.'
		break
	fi
	case $stat in
		'Spell Names') spells | jq --color-output 'map(.name)' | less -R ;;
		'Count Unique Costs') spells | jq --color-output 'map(.cost) | reduce .[] as $tag ({}; .[$tag] += 1)' ; w "" ;;
		'Count Unique Durations') spells | jq --color-output 'map(.duration) | reduce .[] as $tag ({}; .[$tag] += 1)'; w "" ;;
		'Count Tags') spells | jq --color-output 'map(.tags) | flatten | reduce .[] as $tag ({}; .[$tag] += 1)' | less -R ;;
		'All spells that have a table in them') spells -r | jq 'map(select(.frags | any(.font == "f22")) | .name)'; w "" ;;
		'Spells mp_cost >= 2') spells | jq 'map(select(.mp_cost >= 2) | .name )'; w "" ;;
		'Maneuver Names') maneuvers | jq 'map(.name)'; w "" ;;
		'Maneuvers sp_cost >= 2') maneuvers | jq 'map(select(.sp_cost >= 2) | .name )'; w "" ;;
		'Ancestry Traits') ancestries | jq 'INDEX(.name) | map_values(.traits | length)'; w "" ;;
		'Talent Names') talents | jq 'map(.name)'; w "" ;;
		'Talents lv >= 3') talents | jq 'map(select(.level >= 3) | .name )'; w "" ;;
		'Exit') break ;;
		*) echo "Unknown Option: \"$stat\"" ;;
	esac
done

echo "Done"
