<?php
$fn = "../USERdataFOLDERwithAverySECRETname/".$_POST['str'].'inCircleList.txt';
        header('Access-Control-Allow-Origin: *');
	$fp = fopen($fn, "r") or die("{}");
	$data = fgets($fp);
	fclose($fp);
	echo $data;
?>
