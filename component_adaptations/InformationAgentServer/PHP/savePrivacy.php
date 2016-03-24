<?php 
        header('Access-Control-Allow-Origin: *');
	$fn = "../USERdataFOLDERwithAverySECRETname/".$_POST['str'].'privacy.txt';
	$fp = fopen($fn, 'wb');
	fwrite($fp, $_POST['data']);
	fclose($fp);
	echo $fn;
?>
