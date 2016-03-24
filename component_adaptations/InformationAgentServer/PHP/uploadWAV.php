<?php
        header('Access-Control-Allow-Origin: *');
	$cad =  $_POST['data'];
	$stringas = explode(":",$cad);
	$type = explode(";", $stringas[1]);
	$base = explode(",", $type[1]);
	$base64 = $base[1];
	$fn = "../USERdataFOLDERwithAverySECRETname/".$_POST['str'].'uploaded_audio.wav';
	$fh = fopen($fn, 'w');
	fwrite($fh, base64_decode($base64));
	fclose($fh);
	echo "snapsounds saved as: ".$fn;
?>

