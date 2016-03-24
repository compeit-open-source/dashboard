<?php
        header('Access-Control-Allow-Origin: *');
	$str = "../USERdataFOLDERwithAverySECRETname/".$_POST['str']."locations.txt";
	$handle = fopen($str, "r") or die("Unable to open file!");;
	$valArray = array();
	while (!feof($handle) ) $valArray[] = json_decode(fgets($handle));
	echo json_encode($valArray);
?>
