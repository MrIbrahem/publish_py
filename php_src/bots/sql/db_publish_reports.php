<?php

namespace Publish\AddToDb;
/*

*/

use function Publish\MdwikiSql\execute_query;

function InsertPublishReports($title, $user, $lang, $sourcetitle, $result, $data)
{
    $query = "INSERT INTO publish_reports (`date`, `title`, `user`, `lang`, `sourcetitle`, `result`, `data`) VALUES (NOW(), ?, ?, ?, ?, ?, ?)";
    $report_data = json_encode($data);
    // remove .json from $result
    $result = str_replace(".json", "", $result);
    $params = [$title, $user, $lang, $sourcetitle, $result, $report_data];
    execute_query($query, $params, "publish_reports");
}
