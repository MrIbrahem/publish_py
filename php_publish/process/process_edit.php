<?php

namespace Publish\EditProcess;

use function Publish\AddToDb\InsertPublishReports;
use function Publish\WD\LinkToWikidata;
use function Publish\FilesHelps\to_do;
use function Publish\AccessHelps\get_user_access;
use function Publish\EditProcess\add_to_db;
use function Publish\StartUtils\get_errors_file;
use function Publish\StartUtils\prepareApiParams;
use function Publish\CurlRequests\get_url_curl;
use function Publish\MediaWikiClient\get_client;
use function Publish\MediaWikiClient\getAccessToken;
use function Publish\MediaWikiClient\get_edits_token;

function publish_do_edit($apiParams, $wiki, $access)
{
    $client = get_client("$wiki.wikipedia.org");

    $apiUrl = "https://$wiki.wikipedia.org/w/api.php";

    $accessToken = getAccessToken($access["access_key"], $access["access_secret"]);

    $editToken = get_edits_token($client, $accessToken, $apiUrl);

    $apiParams['token'] = $editToken;

    $req = $client->makeOAuthCall(
        $accessToken,
        $apiUrl,
        true,
        $apiParams
    );
    $editResult = json_decode($req, true);
    return $editResult;
}

function GetTitleInfo($targettitle, $lang)
{
    $params = [
        "action" => "query",
        "format" => "json",
        "titles" => $targettitle,
        "utf8" => 1,
        "formatversion" => "2"
    ];
    $url = "https://$lang.wikipedia.org/w/api.php" . "?" . http_build_query($params, '', '&', PHP_QUERY_RFC3986);
    error_log("GetTitleInfo url: $url");
    try {
        $result = get_url_curl($url);
        error_log("GetTitleInfo result: $result");
        $result = json_decode($result, true);
        // { "query": { "pages": [ { "pageid": 5049507, "ns": 2, "title": "利用者:Mr. Ibrahem/オランザピン/サミドルファン" } ] } }
        $result = $result['query']['pages'][0];
    } catch (\Exception $e) {
        error_log("GetTitleInfo: $e");
        $result = null;
    }
    return $result;
}

function shouldAddedToWikidata($lang, $title)
{
    $page_informations = GetTitleInfo($title, $lang);
    if (!$page_informations) {
        return false;
    }
    $page_namespace = $page_informations["ns"] ?? null;
    if ($page_namespace == 2) {
        // skip link to wd for user pages
        return false;
    }
    return true;
}

function retryWithFallbackUser($sourcetitle, $lang, $title, $user)
{
    $LinkTowd = [];
    error_log("get_csrftoken failed for user: $user, retrying with Mr. Ibrahem");

    // Retry with "Mr. Ibrahem" credentials - get fresh credentials from database
    $fallback_access = get_user_access('Mr. Ibrahem');

    if (!empty($fallback_access)) {
        $fallback_access_key = $fallback_access['access_key'];
        $fallback_access_secret = $fallback_access['access_secret'];

        $LinkTowd = LinkToWikidata($sourcetitle, $lang, 'Mr. Ibrahem', $title, $fallback_access_key, $fallback_access_secret) ?? [];

        // Add a note that fallback was used
        if (!isset($LinkTowd['error'])) {
            $LinkTowd['fallback_user'] = 'Mr. Ibrahem';
            $LinkTowd['original_user'] = $user;
            error_log("Successfully linked using Mr. Ibrahem fallback credentials");
        }
    }
    return $LinkTowd;
}

function handleSuccessfulEdit($sourcetitle, $lang, $user, $title, $access, $rand_id)
{
    if (!shouldAddedToWikidata($lang, $title)) {
        // skip link to wd for user pages
        return ["error" => "skip link to wd for user pages"];
    }
    $LinkTowd = [];
    $access_key = $access['access_key'];
    $access_secret = $access['access_secret'];

    try {
        $LinkTowd = LinkToWikidata($sourcetitle, $lang, $user, $title, $access_key, $access_secret) ?? [];
        // Check if the error is get_csrftoken failure and user is not already "Mr. Ibrahem"
        if (isset($LinkTowd['error']) && $LinkTowd['error'] == 'get_csrftoken failed' && $user !== 'Mr. Ibrahem') {
            $LinkTowd['fallback'] = retryWithFallbackUser($sourcetitle, $lang, $title, $user);
        }
        // Log errors if they still exist after retry
    } catch (\Exception $e) {
        error_log($e->getMessage());
    }
    if (isset($LinkTowd['error'])) {
        $tab3 = [
            'error' => $LinkTowd['error'],
            'qid' => $LinkTowd['qid'] ?? "",
            'title' => $title,
            'sourcetitle' => $sourcetitle,
            'fallback' => $LinkTowd['fallback'] ?? "",
            'lang' => $lang,
            'username' => $user
        ];
        // if str($LinkTowd['error']) has "Links to user pages"  then file_name='wd_user_pages' else 'wd_errors'
        $file_name = get_errors_file($LinkTowd['error'], "wd_errors");
        to_do($tab3, $file_name, $rand_id);
        // --
        InsertPublishReports($title, $user, $lang, $sourcetitle, $file_name, $tab3);
    }
    return $LinkTowd;
}

function processEdit($request, $access, $text, $user, $tab, $rand_id, $tr_type)
{
    $sourcetitle = $tab['sourcetitle'];
    $lang = $tab['lang'];
    $campaign = $tab['campaign'];
    $title = $tab['title'];
    $summary = $tab['summary'];
    $mdwiki_revid = $tab['revid'] ?? "";

    $apiParams = prepareApiParams($title, $summary, $text, $request);

    $apiParams["text"] = $text;

    $editit = publish_do_edit($apiParams, $lang, $access);

    $Success = $editit['edit']['result'] ?? '';
    $is_captcha = $editit['edit']['captcha'] ?? null;

    $tab['result'] = $Success;

    $to_do_file = "";

    $words = $tab["words"];

    if ($Success === 'Success') {
        $linktowikidata = handleSuccessfulEdit($sourcetitle, $lang, $user, $title, $access, $rand_id);
        $editit['LinkToWikidata'] = $linktowikidata;

        $to_users_table = false;
        // if $wd_result has "abusefilter-warning-39" then $to_users_table = true
        if (strpos(json_encode($linktowikidata), "abusefilter-warning-39") !== false) {
            $to_users_table = true;
        }
        $editit['sql_result'] = add_to_db($title, $lang, $user, $to_users_table, $campaign, $sourcetitle, $mdwiki_revid, $words, $tr_type);
        $to_do_file = "success";
    } else if ($is_captcha) {
        $to_do_file = "captcha";
    } else {
        $to_do_file = get_errors_file($editit, "errors");
    }
    $tab['result_to_cx'] = $editit;
    to_do($tab, $to_do_file, $rand_id);
    // --
    InsertPublishReports($title, $user, $lang, $sourcetitle, $to_do_file, $tab);
    return $editit;
}
