<?php

namespace Results\GetResults;



use function Results\ResultsHelps\filter_items_missing_cat2;
use function Results\ResultsHelps\create_summary;
use function Results\GetCats\get_mdwiki_cat_members;

use function APICalls\MdwikiSql\fetch_query;

function super_function(array $api_params, array $sql_params, string $sql_query, $table_name = null, $no_refind = false): array
{
    return fetch_query($sql_query, $sql_params, $table_name);
}

function get_cat_exists_and_missing_new($exists_via_td, $cat, $depth, $code, $use_cache = true): array
{

    if (empty($exists_via_td)) {
        $exists_via_td = get_lang_pages_by_cat($code, $cat);
        $exists_via_td = array_column($exists_via_td, null, "title");
    }

    // Fetch category members
    $members = get_mdwiki_cat_members($cat, $depth, $use_cache);



    // pages that exist in $exists and $members

    $exists = array_filter($exists_via_td, function ($item) use ($members) {
        return in_array($item['title'], $members);
    });

    $func = function ($item) {
        return [
            "qid" => $item["qid"] ?? "",
            "title" => $item["title"] ?? "",
            "target" => $item["target"] ?? "",
            "via" => "td",
            "pupdate" => $item["pupdate"] ?? "",
            "user" => $item["user"] ?? ""
        ];
    };

    $exists = array_map($func, $exists);

    // Find missing members
    $missing = array_diff($members, array_keys($exists));

    $missing = array_values(array_unique($missing));

    //
    return [$exists, $missing];
}

function get_lang_pages_by_cat($lang, $cat)
{

    // http://localhost:9001/api.php?get=pages&lang=ar&cat=RTT
    static $data = [];

    if (!empty($data[$lang . $cat] ?? [])) {
        return $data[$lang . $cat];
    }

    $api_params = ['get' => 'pages', 'lang' => $lang, 'cat' => $cat];

    $query = "select * from pages p where p.lang = ? and p.cat = ?";
    $params = [$lang, $cat];

    $u_data = super_function($api_params, $params, $query);

    $data[$lang . $cat] = $u_data;

    return $u_data;
}

function exists_by_qids_query($lang)
{

    // http://localhost:9001/api.php?get=exists_by_qids&lang=ar&target=not_empty

    static $data2 = [];

    if (!empty($data2[$lang] ?? [])) {
        return $data2[$lang];
    }

    $api_params = ['get' => 'exists_by_qids', 'lang' => $lang, 'target' => 'not_empty'];

    $query = <<<SQL
        SELECT a.qid, a.title, a.category, t.code, t.target
            FROM all_qids_titles a
            JOIN all_qids_exists t
            ON t.qid = a.qid
        WHERE t.code = ?

        AND (t.target != '' AND t.target IS NOT NULL)
    SQL;

    $params = [$lang];

    $u_data = super_function($api_params, $params, $query, "all_qids_titles");

    $data2[$lang] = $u_data;

    return $u_data;
}

function get_lang_in_process($code): array
{

    static $cache = [];

    if (!empty($cache[$code] ?? [])) return $cache[$code];

    $query = "select * from in_process where lang = ?";

    $api_params = ['get' => 'in_process', 'lang' => $code];

    $params = [$code];

    $data = super_function($api_params, $params, $query, "in_process");

    $cache[$code] = $data;

    return $data;
}

function exists_expends($items_missing, $exists_targets_before)
{




    // { "qid": "Q133005500", "title": "Video:Abdominal thrusts", "category": "RTTVideo", "code": "ar", "target": "ويكيبيديا:فيديوويكي\/ضغطات البطن" }

    $items_exists = [];
    $missing_new = [];

    foreach ($items_missing as $title) {

        $before_link = $exists_targets_before[$title] ?? [];
        $target = $before_link['target'] ?? "";

        if ($target) {

            $items_exists[$title] = [
                "qid" => $before_link['qid'] ?? "",
                "title" => $before_link['title'] ?? "",
                "target" => $target,
                "via" => "before"
            ];
        } else {
            $missing_new[] = $title;
        }
    }




    return $items_exists;
}

function getinprocess_n($missing, $code)
{
    $res = get_lang_in_process($code);

    $titles = [];

    foreach ($res as $t) {
        if (in_array($t['title'], $missing)) {
            $titles[$t['title']] = $t;
        }
    }

    return $titles;
}

function get_results_new($cat, $camp, $depth, $code, $filter_sparql, $cat2): array
{
    // Get existing and missing pages

    $exists_via_td = get_lang_pages_by_cat($code, $cat);
    $exists_via_td = array_column($exists_via_td, null, "title");



    [$items_exists, $items_missing] = get_cat_exists_and_missing_new($exists_via_td, $cat, $depth, $code, true);

    $exists_targets_before = exists_by_qids_query($code);
    $exists_targets_before = array_column($exists_targets_before, null, 'title');



    $exists_1 = exists_expends($items_missing, $exists_targets_before);

    if ($exists_1) {

        $items_missing = array_diff($items_missing, array_keys($exists_1));
        $items_exists = array_merge($items_exists, $exists_1);
    }


    // Check for a secondary category

    if (!empty($cat2) && $cat2 !== $cat) {
        $items_missing = filter_items_missing_cat2($items_missing, $cat2, $depth);
    }

    $len_of_exists_pages = count($items_exists);


    // Remove duplicates from missing items
    $missing = array_values(array_unique($items_missing));

    // Get in-process items
    $inprocess = getinprocess_n($missing, $code);
    $len_inprocess = count($inprocess);

    // Remove in-process items from missing list
    if ($len_inprocess > 0) {
        $missing = array_diff($missing, array_column($inprocess, 'title'));
        $missing = array_values($missing);
    }

    $summary = create_summary($code, $cat, count($inprocess), count($missing), $len_of_exists_pages);

    // sort $items_exists by keys
    ksort($items_exists);

    return [
        "inprocess" => $inprocess,
        "exists" => $items_exists,
        "missing" => $missing,
        "ix" => $summary,
    ];
}
