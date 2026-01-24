<?php

namespace Publish\Endpoints;

use function Publish\Helps\logger_debug;
use function Publish\AccessHelps\get_access_from_db;
use function Publish\AccessHelpsNew\get_access_from_db_new;
use function Publish\EditProcess\processEdit;
use function Publish\FilesHelps\to_do;
use function Publish\Revids\get_revid_db;
use function Publish\Revids\get_revid;
use function Publish\AddToDb\InsertPublishReports;
use function WpRefs\FixPage\DoChangesToText1;

function make_summary($revid, $sourcetitle, $to, $hashtag)
{
    return "Created by translating the page [[:mdwiki:Special:Redirect/revision/$revid|$sourcetitle]] to:$to $hashtag";
}

function formatTitle($title)
{
    $title = str_replace("_", " ", $title);
    // replace Mr. Ibrahem 1/ by Mr. Ibrahem/
    $title = str_replace("Mr. Ibrahem 1/", "Mr. Ibrahem/", $title);
    return $title;
}

function formatUser($user)
{
    $specialUsers = [
        "Mr. Ibrahem 1" => "Mr. Ibrahem",
        "Admin" => "Mr. Ibrahem"
    ];
    $user = $specialUsers[$user] ?? $user;
    return str_replace("_", " ", $user);
}

function determineHashtag($title, $user)
{
    $hashtag = "#mdwikicx";

    if (strpos($title, "Mr. Ibrahem") !== false && $user == "Mr. Ibrahem") {
        $hashtag = "";
    }
    return $hashtag;
}

function handleNoAccess($user, $tab)
{
    $error = ['code' => 'noaccess', 'info' => 'noaccess'];
    // ---
    $editit = ['error' => $error, 'edit' => ['error' => $error, 'username' => $user], 'username' => $user];
    // ---
    $tab['result_to_cx'] = $editit;
    // ---
    to_do($tab, "noaccess");
    // ---
    InsertPublishReports($tab['title'], $user, $tab['lang'], $tab['sourcetitle'], "noaccess", $tab);
    // ---
    logger_debug("\n<br>");
    logger_debug("\n<br>");

    print(json_encode($editit, JSON_PRETTY_PRINT));

    // file_put_contents(__DIR__ . '/editit.json', json_encode($editit, JSON_PRETTY_PRINT));
}


function executeStartProcess($request, $user, $access, $tab)
{
    $text = $request['text'] ?? '';
    // ---
    // $summary = $request['summary'] ?? '';
    // ---
    $revid = get_revid($tab['sourcetitle']);
    // ---
    if (empty($revid)) $revid = get_revid_db($tab['sourcetitle']);
    // ---
    if (empty($revid)) {
        $tab['empty revid'] = 'Can not get revid from all_pages_revids.json';
        $revid = $request['revid'] ?? $request['revision'] ?? '';
    }
    // ---
    $tab['revid'] = $revid;
    // ---
    $hashtag = determineHashtag($tab['title'], $user);
    // ---
    $tab['summary'] = make_summary($revid, $tab['sourcetitle'], $tab['lang'], $hashtag);
    // ---
    // file_put_contents(__DIR__ . '/post.log', print_r(getallheaders(), true));
    // ---
    $newtext = DoChangesToText1($tab['sourcetitle'], $tab['title'], $text, $tab['lang'], $revid);
    // ---
    if (!empty($newtext)) {
        // ---
        $tab['fix_refs'] = ($newtext != $text) ? 'yes' : 'no';
        // ---
        $text = $newtext;
    }
    // ---
    $editit = processEdit($request, $access, $text, $user, $tab);
    // ---
    logger_debug("\n<br>");
    logger_debug("\n<br>");
    // ---
    print(json_encode($editit, JSON_PRETTY_PRINT));
}


function start($request)
{
    // ---
    $user = formatUser($request['user'] ?? '');
    $title = formatTitle($request['title'] ?? '');
    // ---
    $tab = [
        'title' => $title,
        'summary' => "",
        'lang' => $request['target'] ?? '',
        'user' => $user,
        'campaign' => $request['campaign'] ?? '',
        'result' => "",
        'edit' => [],
        'sourcetitle' => $request['sourcetitle'] ?? ''
    ];
    // ---
    $access = get_access_from_db_new($user);
    // ---
    if ($access === null) {
        $access = get_access_from_db($user);
    }
    // ---
    if ($access == null) {
        handleNoAccess($user, $tab);
    } else {
        executeStartProcess($request, $user, $access, $tab);
    }
}
