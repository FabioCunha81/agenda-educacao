import csv
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware, get_current_timezone
from datetime import datetime
from apps.schedules.models import Agenda
from collections import defaultdict
import re

class Command(BaseCommand):
    help = "Auditoria de histórico do Google Forms."

    def add_arguments(self, parser):
        parser.add_argument('--csv_path', type=str, required=True, help='Caminho do arquivo CSV (ex: planilha.csv)')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        tz = get_current_timezone()

        # Usado apenas para leitura
        agendas = Agenda.objects.all().only(
            'id', 'created_at', 'date', 'contact_email', 'institution_location', 'requester_cpf'
        )
        
        # Otimização em memória para não martelar o banco
        db_records = list(agendas)
        
        completa = []
        pendentes = []

        total_linhas = 0
        stats = {
            "Exata": 0,
            "Provável": 0,
            "Possível Duplicidade": 0,
            "Pendente": 0,
            "Inconsistente": 0
        }

        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=2):
                total_linhas += 1
                carimbo_str = row.get('Carimbo de data/hora', '').strip()
                instituicao = row.get('Instituição/Organização', '').strip()
                solicitante = row.get('Nome Completo', '').strip()
                email = row.get('E-mail', '').strip()
                cidade = row.get('Cidade', '').strip()
                data_pretendida_str = row.get('DATA PRETENDIDA', '').strip()
                cpf = row.get('CPF', '').strip()
                
                # Normalização de CPF para buscas (apenas números)
                cpf_numeros = re.sub(r'[^0-9]', '', cpf) if cpf else ''

                if not carimbo_str or not instituicao:
                    stats["Inconsistente"] += 1
                    completa.append({
                        "linha_csv": i,
                        "carimbo_registro": carimbo_str,
                        "instituicao": instituicao,
                        "solicitante": solicitante,
                        "email": email,
                        "cidade": cidade,
                        "data_pretendida": data_pretendida_str,
                        "classificacao": "Inconsistente",
                        "nivel_confianca": "Nenhum",
                        "agenda_id_encontrada": "",
                        "criterio_utilizado": "Faltam dados essenciais (Carimbo ou Instituição)",
                        "observacao": "Impossível analisar"
                    })
                    continue
                
                # Tentar converter carimbo
                carimbo_dt = None
                try:
                    # Formato típico do google forms: DD/MM/YYYY HH:MM:SS
                    naive_dt = datetime.strptime(carimbo_str, '%d/%m/%Y %H:%M:%S')
                    carimbo_dt = make_aware(naive_dt, timezone=tz)
                except ValueError:
                    pass
                
                # Tentar converter data pretendida
                data_pretendida_dt = None
                try:
                    data_pretendida_dt = datetime.strptime(data_pretendida_str, '%d/%m/%Y').date()
                except ValueError:
                    pass

                if not carimbo_dt:
                    stats["Inconsistente"] += 1
                    completa.append({
                        "linha_csv": i,
                        "carimbo_registro": carimbo_str,
                        "instituicao": instituicao,
                        "solicitante": solicitante,
                        "email": email,
                        "cidade": cidade,
                        "data_pretendida": data_pretendida_str,
                        "classificacao": "Inconsistente",
                        "nivel_confianca": "Nenhum",
                        "agenda_id_encontrada": "",
                        "criterio_utilizado": "Falha no parse do carimbo",
                        "observacao": "Formato de data inválido"
                    })
                    continue

                # Busca no banco carregado em memória
                candidatos_exatos = []
                candidatos_provaveis = []

                for db_item in db_records:
                    # 1. Correspondência Exata
                    # Consideramos tolerância zero para "exata" (mesmo segundo)
                    is_exact_time = abs((db_item.created_at - carimbo_dt).total_seconds()) < 1.0
                    if is_exact_time:
                        candidatos_exatos.append(db_item)
                        continue
                    
                    # 2. Correspondência Provável (Tolerância de ± 5 minutos)
                    diff_seconds = abs((db_item.created_at - carimbo_dt).total_seconds())
                    if diff_seconds <= 300: # 5 minutos
                        # Exige fator complementar para ser provável
                        db_cpf = re.sub(r'[^0-9]', '', db_item.requester_cpf) if db_item.requester_cpf else ''
                        match_cpf = (cpf_numeros and db_cpf and cpf_numeros == db_cpf)
                        
                        db_email = db_item.contact_email.strip().lower() if db_item.contact_email else ''
                        csv_email = email.lower()
                        match_email = (csv_email and db_email and csv_email == db_email)
                        
                        db_inst = db_item.institution_location.strip().lower() if db_item.institution_location else ''
                        csv_inst = instituicao.lower()
                        match_inst = (csv_inst and db_inst and (csv_inst in db_inst or db_inst in csv_inst))
                        
                        match_date = (data_pretendida_dt and db_item.date and data_pretendida_dt == db_item.date)

                        if match_inst and match_cpf:
                            candidatos_provaveis.append((db_item, "Provável (Tempo <= 5m + CPF + Instituição)"))
                        elif match_inst and match_date and match_email:
                            candidatos_provaveis.append((db_item, "Provável (Tempo <= 5m + Data + E-mail + Instituição)"))
                
                # Resolução final do registro
                if len(candidatos_exatos) == 1:
                    classificacao = "Já cadastrado"
                    nivel = "Exata"
                    item_id = candidatos_exatos[0].id
                    criterio = "Timestamp idêntico"
                    stats["Exata"] += 1
                elif len(candidatos_exatos) > 1:
                    classificacao = "Possível Duplicidade"
                    nivel = "Exata (Múltiplos)"
                    item_id = ", ".join([str(x.id) for x in candidatos_exatos])
                    criterio = "Múltiplos timestamps idênticos"
                    stats["Possível Duplicidade"] += 1
                elif len(candidatos_provaveis) == 1:
                    classificacao = "Já cadastrado"
                    nivel = "Provável"
                    item_id = candidatos_provaveis[0][0].id
                    criterio = candidatos_provaveis[0][1]
                    stats["Provável"] += 1
                elif len(candidatos_provaveis) > 1:
                    classificacao = "Possível Duplicidade"
                    nivel = "Provável (Múltiplos)"
                    item_id = ", ".join([str(x[0].id) for x in candidatos_provaveis])
                    criterio = "Múltiplos candidatos no range de 5m que atendem critérios de fallback"
                    stats["Possível Duplicidade"] += 1
                else:
                    classificacao = "Pendente"
                    nivel = "Nenhum"
                    item_id = ""
                    criterio = "Nenhum match exato ou provável encontrado"
                    stats["Pendente"] += 1
                
                res = {
                    "linha_csv": i,
                    "carimbo_registro": carimbo_str,
                    "instituicao": instituicao,
                    "solicitante": solicitante,
                    "email": email,
                    "cidade": cidade,
                    "data_pretendida": data_pretendida_str,
                    "classificacao": classificacao,
                    "nivel_confianca": nivel,
                    "agenda_id_encontrada": item_id,
                    "criterio_utilizado": criterio,
                    "observacao": ""
                }
                completa.append(res)
                
                if classificacao == "Pendente":
                    pendentes.append(res)

        # Gravar os relatórios (Apenas escrita no sistema de arquivos, sem banco de dados)
        fieldnames = ["linha_csv", "carimbo_registro", "instituicao", "solicitante", "email", "cidade", "data_pretendida", "classificacao", "nivel_confianca", "agenda_id_encontrada", "criterio_utilizado", "observacao"]
        
        with open("auditoria_forms_completa.csv", "w", encoding="utf-8-sig", newline="") as out1:
            w1 = csv.DictWriter(out1, fieldnames=fieldnames)
            w1.writeheader()
            w1.writerows(completa)
            
        with open("auditoria_forms_pendentes.csv", "w", encoding="utf-8-sig", newline="") as out2:
            w2 = csv.DictWriter(out2, fieldnames=fieldnames)
            w2.writeheader()
            w2.writerows(pendentes)

        self.stdout.write(self.style.SUCCESS("-" * 40))
        self.stdout.write(self.style.SUCCESS("AUDITORIA CONCLUÍDA COM SUCESSO (Read-Only)"))
        self.stdout.write(self.style.SUCCESS("-" * 40))
        self.stdout.write(f"Total de registros na planilha: {total_linhas}")
        self.stdout.write(f"Já cadastrados (Exatos): {stats['Exata']}")
        self.stdout.write(f"Já cadastrados (Prováveis): {stats['Provável']}")
        self.stdout.write(f"Pendentes de lançamento: {stats['Pendente']}")
        self.stdout.write(f"Possíveis duplicados: {stats['Possível Duplicidade']}")
        self.stdout.write(f"Inconsistências: {stats['Inconsistente']}")
        self.stdout.write("-" * 40)
        self.stdout.write("Relatórios gerados: auditoria_forms_completa.csv e auditoria_forms_pendentes.csv")
