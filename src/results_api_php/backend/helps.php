<?php

namespace Results\ResultsHelps;

use function Results\GetCats\get_mdwiki_cat_members;

function make_mdwiki_cat_url($category, $name = null)
{
    if (empty($category)) return $category;

    $new_cat = str_replace('Category:', '', $category);

    $display_name = $name ? $name : $new_cat;

    $encoded_category = rawurlencode(str_replace(' ', '_', $new_cat));

    return "<a target='_blank' href='https://mdwiki.org/wiki/Category:$encoded_category'>$display_name</a>";
}

function filter_items_missing_cat2($items_missing, $cat2, $depth)
{

    // $cat2_members = get_mdwiki_cat_members($cat2, $use_cache = true, $depth = $depth, $camp = $camp);

    $cat2_members = get_mdwiki_cat_members($cat2, $depth, true);

    $new_missing = array_intersect($items_missing, $cat2_members);

    $new_missing = array_values($new_missing);

    return $new_missing;
}

function create_summary($code, $cat, $len_inprocess, $len_missing, $len_of_exists_pages)
{

    $len_of_all = $len_of_exists_pages + $len_missing + $len_inprocess;

    // Prepare category URL
    $caturl = make_mdwiki_cat_url($cat, "Category");

    // Generate summary message
    $summary = "Found $len_of_all pages in $caturl, $len_of_exists_pages exists, and $len_missing missing in (<a href='https://$code.wikipedia.org' target='_blank'>$code</a>), $len_inprocess In process.";

    return $summary;
}
