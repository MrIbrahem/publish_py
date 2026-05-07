<?php
header('Content-Type: application/json; charset=UTF-8');
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$time_start = microtime(true);

use function Results\GetResults\get_results_new;

$cat   = $_GET['cat'] ?? "";
$cat2  = $_GET['cat2'] ?? "";
$camp  = $_GET['camp'] ?? "";
$depth = $_GET['depth'] ?? "1";
$code  = $_GET['code'] ?? "ar";

if (empty($cat)) {
    $cat = "RTTHearing";
}
if (empty($camp)) {
    $camp = "Hearing";
}

$results = get_results_new($cat, $camp, $depth, $code, true, $cat2);

$tab = [
    "execution_time" => (microtime(true) - $time_start),
    "results" => $results
];

echo json_encode($tab, JSON_PRETTY_PRINT);
