<?php 
        header('Access-Control-Allow-Origin: *');
	$fn = "../USERdataFOLDERwithAverySECRETname/".$_POST['str'];
	mkdir($fn);
	mkdir($fn."InCircles");
	mkdir($fn."privacy");
	mkdir($fn."snaplocations");
	mkdir($fn."snapshots");
	mkdir($fn."snapsounds");
	mkdir($fn."models");
	mkdir($fn."snapskeletons");
	echo $fn;
?>
