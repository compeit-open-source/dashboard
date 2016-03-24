<?php
session_start();
header('Access-Control-Allow-Origin: *');
echo "{ username: $_SESSION[username],
		room: $_SESSION[lair], 
		friends: '$_SESSION[friends]',
		clientIP: $_SERVER[REMOTE_ADDR],
		clientPort: $_SERVER[REMOTE_PORT]
		}"
?>
