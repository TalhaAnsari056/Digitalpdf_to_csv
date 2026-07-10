from services.classifier_service import ClassifierService


class ClassificationAgent:

    @staticmethod
    def run(document):

        document.document_type = ClassifierService.classify(document)

        print()

        print("=" * 60)

        print("DOCUMENT TYPE :", document.document_type)

        print("=" * 60)

        print()

        return document
