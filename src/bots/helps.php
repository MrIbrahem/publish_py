<?php

namespace Publish\Helps;
/*
Usage:
use function Publish\Helps\logger_debug;
use function Publish\Helps\encode_value;
use function Publish\Helps\decode_value;
*/

use Defuse\Crypto\Crypto;

function logger_debug($s)
{
    //---
    if (!isset($_REQUEST['test'])) return;
    //---
    if (gettype($s) == 'string') {
        echo "\n<br>\n$s";
    } else {
        echo "\n<br>\n";
        print_r($s);
    }
}

function decode_value($value, $key_type = "cookie")
{
    global $cookie_key, $decrypt_key;
    // ---
    if (empty(trim($value))) {
        return "";
    }
    // ---
    $use_key = ($key_type == "decrypt") ? $decrypt_key : $cookie_key;
    // ---
    try {
        $value = Crypto::decrypt($value, $use_key);
    } catch (\Exception $e) {
        $value = "";
    }
    return $value;
}

function encode_value($value, $key_type = "cookie")
{
    global $cookie_key, $decrypt_key;
    // ---
    $use_key = ($key_type == "decrypt") ? $decrypt_key : $cookie_key;
    // ---
    if (empty(trim($value))) {
        return "";
    }
    // ---
    try {
        $value = Crypto::encrypt($value, $use_key);
    } catch (\Exception $e) {
        $value = "";
    };
    return $value;
}
