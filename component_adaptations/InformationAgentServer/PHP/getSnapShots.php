<?php
header('Access-Control-Allow-Origin: *');
$str = "../USERdataFOLDERwithAverySECRETname/".$_POST['str'];
echo json_encode( glob($str."*.jpg") );
?>
