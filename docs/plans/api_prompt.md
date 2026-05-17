write plan at `plans/api.md` to create endpoint routes for `/api/index.php?get=publish_reports`

# releted informations:
```json
{
    "publish_reports": {
        "columns": [
            "date",
            "title",
            "user",
            "lang",
            "sourcetitle",
            "result",
            "data"
        ],
        "params": [
            {
                "name": "year",
                "column": "YEAR(date)",
                "type": "number",
                "placeholder": "year of date"
            },
            {
                "name": "month",
                "column": "MONTH(date)",
                "type": "number",
                "placeholder": "month of date"
            },
            {
                "name": "title",
                "column": "title",
                "type": "text",
                "placeholder": "Page Title"
            },
            {
                "name": "user",
                "column": "user",
                "type": "text",
                "placeholder": "user"
            },
            {
                "name": "lang",
                "column": "lang",
                "type": "text",
                "placeholder": "Language code"
            },
            {
                "name": "sourcetitle",
                "column": "sourcetitle",
                "type": "text",
                "placeholder": "sourcetitle"
            },
            {
                "name": "result",
                "column": "result",
                "type": "text",
                "placeholder": "result"
            },
            {
                "name": "select",
                "column": "select",
                "type": "text",
                "placeholder": "Select fields"
            }
        ]
    }
    }
```
----
# from php api endpoint
```php
    case 'publish_reports':
        $query = <<<SQL
            SELECT DISTINCT *
            FROM publish_reports
            SQL;
        // ---
        list($query, $params) = add_li_params($query, [], $endpoint_params);
        // ---
        break;
```        
----
# from php sql file:

```php
function add_one_param($qua, $column, $added, $tabe)
{
    // ---
    $add_str = "";
    $params = [];
    // ---
    $where_or_and = (strpos(strtoupper($qua), 'WHERE') !== false) ? ' AND ' : ' WHERE ';
    // ---
    if ($added == "not_mt" || $added == "not_empty") {
        $add_str = " $where_or_and ($column != '' AND $column IS NOT NULL) ";
        // ---
    } elseif ($added == "mt" || $added == "empty") {
        $add_str = " $where_or_and ($column = '' OR $column IS NULL) ";
        // ---
    } elseif ($added == ">0" || $added == "&#62;0") {
        $add_str = " $where_or_and $column > 0 ";
        // ---
    } elseif (($tabe['type'] ?? '') == 'array') {
        list($add_str, $params) = add_array_params($add_str, $params, $tabe['name'], $column, $where_or_and);
    } else {
        $params[] = $added;
        $add_str = " $where_or_and $column = ? ";
        // ---
        $value_can_be_null = isset($tabe['value_can_be_null']) ? $tabe['value_can_be_null'] : false;
        // ---
        if ($value_can_be_null) {
            $add_str = " $where_or_and ($column = ? OR $column IS NULL OR $column = '') ";
        }
    }
    // ---
    return [$add_str, $params];
}

function change_types($types, $endpoint_params, $ignore_params)
{
    // ---
    // $types = array_flip($types);
    // ---
    $types2 = [];
    // ---
    foreach ($types as $type) {
        $types2[$type] = ["column" => $type];
    }
    // ---value_can_be_null
    $types = $types2;
    // ---
    if (count($types) == 0 && count($endpoint_params) > 0) {
        foreach ($endpoint_params as $param) {
            // { "name": "title", "column": "w_title", "type": "text", "placeholder": "Page Title" },
            // , "no_select": true
            if (isset($param['no_select'])) continue;
            $types[$param['name']] = $param;
        }
    }
    // ---
    foreach ($ignore_params as $param) {
        if (isset($types[$param])) unset($types[$param]);
    }
    // ---
    return $types;
}
function add_array_params($qua, $params, $param = "titles", $column = "title", $where_or_and = "")
{
    // ---
    // list($query, $params) = add_array_params($query, $params, 'titles', 'title', "AND");
    // ---
    if (empty($where_or_and)) {
        $where_or_and = (strpos(strtoupper($qua), 'WHERE') !== false) ? ' AND ' : ' WHERE ';
    }
    // ---
    $titles = $_GET[$param] ?? [];
    // ---
    if (!empty($titles) && is_array($titles)) {
        // ---
        $placeholders = rtrim(str_repeat('?,', count($titles)), ',');
        // ---
        $qua .= " $where_or_and $column IN ($placeholders)";
        // ---
        $params = array_merge($params, $titles);
    }
    // ---
    return [$qua, $params];
}

function add_li_params(string $qua, array $types, array $endpoint_params = [], array $ignore_params = []): array
{
    $types = change_types($types, $endpoint_params, $ignore_params);
    // ---
    $params = [];
    // ---
    foreach ($types as $type => $tabe) {
        // ---
        $column = $tabe['column'];
        // ---
        if (empty($column)) continue;
        // ---
        if (isset($_GET[$type]) || isset($_GET[$column])) {
            // ---
            // filter input
            $added = filter_input(INPUT_GET, $type, FILTER_SANITIZE_SPECIAL_CHARS) ?? '';
            $added = (!empty($added)) ? $added : filter_input(INPUT_GET, $column, FILTER_SANITIZE_SPECIAL_CHARS);
            // ---
            // if "limit" in endpoint_params remove it
            if ($column == "limit" || $column == "select" || strtolower($added) == "all") {
                continue;
            }
            // ---
            if (isset($tabe['no_empty_value']) && empty($added)) {
                continue;
            }
            // ---
            if ($column == "distinct" && $added == "1") {
                if (strpos(strtolower($qua), 'distinct') === false) {
                    $qua = add_distinct($qua);
                }
            } else {
                list($add_str, $new_params) = add_one_param($qua, $column, $added, $tabe);
                // ---
                $params = array_merge($params, $new_params);
                // ---
                $qua .= $add_str;
            }
        }
    }
    // ---
    return [$qua, $params];
}
```
