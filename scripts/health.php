<?php
// Check the interface consumers use, including the real API credential.
if (($argv[1] ?? '') === 'daemon') {
    $command = file_get_contents('/proc/1/cmdline');
    exit(is_file('/var/www/storage/database/dreeve.db') && str_contains($command, 'app:daemon:run') ? 0 : 1);
}
$context = stream_context_create(['http' => [
    'header' => 'Authorization: Bearer '.getenv('DREEVE_API_KEY'),
    'timeout' => 5,
]]);
$response = @file_get_contents('http://localhost:8080/api/v1/status', false, $context);
exit($response !== false && is_array(json_decode($response, true)) ? 0 : 1);
