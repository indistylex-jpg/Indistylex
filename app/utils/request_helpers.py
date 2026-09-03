"""HTTP request helpers for JSON vs HTML responses."""
from flask import request


def wants_json_response():
    """True when the client expects JSON (fetch/XHR/API routes)."""
    if request.is_json:
        return True
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    accept = request.accept_mimetypes
    if accept['application/json'] and accept['application/json'] >= accept['text/html']:
        return True
    # Admin AI analyze and similar POST endpoints
    if request.path.endswith('/analyze-image'):
        return True
    return False
