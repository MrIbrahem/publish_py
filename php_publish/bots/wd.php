<?php

namespace Publish\WD;

use function Publish\Sql\GetQidForMdtitle;
use function Publish\MediaWikiClient\post_params;
use function Publish\AccessHelps\get_user_access;

function getAccessCredentials($user, $access_key, $access_secret)
{
    if ($access_key && $access_secret) {
        return [$access_key, $access_secret];
    }

    $access = get_user_access($user);

    if (empty($access)) {
        error_log("user = $user");
        error_log("access == null");
        return null;
    }

    $access_key = $access['access_key'];
    $access_secret = $access['access_secret'];

    return [$access_key, $access_secret];
}

function LinkIt($apiParams, $access_key, $access_secret)
{
    $wikidata_domain = getenv('WIKIDATA_DOMAIN') ?: ($_ENV['WIKIDATA_DOMAIN'] ?? 'www.wikidata.org');
    $https_domain = "https://$wikidata_domain";

    $response = post_params($apiParams, $https_domain, $access_key, $access_secret);
    $Result = json_decode($response, true);
    if (!is_array($Result)) {
        $Result = [];
    }
    if (isset($Result['error'])) {
        error_log("post_params: Result->error: " . json_encode($Result['error']));
    }

    if (empty($Result)) {
        error_log("post_params: Error: " . json_last_error() . " " . json_last_error_msg());
        error_log("response:");
        error_log($response);
    }
    return $Result;
}
function LinkToWikidata($sourcetitle, $lang, $user, $targettitle, $access_key, $access_secret)
{
    $qids = GetQidForMdtitle($sourcetitle);
    $qid = $qids[0]['qid'] ?? '';

    $credentials = getAccessCredentials($user, $access_key, $access_secret);
    if ($credentials === null) {
        return ['error' => 'Access credentials not found for user: ' . $user, 'qid' => $qid];
    }
    list($access_key, $access_secret) = $credentials;

    $apiParams = [
        "action" => "wbsetsitelink",
        "linktitle" => $targettitle,
        "linksite" => "{$lang}wiki",
    ];
    if (!empty($qid)) {
        $apiParams["id"] = $qid;
    } else {
        $apiParams["title"] = $sourcetitle;
        $apiParams["site"] = "enwiki";
    }

    $link_result = LinkIt($apiParams, $access_key, $access_secret) ?? [];

    $link_result["qid"] = $qid;

    if (isset($link_result['success']) && $link_result['success']) {
        error_log("success: true");
        return ['result' => "success", 'qid' => $qid];
    }

    return $link_result;
}
