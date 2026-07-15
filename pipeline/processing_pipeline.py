# from agents.extraction_agent import ExtractionAgent
# from agents.cleaning_agent import CleaningAgent
# from agents.classification_agent import ClassificationAgent

# from agents.bank_statement_agent import BankStatementAgent
# from agents.balance_sheet_agent import BalanceSheetAgent

# # from agents.validation_agent import ValidationAgent
# from agents.csv_export_agent import CSVExportAgent


# class ProcessingPipeline:

#     @staticmethod
#     def run(pdf_path):

#         print("\n" + "=" * 80)
#         print("AI PDF TO CSV PIPELINE")
#         print("=" * 80)

#         ############################################################
#         # STEP 1 - Marker Extraction
#         ############################################################

#         print("\n[1/6] Marker Extraction\n")

#         document = ExtractionAgent.run(pdf_path)

#         ############################################################
#         # STEP 2 - Markdown Cleaning
#         ############################################################

#         print("\n[2/6] Cleaning Markdown\n")

#         document = CleaningAgent.run(document)

#         ############################################################
#         # STEP 3 - Rule-Based Classification
#         ############################################################

#         print("\n[3/6] Document Classification\n")

#         document = ClassificationAgent.run(document)

#         ############################################################
#         # STEP 4 - Document Processing (Temporary)
#         ############################################################

#         print("\n[4/6] Document Processing\n")

#         if document.document_type == "bank_statement":

#             document = BankStatementAgent.run(document)

#         elif document.document_type == "balance_sheet":

#             document = BalanceSheetAgent.run(document)

#         else:

#             raise Exception(f"Unsupported document type: {document.document_type}")

#         ############################################################
#         # STEP 6 - CSV Export
#         ############################################################

#         # print("\n[6/6] CSV Export\n")

#         # CSVExportAgent.run(document)

#         # print("\n" + "=" * 80)
#         # print("PIPELINE COMPLETED")
#         # print("=" * 80)

#         return document
from agents.extraction_agent import ExtractionAgent
from agents.cleaning_agent import CleaningAgent
from agents.classification_agent import ClassificationAgent
from agents.llm_extraction_agent import LLMExtractionAgent

# from agents.csv_export_agent import CSVExportAgent


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
        # STEP 5 - CSV Export
        ############################################################

        # print("\n[5/5] CSV Export\n")

        # CSVExportAgent.run(document)

        print("\n" + "=" * 80)
        print("PIPELINE COMPLETED")
        print("=" * 80)

        return document
