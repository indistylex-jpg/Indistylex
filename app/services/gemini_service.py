"""Shared Google Gemini text generation for Indistylex."""
import json
import time
import urllib.error
import urllib.request

from flask import current_app

GEMINI_TEXT_MODELS = (
    'gemini-2.5-flash',
    'gemini-flash-latest',
    'gemini-2.5-flash-lite',
    'gemini-2.0-flash-lite',
    'gemini-1.5-flash-latest',
)

_discovered_models_cache = {'expires_at': 0.0, 'models': ()}


def gemini_configured():
    return bool((current_app.config.get('GEMINI_API_KEY') or '').strip())


def generate_text(prompt, *, system=None, temperature=0.5, json_mode=False, timeout=60):
    """
    Call Gemini with a text prompt. Returns response text.
    Raises ValueError with a short admin/customer-facing message on failure.
    """
    api_key = (current_app.config.get('GEMINI_API_KEY') or '').strip()
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured on the server.')

    configured = (current_app.config.get('GEMINI_VISION_MODEL') or '').strip()
    discovered = _discover_gemini_models(api_key)
    models = []
    for model in (configured, *GEMINI_TEXT_MODELS, *discovered):
        if model and model not in models:
            models.append(model)

    parts = []
    if system:
        parts.append({'text': system.strip()})
    parts.append({'text': prompt.strip()})

    last_error = 'Gemini request failed.'
    for model in models:
        for use_json in ((True, False) if json_mode else (False,)):
            payload = {
                'contents': [{'parts': parts}],
                'generationConfig': {'temperature': temperature},
            }
            if use_json:
                payload['generationConfig']['responseMimeType'] = 'application/json'

            for api_version in ('v1beta', 'v1'):
                try:
                    data = _gemini_generate(api_key, model, payload, api_version, timeout)
                    return data['candidates'][0]['content']['parts'][0]['text']
                except urllib.error.HTTPError as exc:
                    err_body = exc.read().decode('utf-8', errors='replace')
                    last_error = _gemini_http_error(exc.code, err_body, model)
                    if exc.code == 404:
                        break
                    if exc.code == 400 and use_json:
                        continue
                    if exc.code in (401, 403):
                        raise ValueError(last_error) from exc
                    break
                except urllib.error.URLError as exc:
                    raise ValueError('Could not reach AI service. Check server internet.') from exc
                except (KeyError, IndexError, TypeError) as exc:
                    raise ValueError('AI returned an unexpected response.') from exc
            if json_mode and use_json:
                continue
            break

    raise ValueError(last_error)


def parse_json_response(raw):
    """Parse JSON from Gemini output, tolerating markdown fences."""
    text = (raw or '').strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[-1]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        if text.lower().startswith('json'):
            text = text[4:].strip()
    return json.loads(text)


def _gemini_generate(api_key, model, payload, api_version='v1beta', timeout=60):
    body = json.dumps(payload).encode('utf-8')
    url = (
        f'https://generativelanguage.googleapis.com/{api_version}/models/{model}:generateContent'
    )
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': api_key,
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _discover_gemini_models(api_key):
    now = time.time()
    if _discovered_models_cache['models'] and _discovered_models_cache['expires_at'] > now:
        return _discovered_models_cache['models']

    url = 'https://generativelanguage.googleapis.com/v1beta/models?pageSize=100'
    req = urllib.request.Request(url, headers={'x-goog-api-key': api_key}, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError):
        return ()

    names = []
    for item in data.get('models', []):
        methods = item.get('supportedGenerationMethods') or []
        if 'generateContent' not in methods:
            continue
        name = item.get('name', '')
        if name.startswith('models/'):
            name = name[len('models/'):]
        if name:
            names.append(name)

    def _rank(model_name):
        lower = model_name.lower()
        score = 0
        if 'flash' in lower:
            score += 10
        if '2.5' in lower:
            score += 5
        if 'thinking' in lower or 'tts' in lower or 'live' in lower:
            score -= 20
        return -score

    names.sort(key=_rank)
    _discovered_models_cache['models'] = tuple(names)
    _discovered_models_cache['expires_at'] = now + 3600
    return _discovered_models_cache['models']


def _gemini_http_error(status_code, err_body, model):
    message = ''
    try:
        parsed = json.loads(err_body)
        message = parsed.get('error', {}).get('message', '')
    except json.JSONDecodeError:
        message = err_body[:200]

    if status_code == 404:
        return f'Model {model} not available. Check GEMINI_API_KEY in Google AI Studio.'
    if status_code in (401, 403):
        return 'Invalid GEMINI_API_KEY or API access blocked.'
    if message:
        return f'AI service error ({status_code}): {message}'
    return f'AI service error ({status_code}).'
