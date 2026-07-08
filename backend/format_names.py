import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.schedules.models import Agent, Chief, Support

def format_all_names():
    for model_class in [Agent, Chief, Support]:
        records = model_class.objects.all()
        count = 0
        for r in records:
            if r.name.isupper():
                words = r.name.split()
                new_words = []
                for w in words:
                    w_lower = w.lower()
                    if w_lower in ['da', 'de', 'do', 'dos', 'das', 'e']:
                        new_words.append(w_lower)
                    else:
                        new_words.append(w.capitalize())
                
                new_name = " ".join(new_words)
                print(f"[{model_class.__name__}] Atualizando: {r.name} -> {new_name}")
                r.name = new_name
                r.save(update_fields=['name'])
                count += 1
        print(f"[{model_class.__name__}] {count} nomes atualizados.")

if __name__ == "__main__":
    print("Iniciando formatação de nomes...")
    format_all_names()
    print("Concluído!")
