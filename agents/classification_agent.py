from services.classifier_service import ClassifierService


class ClassificationAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("CLASSIFICATION AGENT")
        print("=" * 70)

        print(document.cleaned_markdown[:1000])
        document.document_type = ClassifierService.classify(document)

        print("\nDetected Document Type")
        print("----------------------")
        print(document.document_type)

        if document.document_type == "unknown":

            raise Exception(
                "Unable to classify document. "
                "No balance-sheet or bank-statement keywords were detected."
            )

        print("=" * 70)
        print()

        return document
