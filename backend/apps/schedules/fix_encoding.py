import codecs
path = r'd:\agenda_eventos_ols\backend\apps\schedules\serializers.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

replacements = {
    'ÃƒÆ’Ã‚Â©': 'é',
    'ÃƒÆ’Ã‚Â£': 'ã',
    'ÃƒÆ’Ã‚Â¡': 'á',
    'ÃƒÆ’Ã‚Â³': 'ó',
    'ÃƒÆ’Ã‚Âº': 'ú',
    'ÃƒÆ’Ã‚Â§': 'ç',
    'ÃƒÆ’Ã‚Âª': 'ê',
    'ÃƒÆ’Ã‚Â­': 'í',
    'ÃƒÆ’Ã¢â‚¬Å“': 'Ó',
    'ÃƒÆ’Ã¢â‚¬Â°': 'É',
    'ÃƒÆ’Ã‚Âµ': 'õ',
    'ÃƒÆ’Ã‚Â¢': 'â',
    'ÃƒÆ’Ã‚Â ': 'à'
}

for k, v in replacements.items():
    text = text.replace(k, v)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Finished replacements")
