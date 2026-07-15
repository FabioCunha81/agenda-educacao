import csv
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from apps.schedules.models import Agenda
import re

class Command(BaseCommand):
    help = "Auditoria de histórico do AppSheet."

    def add_arguments(self, parser):
        parser.add_argument('--csv_path', type=str, required=True, help='Caminho do arquivo CSV do AppSheet')

    def handle(self, *args, **options):
        csv_path = options['csv_path']

        # Usado apenas para leitura
        agendas = Agenda.objects.all().only(
            'id', 'source_id', 'date', 'institution_location', 'location', 
            'start_time', 'action_type', 'city', 'contact_email'
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

        with open(csv_path, mode='r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.reader(f)
            # Ignorar cabeçalho
            try:
                next(reader)
            except StopIteration:
                pass

            for i, row in enumerate(reader, start=2):
                if not any(row):
                    continue

                total_linhas += 1

                # Índices mapeados com base no padrão do AppSheet:
                # 0: ID, 1: DATA, 9: TIPO DE AÇÃO, 10: INSTITUIÇÃO/LOCAL
                # 12: HORÁRIO, 15: MUNICÍPIO, 18: E-MAIL
                id_appsheet = row[0].strip() if len(row) > 0 else ""
                data_str = row[1].strip() if len(row) > 1 else ""
                modalidade = row[9].strip() if len(row) > 9 else ""
                instituicao = row[10].strip() if len(row) > 10 else ""
                horario_str = row[12].strip() if len(row) > 12 else ""
                municipio = row[15].strip() if len(row) > 15 else ""

                if not data_str or not instituicao:
                    stats["Inconsistente"] += 1
                    completa.append({
                        "linha_csv": i,
                        "id_appsheet": id_appsheet,
                        "data_agenda": data_str,
                        "instituicao": instituicao,
                        "modalidade": modalidade,
                        "municipio": municipio,
                        "horario": horario_str,
                        "classificacao": "Inconsistente",
                        "nivel_confianca": "Nenhum",
                        "agenda_id_encontrada": "",
                        "criterio_utilizado": "Faltam dados essenciais (Data ou Instituição)"
                    })
                    continue
                
                # Parse date
                dt = None
                try:
                    dt = datetime.strptime(data_str, "%d/%m/%Y").date()
                except ValueError:
                    try:
                        dt = datetime.strptime(data_str, "%Y-%m-%d").date()
                    except ValueError:
                        try:
                            dt = datetime.strptime(data_str, "%m/%d/%Y").date()
                        except ValueError:
                            pass

                if not dt:
                    stats["Inconsistente"] += 1
                    completa.append({
                        "linha_csv": i,
                        "id_appsheet": id_appsheet,
                        "data_agenda": data_str,
                        "instituicao": instituicao,
                        "modalidade": modalidade,
                        "municipio": municipio,
                        "horario": horario_str,
                        "classificacao": "Inconsistente",
                        "nivel_confianca": "Nenhum",
                        "agenda_id_encontrada": "",
                        "criterio_utilizado": "Formato de data inválido ou não suportado"
                    })
                    continue

                # Parse time
                start_time = None
                if horario_str:
                    try:
                        if len(horario_str) == 5:
                            start_time = datetime.strptime(horario_str, "%H:%M").time()
                        elif len(horario_str) >= 8:
                            start_time = datetime.strptime(horario_str[:8], "%H:%M:%S").time()
                    except ValueError:
                        pass

                # Busca no banco carregado em memória
                candidatos_exatos = []
                candidatos_provaveis = []

                # Source ID que o script de importação original usaria
                possible_source_id = f"appsheet:{id_appsheet}" if id_appsheet else ""

                for db_item in db_records:
                    # Se tiver source_id, é match perfeito instantâneo (O AppSheet importou e gravou a tag)
                    if possible_source_id and db_item.source_id == possible_source_id:
                        candidatos_exatos.append(db_item)
                        continue

                    # Fallback principal baseado na DATA
                    if db_item.date == dt:
                        db_inst = (db_item.institution_location or "").strip().lower()
                        db_loc = (db_item.location or "").strip().lower()
                        csv_inst = instituicao.lower()
                        
                        match_inst = (csv_inst and db_inst and (csv_inst in db_inst or db_inst in csv_inst)) or \
                                     (csv_inst and db_loc and (csv_inst in db_loc or db_loc in csv_inst))
                        
                        if match_inst:
                            candidatos_exatos.append(db_item)
                        else:
                            # Se não bateu instituição perfeitamente, tenta provável (mesma data + horario + municipio)
                            db_city = (db_item.city or "").strip().lower()
                            csv_city = municipio.lower()
                            match_city = (csv_city and db_city and csv_city == db_city)
                            
                            match_time = (start_time and db_item.start_time and start_time == db_item.start_time)
                            
                            if match_city and match_time:
                                candidatos_provaveis.append(db_item)
                
                # Resolução final do registro
                if len(candidatos_exatos) == 1:
                    classificacao = "Já cadastrado"
                    nivel = "Exata"
                    item_id = candidatos_exatos[0].id
                    criterio = "Source ID Idêntico ou (Data + Instituição) batem perfeitamente"
                    stats["Exata"] += 1
                elif len(candidatos_exatos) > 1:
                    classificacao = "Possível Duplicidade"
                    nivel = "Exata (Múltiplos)"
                    item_id = ", ".join([str(x.id) for x in candidatos_exatos])
                    criterio = "Múltiplos registros com mesma Data e Instituição"
                    stats["Possível Duplicidade"] += 1
                elif len(candidatos_provaveis) == 1:
                    classificacao = "Já cadastrado"
                    nivel = "Provável"
                    item_id = candidatos_provaveis[0].id
                    criterio = "Mesma Data + Município + Horário batem (Instituição diverge levemente)"
                    stats["Provável"] += 1
                elif len(candidatos_provaveis) > 1:
                    classificacao = "Possível Duplicidade"
                    nivel = "Provável (Múltiplos)"
                    item_id = ", ".join([str(x.id) for x in candidatos_provaveis])
                    criterio = "Múltiplos registros com mesma Data + Município + Horário"
                    stats["Possível Duplicidade"] += 1
                else:
                    classificacao = "Pendente"
                    nivel = "Nenhum"
                    item_id = ""
                    criterio = "Nenhuma agenda na mesma data que satisfaça local, ou hora/município"
                    stats["Pendente"] += 1
                
                res = {
                    "linha_csv": i,
                    "id_appsheet": id_appsheet,
                    "data_agenda": data_str,
                    "instituicao": instituicao,
                    "modalidade": modalidade,
                    "municipio": municipio,
                    "horario": horario_str,
                    "classificacao": classificacao,
                    "nivel_confianca": nivel,
                    "agenda_id_encontrada": item_id,
                    "criterio_utilizado": criterio
                }
                completa.append(res)
                
                if classificacao == "Pendente":
                    pendentes.append(res)

        # Gravar os relatórios (Apenas escrita no sistema de arquivos)
        fieldnames = ["linha_csv", "id_appsheet", "data_agenda", "instituicao", "modalidade", "municipio", "horario", "classificacao", "nivel_confianca", "agenda_id_encontrada", "criterio_utilizado"]
        
        with open("auditoria_appsheet_completa.csv", "w", encoding="utf-8-sig", newline="") as out1:
            w1 = csv.DictWriter(out1, fieldnames=fieldnames)
            w1.writeheader()
            w1.writerows(completa)
            
        with open("auditoria_appsheet_pendentes.csv", "w", encoding="utf-8-sig", newline="") as out2:
            w2 = csv.DictWriter(out2, fieldnames=fieldnames)
            w2.writeheader()
            w2.writerows(pendentes)

        self.stdout.write(self.style.SUCCESS("-" * 40))
        self.stdout.write(self.style.SUCCESS("AUDITORIA APPSHEET CONCLUÍDA COM SUCESSO (Read-Only)"))
        self.stdout.write(self.style.SUCCESS("-" * 40))
        self.stdout.write(f"Total de registros na planilha: {total_linhas}")
        self.stdout.write(f"Já cadastrados (Exatos): {stats['Exata']}")
        self.stdout.write(f"Já cadastrados (Prováveis): {stats['Provável']}")
        self.stdout.write(f"Pendentes de lançamento: {stats['Pendente']}")
        self.stdout.write(f"Possíveis duplicados: {stats['Possível Duplicidade']}")
        self.stdout.write(f"Inconsistências: {stats['Inconsistente']}")
        self.stdout.write("-" * 40)
        self.stdout.write("Relatórios gerados: auditoria_appsheet_completa.csv e auditoria_appsheet_pendentes.csv")
