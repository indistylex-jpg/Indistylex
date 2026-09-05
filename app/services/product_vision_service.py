"""AI product photo analysis — autofill admin product form from one image."""
import base64
import json
import re
import urllib.error
import urllib.request
from typing import Any

from flask import current_app

from app.utils.product_ages import normalize_age_groups


PRODUCT_TYPE_KEYWORDS = {
    'frock': ['frock', 'dress', 'gown'],
    'dress': ['dress', 'frock', 'party'],
    'shirt': ['shirt', 'top', 'blouse', 'formal'],
    'tshirt': ['t-shirt', 'tshirt', 'tee', 'polo'],
    'pant': ['pant', 'trouser', 'bottom', 'legging'],
    'shorts': ['short'],
    'kurta': ['kurta', 'ethnic', 'sherwani', 'lehenga'],
    'romper': ['romper', 'bodysuit', 'onesie'],
    'nightwear': ['night', 'pyjama', 'sleep'],
    'winter': ['jacket', 'sweater', 'hoodie', 'winter'],
    'school': ['school', 'uniform'],
}


def product_ai_configured():
    """True when Gemini or OpenAI vision API key is set."""
    return bool(
        current_app.config.get('GEMINI_API_KEY')
        or current_app.config.get('OPENAI_API_KEY')
    )


def build_category_catalog(category_groups):
    """Flatten admin category groups for the AI prompt."""
    catalog = []
    for group in category_groups or []:
        for opt in group.get('options', []):
            catalog.append({
                'id': opt['id'],
                'name': opt['name'],
                'slug': opt.get('slug', ''),
                'parent': group.get('label', ''),
            })
    return catalog


def analyze_product_image(image_bytes, mime_type, category_groups):
    """
    Analyze a product photo and return structured fields for the admin form.
    Raises ValueError with a user-facing message on failure.
    """
    if not image_bytes:
        raise ValueError('Please choose a product photo first.')
    if not product_ai_configured():
        raise ValueError(
            'AI autofill is not configured. Add GEMINI_API_KEY or OPENAI_API_KEY to your server .env file.'
        )

    mime_type = (mime_type or 'image/jpeg').split(';')[0].strip().lower()
    if mime_type not in ('image/jpeg', 'image/jpg', 'image/png', 'image/webp'):
        raise ValueError('Use a JPG, PNG, or WebP photo.')

    catalog = build_category_catalog(category_groups)
    if not catalog:
        raise ValueError('No active categories found. Add categories before using AI autofill.')

    prompt = _build_prompt(catalog)
    raw = _call_vision_api(image_bytes, mime_type, prompt)
    parsed = _parse_ai_json(raw)
    return _normalize_result(parsed, catalog)


def _build_prompt(catalog):
    category_lines = '\n'.join(
        f"- id={c['id']} slug={c['slug']} name={c['name']} (under {c['parent']})"
        for c in catalog[:80]
    )
    return f"""You are a kids fashion e-commerce catalog expert for Indistylex (India, ages 0-18).
Look at the product photo and return ONLY valid JSON (no markdown) with these keys:
{{
  "name": "customer-facing product title, include color/style",
  "product_type": "one of: frock, dress, shirt, tshirt, pant, shorts, kurta, romper, nightwear, winter, school, other",
  "gender": "boys, girls, or kids",
  "primary_color": "main color name in English e.g. Pink",
  "material": "fabric e.g. 100% Cotton",
  "quality_notes": "brief quality/finish e.g. soft breathable, premium stitching",
  "short_description": "one line under 140 chars for product cards",
  "description": "2-4 sentences: fabric, fit, occasion, care tips",
  "category_id": integer id from list below (best match),
  "age_groups": ["3-4y", "4-5y"] using codes like 0-3m, 1-2y, 3-4y, 9-10y, 13-14y,
  "variant_color": "color for SKU e.g. Pink"
}}

Pick category_id from this store catalog:
{category_lines}

Rules:
- Indian kids wear context; be specific about garment type (frock vs shirt vs kurta).
- If unsure of gender, use kids.
- age_groups: pick 1-4 bands that fit the garment size shown.
- Do NOT suggest prices — admin sets pricing manually.
"""


