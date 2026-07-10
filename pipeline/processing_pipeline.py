from agents.extraction_agent import ExtractionAgent
from agents.classification_agent import ClassificationAgent
from agents.bank_statement_agent import BankStatementAgent
from agents.balance_sheet_agent import BalanceSheetAgent
from services.normalization_service import NormalizationService
from agents.cleaning_agent import CleaningAgent
from agents.validation_agent import ValidationAgent
from agents.csv_export_agent import CSVExportAgent


class ProcessingPipeline:

    @staticmethod
    def run(pdf_path):

        # Step 1
        document = ExtractionAgent.run(pdf_path)

        document = NormalizationService.normalize(document)

        # Step 2
        document = ClassificationAgent.run(document)

        # Step 3
        if document.document_type == "bank_statement":

            document = BankStatementAgent.run(document)

        elif document.document_type == "balance_sheet":

            document = BalanceSheetAgent.run(document)

        else:

            raise Exception("Unsupported document type.")

        # Step 4
        document = CleaningAgent.run(document)

        # Step 5
        document = ValidationAgent.run(document)

        # Step 6
        CSVExportAgent.run(document)

        return document
