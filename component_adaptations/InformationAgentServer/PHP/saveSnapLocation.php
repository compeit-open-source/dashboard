<?php 
        header('Access-Control-Allow-Origin: *');
	$fn = "../USERdataFOLDERwithAverySECRETname/".$_POST['str'].'locations.txt';
	$fp = fopen($fn, 'a');
	fwrite($fp,$_POST['loc']."\n");
	fclose($fp);
	echo "success";
?>
