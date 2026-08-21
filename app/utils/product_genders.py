"""Product gender options."""

GENDER_CHOICES = [
    ('', 'Select Gender'),
    ('boys', 'Boys'),
    ('girls', 'Girls'),
    ('kids', 'Kids (Unisex)'),
]

GENDER_LABELS = {
    'boys': 'Boys',
    'girls': 'Girls',
    'kids': 'Kids',
    'boy': 'Boys',
    'girl': 'Girls',
}


def gender_label(value):
    if not value:
        return ''
    return GENDER_LABELS.get(value.lower(), value.replace('_', ' ').title())
