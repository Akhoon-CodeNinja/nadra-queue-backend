from django.core.management.base import BaseCommand
from services.pdf_ingestion import process_and_save_pdf
import os

class Command(BaseCommand):
    help = 'Ingest a NADRA PDF manual into the FAISS vector database'

    def add_arguments(self, parser):
        parser.add_argument('--pdf', type=str, help='Path to the PDF file')

    def handle(self, *args, **kwargs):
        pdf_path = kwargs['pdf']
        
        if not pdf_path or not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f"Error: PDF file nahi mili -> {pdf_path}"))
            return
            
        self.stdout.write(self.style.SUCCESS(f"Ingestion shuru ho rahi hai..."))
        process_and_save_pdf(pdf_path)
        self.stdout.write(self.style.SUCCESS("System ab NADRA ke naye rules jaanta hai!"))