def _call_vision_api(image_bytes, mime_type, prompt):
    gemini_key = current_app.config.get('GEMINI_API_KEY')
    if gemini_key:
        return _call_gemini(gemini_key, image_bytes, mime_type, prompt)
    openai_key = current_app.config.get('OPENAI_API_KEY')
    if openai_key:
        return _call_openai(openai_key, image_bytes, mime_type, prompt)
    raise ValueError('AI API key missing.')


# Preferred order when ListModels is unavailable. Avoid gemini-2.0-flash (404 for new keys).
GEMINI_VISION_MODELS = (
    'gemini-2.5-flash',
    'gemini-flash-latest',
    'gemini-2.5-flash-lite',
    'gemini-2.0-flash-lite',
    'gemini-2.0-flash-001',
    'gemini-1.5-flash-latest',
    'gemini-1.5-flash-002',
    'gemini-1.5-flash',
)

_discovered_models_cache = {'expires_at': 0.0, 'models': ()}


def _call_gemini(api_key, image_bytes, mime_type, prompt):
    api_key = (api_key or '').strip()
    if not api_key:
        raise ValueError('AI API key missing.')

    configured = (current_app.config.get('GEMINI_VISION_MODEL') or '').strip()
    discovered = _discover_gemini_models(api_key)
    models = []
    for model in (configured, *GEMINI_VISION_MODELS, *discovered):
        if model and model not in models:
            models.append(model)

    b64 = base64.b64encode(image_bytes).decode('ascii')
    last_error = 'Gemini request failed.'

    for model in models:
        for json_mode in (True, False):
            payload = _build_gemini_payload(prompt, mime_type, b64, json_mode=json_mode)
            for api_version in ('v1beta', 'v1'):
                try:
                    data = _gemini_generate(api_key, model, payload, api_version)
                    return data['candidates'][0]['content']['parts'][0]['text']
                except urllib.error.HTTPError as exc:
                    err_body = exc.read().decode('utf-8', errors='replace')
                    last_error = _gemini_http_error(exc.code, err_body, model)
                    if exc.code == 404:
                        break  # try next model
                    if exc.code == 400 and json_mode:
                        continue  # retry same model without JSON mode
                    if exc.code in (401, 403):
                        raise ValueError(last_error) from exc
                    break
                except urllib.error.URLError as exc:
                    raise ValueError('Could not reach AI service. Check server internet.') from exc
                except (KeyError, IndexError, TypeError) as exc:
                    raise ValueError('AI returned an unexpected response.') from exc
            if json_mode:
                continue
            break

    raise ValueError(last_error)


def _build_gemini_payload(prompt, mime_type, b64_image, json_mode=True):
    payload = {
        'contents': [{
            'parts': [
                {'text': prompt},
                {'inlineData': {
                    'mimeType': mime_type,
                    'data': b64_image,
                }},
            ],
        }],
        'generationConfig': {'temperature': 0.2},
    }
    if json_mode:
        payload['generationConfig']['responseMimeType'] = 'application/json'
    return payload


def _gemini_generate(api_key, model, payload, api_version='v1beta'):
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
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _discover_gemini_models(api_key):
    """Fetch models this API key can call; cached for one hour."""
    import time

    now = time.time()
    if _discovered_models_cache['models'] and _discovered_models_cache['expires_at'] > now:
        return _discovered_models_cache['models']

    url = 'https://generativelanguage.googleapis.com/v1beta/models?pageSize=100'
    req = urllib.request.Request(
        url,
        headers={'x-goog-api-key': api_key},
        method='GET',
    )
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
        if '2.5' in lower or '2-5' in lower:
            score += 5
        if 'lite' in lower:
            score += 2
        if 'latest' in lower:
            score += 3
        if 'thinking' in lower or 'tts' in lower or 'live' in lower:
            score -= 20
        if 'pro' in lower:
            score -= 1
        return -score

    names.sort(key=_rank)
    _discovered_models_cache['models'] = tuple(names)
    _discovered_models_cache['expires_at'] = now + 3600
    return _discovered_models_cache['models']


