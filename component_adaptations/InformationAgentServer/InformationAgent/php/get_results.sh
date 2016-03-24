#!/user/bin/sh
eval `awk 'NR==3{print "set x="$2}' results_uploaded_audio.res
echo $x