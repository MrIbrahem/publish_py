<?php
header('Content-Type: application/json; charset=utf-8');

// Check if the request is a POST request
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405); // Method Not Allowed
    echo json_encode(['error' => 'Only POST requests are allowed']);
    exit;
}

use function Publish\Endpoints\start;

include_once __DIR__ . '/include.php';
include_once __DIR__ . '/endpoints/post.php';

start($_POST);
