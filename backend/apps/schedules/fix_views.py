import codecs
path = r'd:\agenda_eventos_ols\backend\apps\schedules\views.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

replacements = {
    'ÃƒÂ©': 'é',
    'ÃƒÂ£': 'ã',
    'ÃƒÂ¡': 'á',
    'ÃƒÂ³': 'ó',
    'ÃƒÂº': 'ú',
    'ÃƒÂ§': 'ç',
    'ÃƒÂª': 'ê',
    'ÃƒÂ­': 'í',
    'ÃƒÂ\xad': 'í', # In case the editor rendered it weirdly
    'Ã¢â‚¬Å“': 'Ó', # Actually wait, what is Ã¢â‚¬Å“? It was double encoded Ó. In views.py we might just have Ã“ for Ó. Let's look closely at views.py
    'ÃƒÂµ': 'õ',
    'ÃƒÂ¢': 'â',
    'ÃƒÂ ': 'à',
    'ÃƒÂ': 'À',  # Check if there's Á or À. `Recursos ÃƒÂudio-visuais` -> `ÃƒÂ` is Á. Let's explicitly put 'ÃƒÂ': 'Á'.
    'ÃƒÂ': 'Á',
    'ÃƒÂ‰': 'É',
    'ÃƒÂ“': 'Ó',
    'ÃƒÂ”': 'Ô',
    'ÃƒÂ•': 'Õ',
    'ÃƒÂŠ': 'Ê',
    'ÃƒÂ‡': 'Ç',
    'Ã¢â‚¬â€ ': '—', # EM DASH
}

# Let's fix the specific ones we know exist from the grep:
# "SolicitaÃƒÂ§ÃƒÂ£o"
# "DinÃƒÂ¢micas"
# "Recursos ÃƒÂudio-visuais"
# "tÃƒÂ©cnico"

for k, v in replacements.items():
    text = text.replace(k, v)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Finished fixing views.py")
