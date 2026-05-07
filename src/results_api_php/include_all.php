<?PHP

# don't use OAuth\Settings\Settings here, Instance is not created yet
$env = getenv('APP_ENV') ?: ($_ENV['APP_ENV'] ?? 'development');

if ($env === 'development' && file_exists(__DIR__ . '/load_env.php')) {
    include_once __DIR__ . '/load_env.php';
}
include_once __DIR__ . '/backend/results/new_way/get_results.php';
include_once __DIR__ . '/backend/results/getcats.php';
include_once __DIR__ . '/backend/helps.php';
include_once __DIR__ . '/backend/api_calls/mdwiki_sql.php';
