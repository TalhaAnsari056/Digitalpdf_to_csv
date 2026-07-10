# import re


# class CleaningAgent:

#     @staticmethod
#     def run(document):

#         print("\nCleaning Data...\n")

#         if document.document_type == "balance_sheet":

#             CleaningAgent.clean_balance_sheet(document)

#         elif document.document_type == "bank_statement":

#             CleaningAgent.clean_bank_statement(document)

#         return document

#     @staticmethod
#     def clean_balance_sheet(document):

#         for record in document.parsed_data:

#             record.account_name = re.sub(r"\s+", " ", record.account_name).strip()

#             record.section = re.sub(r"\s+", " ", record.section).strip()

#             if record.account_code:

#                 record.account_code = record.account_code.strip()

#     @staticmethod
#     def clean_bank_statement(document):

#         for record in document.parsed_data:

#             record.description = re.sub(r"\s+", " ", record.description)

#             record.description = record.description.strip()

#             if record.currency:

#                 record.currency = record.currency.upper()

#             if record.date:

#                 record.date = record.date.replace("-", "/")

import re
from dataclasses import fields


class CleaningAgent:

    @staticmethod
    def run(document):

        print("\nCleaning Data...\n")

        if not document.parsed_data:
            return document

        for record in document.parsed_data:

            for field in fields(record):

                value = getattr(record, field.name)

                if isinstance(value, str):

                    value = re.sub(r"\s+", " ", value)

                    value = value.strip()

                    setattr(record, field.name, value)

        return document
