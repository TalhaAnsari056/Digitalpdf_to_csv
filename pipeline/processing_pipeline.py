from agents.extraction_agent import ExtractionAgent
from agents.cleaning_agent import CleaningAgent
from agents.classification_agent import ClassificationAgent
from agents.llm_extraction_agent import LLMExtractionAgent
from agents.markdown_table_parser_agent import MarkdownTableParserAgent

from agents.balancesheet_normalizer_agent import BalanceSheetNormalizerAgent
from agents.bank_statement_normalizer_agent import BankStatementNormalizerAgent

from agents.balancesheet_validator_agent import BalanceSheetValidatorAgent
from agents.bank_statement_validator_agent import BankStatementValidatorAgent

from agents.csv_export_agent import CSVExportAgent

from agents.excel_formatter_agent import ExcelFormatterAgent
from agents.bank_statement_excel_formatter_agent import (
    BankStatementExcelFormatterAgent,
)
from agents.balance_sheet_response_agent import BalanceSheetResponseAgent
from agents.bank_statement_response_agent import (
    BankStatementResponseAgent,
)


class ProcessingPipeline:

    @staticmethod
    def run(pdf_path):

        print("\n" + "=" * 80)
        print("AI PDF TO CSV PIPELINE")
        print("=" * 80)

        ############################################################
        # STEP 1 - Marker Extraction
        ############################################################

        print("\n[1/5] Marker Extraction\n")

        document = ExtractionAgent.run(pdf_path)

        ############################################################
        # STEP 2 - Markdown Cleaning
        ############################################################

        print("\n[2/5] Cleaning Markdown\n")

        document = CleaningAgent.run(document)

        ############################################################
        # STEP 3 - Rule-Based Classification
        ############################################################

        print("\n[3/5] Document Classification\n")

        document = ClassificationAgent.run(document)

        ############################################################
        # STEP 4 - Prompt + LLM Mapping
        ############################################################

        print("\n[4/5] LLM Mapping\n")

        document = LLMExtractionAgent.run(document)
        ############################################################
        # STEP 5
        print("\n[5/10] Markdown Table Parsing\n")
        document = MarkdownTableParserAgent.run(document)

        ############################################################
        # BALANCE SHEET PIPELINE
        ############################################################

        if document.document_type == "balance_sheet":

            ########################################################
            # STEP 6
            ########################################################

            print("\n[6/10] Balance Sheet Normalization\n")

            document = BalanceSheetNormalizerAgent.run(document)

            ########################################################
            # STEP 7
            ########################################################

            print("\n[7/10] Balance Sheet Validation\n")

            document = BalanceSheetValidatorAgent.run(document)

            ########################################################
            # STEP 8
            ########################################################

            print("\n[8/10] CSV Export\n")

            document = CSVExportAgent.run(document)

            ########################################################
            # STEP 9
            ########################################################

            print("\n[9/10] Excel Formatter\n")

            document = ExcelFormatterAgent.run(document)

            ########################################################
            # STEP 10
            ########################################################

            print("\n[10/10] Building API Response\n")

            document = BalanceSheetResponseAgent.run(document)

        ############################################################
        # BANK STATEMENT PIPELINE
        ############################################################

        elif document.document_type == "bank_statement":

            ########################################################
            # STEP 6
            ########################################################

            print("\n[6/10] Bank Statement Normalization\n")

            document = BankStatementNormalizerAgent.run(document)

            ########################################################
            # STEP 7
            ########################################################

            print("\n[7/10] Bank Statement Validation\n")

            document = BankStatementValidatorAgent.run(document)

            ########################################################
            # STEP 8
            ########################################################

            print("\n[8/10] CSV Export\n")

            document = CSVExportAgent.run(document)

            ########################################################
            # STEP 9
            ########################################################

            print("\n[9/10] Excel Formatter\n")

            document = BankStatementExcelFormatterAgent.run(document)

            ########################################################
            # STEP 10
            ########################################################

            print("\n[10/10] Building API Response\n")

            document = BankStatementResponseAgent.run(document)

        ############################################################
        # Unsupported
        ############################################################

        else:

            raise ValueError(f"Unsupported document type: {document.document_type}")

        ############################################################

        print("\n" + "=" * 80)
        print("PIPELINE COMPLETED")
        print("=" * 80)

        return document