def _gemini_http_error(status_code, err_body, model):
    """Turn Gemini HTTP error JSON into a short admin-facing message."""
    message = ''
    try:
        parsed = json.loads(err_body)
        message = parsed.get('error', {}).get('message', '')
    except json.JSONDecodeError:
        message = err_body[:200]

    if status_code == 404:
        if message:
            return (
                f'Model {model} not available: {message} '
                'Enable Generative Language API for your Google Cloud project in AI Studio.'
            )
        return (
            f'Model {model} not available. '
            'Enable Generative Language API at https://aistudio.google.com/apikey'
        )

    if status_code in (401, 403):
        return 'Invalid GEMINI_API_KEY or API access blocked. Create a new key in Google AI Studio.'

    if message:
        return f'AI service error ({status_code}): {message}'
    return f'AI service error ({status_code}). Check GEMINI_API_KEY.'


def _call_openai(api_key, image_bytes, mime_type, prompt):
    model = current_app.config.get('OPENAI_VISION_MODEL', 'gpt-4o-mini')
    b64 = base64.b64encode(image_bytes).decode('ascii')
    payload = {
        'model': model,
        'messages': [{
            'role': 'user',
            'content': [
                {'type': 'text', 'text': prompt},
                {'type': 'image_url', 'image_url': {'url': f'data:{mime_type};base64,{b64}'}},
            ],
        }],
        'response_format': {'type': 'json_object'},
        'max_tokens': 1200,
    }
    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=body,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        raise ValueError(f'AI service error ({exc.code}). Check OPENAI_API_KEY.') from exc
    except urllib.error.URLError as exc:
        raise ValueError('Could not reach AI service. Check server internet.') from exc

    try:
        return data['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError('AI returned an unexpected response.') from exc


def _parse_ai_json(text):
    text = (text or '').strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError('AI response could not be parsed. Try another photo.') from exc


def _normalize_result(raw: dict, catalog):
    """Map AI output to admin form field values."""
    catalog_by_id = {c['id']: c for c in catalog}
    valid_ids = set(catalog_by_id.keys())

    category_id = raw.get('category_id')
    try:
        category_id = int(category_id) if category_id is not None else None
    except (TypeError, ValueError):
        category_id = None
    if category_id not in valid_ids:
        category_id = _resolve_category_id(raw, catalog)

    gender = (raw.get('gender') or 'kids').lower().strip()
    if gender not in ('boys', 'girls', 'kids'):
        gender = 'kids'

    age_groups = normalize_age_groups(raw.get('age_groups') or [])

    material = (raw.get('material') or '').strip()
    quality = (raw.get('quality_notes') or '').strip()
    if quality and material:
        material = f'{material} — {quality}'
    elif quality:
        material = quality

    return {
        'name': _clip(raw.get('name'), 300),
        'product_type': (raw.get('product_type') or 'other').lower(),
        'category_id': category_id,
        'gender': gender,
        'primary_color': _clip(raw.get('primary_color') or raw.get('variant_color'), 50),
        'material': _clip(material, 200),
        'short_description': _clip(raw.get('short_description'), 500),
        'description': (raw.get('description') or '').strip(),
        'brand': 'Indistylex',
        'age_groups': age_groups,
        'variant_color': _clip(raw.get('variant_color') or raw.get('primary_color'), 50),
    }


def _resolve_category_id(raw, catalog):
    product_type = (raw.get('product_type') or '').lower()
    name_blob = ' '.join([
        str(raw.get('name') or ''),
        str(raw.get('product_type') or ''),
        str(raw.get('description') or ''),
    ]).lower()

    keywords = PRODUCT_TYPE_KEYWORDS.get(product_type, [product_type] if product_type else [])
    for keyword in keywords:
        if not keyword:
            continue
        for cat in catalog:
            slug_name = f"{cat['slug']} {cat['name']}".lower()
            if keyword in slug_name:
                return cat['id']

    for cat in catalog:
        if any(k in name_blob for k in (cat['slug'], cat['name'].lower())):
            return cat['id']

    return catalog[0]['id'] if catalog else None


def _clip(value, max_len):
    text = (value or '').strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + '…'
