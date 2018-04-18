if [ ! -z "$HOME" ]
then
	echo "$HOME"
elif [[ ! -z "$USERPROFILE" ]]
then
	echo "$USERPROFILE"
elif [[ ! -z "$HOMEDRIVE" && ! -z "$HOMEPATH" ]]
then
	echo "$HOMEDRIVE$HOMEPATH"
elif [[ ! -z "$USER" ]]
then
	echo $(eval echo ~$USER)
elif [[ ! -z "$(logname 2> /dev/null)" ]]
then
	echo $(eval echo ~$(logname 2> /dev/null))
elif [[ $(id -un) ]]
then
	echo $(eval echo ~$(id -un 2> /dev/null))
else
	echo "None"
fi
