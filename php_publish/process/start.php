<?php

namespace Publish\Start;

use function Publish\EditProcess\text_changes;
use function Publish\AccessHelps\get_user_access;
use function Publish\EditProcess\processEdit;
use function Publish\FilesHelps\to_do;
use function Publish\AddToDb\InsertPublishReports;
use function Publish\StartUtils\make_summary;
use function Publish\StartUtils\formatTitle;
use function Publish\StartUtils\formatUser;
use function Publish\StartUtils\determineHashtag;

use function Publish\CurlRequests\get_url_curl;

function get_revid_db($sourcetitle)
{
    $params = [
        "get" => "revids",
        "title" => $sourcetitle
    ];
    if (($_SERVER['SERVER_NAME'] ?? "localhost") == "localhost") {
        $url = "http://localhost:9001/api?" . http_build_query($params, '', '&', PHP_QUERY_RFC3986);
        $json = file_get_contents($url);
    } else {
        $url = "https://mdwiki.toolforge.org/api.php?" . http_build_query($params, '', '&', PHP_QUERY_RFC3986);
        $json = get_url_curl($url);
    }
    $json = json_decode($json, true);
    $results = array_column($json["results"] ?? [], "revid", "title");
    $revid = $results[$sourcetitle] ?? "";
    return $revid;
}

function get_revid($sourcetitle)
{
    // read all_pages_revids.json file
    $revids_file_path = getenv("ALL_PAGES_REVIDS_PATH") ?: ($_ENV['ALL_PAGES_REVIDS_PATH'] ?? "");
    if (empty($revids_file_path)) {
        error_log("ALL_PAGES_REVIDS_PATH is not set");
        $revids_file_path = __DIR__ . '/all_pages_revids.json';
    };
    if (!file_exists($revids_file_path)) {
        error_log("all_pages_revids.json file not found");
        return "";
    }
    try {
        $json = json_decode(file_get_contents($revids_file_path), true);
        $revid = $json[$sourcetitle] ?? "";
        return $revid;
    } catch (\Exception $e) {
        error_log($e->getMessage());
    }
    return "";
}

function load_words_table()
{

    $word_file = __DIR__ . "/../../td/Tables/jsons/words.json";
    if (!file_exists($word_file)) {
        $word_file = "I:/mdwiki/mdwiki/public_html/td/Tables/jsons/words.json";
    }
    try {
        $file = file_get_contents($word_file);
        // $file = file_get_contents("https://mdwiki.toolforge.org/td/Tables/jsons/words.json");
        $Words_table = json_decode($file, true);
    } catch (\Exception $e) {
        $Words_table = [];
    }
    return $Words_table;
}

function handleNoAccess($user, $tab, $rand_id)
{
    $error = ['code' => 'noaccess', 'info' => 'noaccess'];
    $editit = ['error' => $error, 'edit' => ['error' => $error, 'username' => $user], 'username' => $user];
    $tab['result_to_cx'] = $editit;

    to_do($tab, "noaccess", $rand_id);
    InsertPublishReports($tab['title'], $user, $tab['lang'], $tab['sourcetitle'], "noaccess", $tab);

    error_log("\n<br>");
    error_log("\n<br>");

    print(json_encode($editit, JSON_PRETTY_PRINT));
}

function start($request)
{
    $rand_id = time() .  "-" . bin2hex(random_bytes(6));
    $user = formatUser($request['user'] ?? '');
    $title = formatTitle($request['title'] ?? '');
    $tab = [
        'title' => $title,
        'summary' => "",
        'lang' => $request['target'] ?? '',
        'user' => $user,
        'campaign' => $request['campaign'] ?? '',
        'result' => "",
        'words' => "",
        'edit' => [],
        'sourcetitle' => $request['sourcetitle'] ?? ''
    ];
    $access = get_user_access($user);

    if (empty($access)) {
        handleNoAccess($user, $tab, $rand_id);
        return;
    }

    $Words_table = load_words_table();
    $tab['words'] = $Words_table[$title] ?? 0;

    $tr_type = $request['tr_type'] ?? 'lead';

    $text = $request['text'] ?? '';
    $revid = get_revid($tab['sourcetitle']);
    if (empty($revid)) $revid = get_revid_db($tab['sourcetitle']);

    if (empty($revid)) {
        $tab['empty revid'] = 'Can not get revid from all_pages_revids.json';
        $revid = $request['revid'] ?? $request['revision'] ?? '';
    }

    $tab['revid'] = $revid;

    $hashtag = determineHashtag($tab['title'], $user);
    $tab['summary'] = make_summary($revid, $tab['sourcetitle'], $tab['lang'], $hashtag);


    $newtext = text_changes($tab['sourcetitle'], $tab['title'], $text, $tab['lang'], $revid);

    if (!empty($newtext)) {
        $tab['fix_refs'] = ($newtext != $text) ? 'yes' : 'no';
        $text = $newtext;
    }

    $edit_result = processEdit($request, $access, $text, $user, $tab, $rand_id, $tr_type);

    error_log("\n<br>");
    error_log("\n<br>");

    print(json_encode($edit_result, JSON_PRETTY_PRINT));
}
