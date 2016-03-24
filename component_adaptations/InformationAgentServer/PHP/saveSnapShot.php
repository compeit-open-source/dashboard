<?php 
        header('Access-Control-Allow-Origin: *');
	$data = substr($_POST['img'], strpos($_POST['img'], ",") + 1);
	$decodedData = base64_decode($data);
	$date = date_create();
	$fn = "../USERdataFOLDERwithAverySECRETname/".$_POST['str'].date_timestamp_get($date).'.jpg';
	$fp = fopen($fn, 'wb');
	fwrite($fp, $decodedData);
	fclose($fp);
	echo $fn;
?>
