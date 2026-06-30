import pandas as pd
from django.core.management.base import BaseCommand
from apps.schedules.models import Region, Municipality, Agenda

class Command(BaseCommand):
    help = "Import municipalities and regions from Excel, and normalize existing agendas"

    def add_arguments(self, parser):
        parser.add_argument('excel_path', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        excel_path = kwargs['excel_path']
        self.stdout.write(f"Reading from: {excel_path}")

        try:
            df = pd.read_excel(excel_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to read Excel: {e}"))
            return

        regions_created = 0
        mun_created = 0
        agendas_updated = 0

        # Mapping for normalization
        name_to_mun = {}

        for _, row in df.iterrows():
            mun_name = str(row['Município']).strip()
            region_name = str(row['Região de Governo']).strip()
            ibge_code = str(row['Código IBGE']).strip()

            if not mun_name or mun_name.lower() == 'nan':
                continue

            # Create or get Region
            region, created = Region.objects.get_or_create(
                name=region_name,
                defaults={'source_id': f"region:{region_name.lower()}"}
            )
            if created:
                regions_created += 1

            # Create or get Municipality
            mun, created = Municipality.objects.get_or_create(
                name=mun_name,
                defaults={
                    'source_id': f"ibge:{ibge_code}",
                    'region': region
                }
            )
            if created:
                mun_created += 1
            elif mun.region != region:
                mun.region = region
                mun.save(update_fields=['region'])

            # Store mapping (case insensitive, without accents ideally, but exact lower works for most)
            name_to_mun[mun_name.lower()] = mun
            # Add some common variations just in case
            if " de " in mun_name.lower():
                name_to_mun[mun_name.lower().replace(" de ", " ")] = mun
            if " do " in mun_name.lower():
                name_to_mun[mun_name.lower().replace(" do ", " ")] = mun
            if " dos " in mun_name.lower():
                name_to_mun[mun_name.lower().replace(" dos ", " ")] = mun

        self.stdout.write(f"Created {regions_created} new regions and {mun_created} new municipalities.")

        # Special hardcoded cases observed in standard usage
        hardcoded_variations = {
            "rio de janeiro": "Rio de Janeiro",
            "sao goncalo": "São Gonçalo",
            "niteroi": "Niterói",
            "duque de caxias": "Duque de Caxias",
            "sao joao de meriti": "São João de Meriti",
            "belford roxo": "Belford Roxo",
            "nova iguacu": "Nova Iguaçu",
            "macae": "Macaé",
            "campos dos goytacazes": "Campos dos Goytacazes",
            "cabo frio": "Cabo Frio",
            "armacao dos buzios": "Armação dos Búzios",
            "teresopolis": "Teresópolis",
            "petropolis": "Petrópolis",
            "nova friburgo": "Nova Friburgo",
            "mage": "Magé",
            "itaguai": "Itaguaí",
            "marica": "Maricá",
            "araruama": "Araruama",
            "saquarema": "Saquarema",
            "rio das ostras": "Rio das Ostras",
            "sao pedro da aldeia": "São Pedro da Aldeia",
            "iguaba grande": "Iguaba Grande",
            "arrial do cabo": "Arraial do Cabo",
            "arraial do cabo": "Arraial do Cabo",
        }

        # Normalize Agenda.city
        import unicodedata
        def strip_accents(s):
            return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

        for k, v in hardcoded_variations.items():
            k_strip = strip_accents(k)
            # Find the actual municipality object for the value
            mun_obj = name_to_mun.get(v.lower())
            if mun_obj:
                name_to_mun[k_strip] = mun_obj
        
        # Add all exact names stripped
        for k, v in list(name_to_mun.items()):
            name_to_mun[strip_accents(k)] = v

        for agenda in Agenda.objects.all():
            city_str = agenda.city.strip()
            mun_ref_name = agenda.municipality_ref.name if agenda.municipality_ref else ""
            
            check_str = mun_ref_name or city_str
            if not check_str:
                continue

            normalized_key = strip_accents(check_str.lower())
            
            matched_mun = name_to_mun.get(normalized_key)
            
            changed = False
            if matched_mun:
                if agenda.municipality_ref != matched_mun:
                    agenda.municipality_ref = matched_mun
                    changed = True
                
                if agenda.city != matched_mun.name:
                    agenda.city = matched_mun.name
                    changed = True
            else:
                # Capitalize it better as fallback
                fallback_city = city_str.title()
                if agenda.city != fallback_city:
                    agenda.city = fallback_city
                    changed = True

            if changed:
                agenda.save(update_fields=['municipality_ref', 'city'])
                agendas_updated += 1

        self.stdout.write(self.style.SUCCESS(f"Finished! Normalized and updated {agendas_updated} agendas."))
