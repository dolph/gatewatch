CONFIG = {
    'mode': 'wsgi',
    'args': (
        '--bind=unix:/tmp/gunicorn.sock',
        '--workers=3',
        'gatewatch.app',
    ),
}
