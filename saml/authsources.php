<?php
$config = [
    'admin' => [
        'core:AdminPassword',
    ],

    'example-userpass' => [
        'exampleauth:UserPass',
        'test@example.com:password' => [
            'uid' => ['test'],
            'email' => ['test@example.com'],
            'displayName' => ['Test User'],
        ],
    ],
];
