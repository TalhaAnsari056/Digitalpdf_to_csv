from services.classifier_service import ClassifierService


class ClassificationAgent:

    @staticmethod
    def run(document):

        print("\n" + "=" * 70)
        print("CLASSIFICATION AGENT")
        print("=" * 70)

        document.document_type = ClassifierService.classify(document)

        print("\nDetected Document Type")
        print("----------------------")
        print(document.document_type)

        print("=" * 70)
        print()

        return document
