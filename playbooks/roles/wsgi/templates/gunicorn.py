CONFIG = {
    'mode': 'wsgi',
    'args': (
        '--bind=unix:/tmp/gunicorn.sock',
        '--workers=3',
        '--timeout=60',
        'gatewatch.app',
    ),
}
