<?PHP

foreach (glob(__DIR__ . '/bots/*.php') as $filename) {
    include_once $filename;
}

foreach (glob(__DIR__ . '/bots/api/*.php') as $filename) {
    include_once $filename;
}

foreach (glob(__DIR__ . '/bots/sql/*.php') as $filename) {
    include_once $filename;
}

foreach (glob(__DIR__ . '/bots/services/*.php') as $filename) {
    include_once $filename;
}
