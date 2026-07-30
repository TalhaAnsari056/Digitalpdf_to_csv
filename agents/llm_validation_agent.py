from services.llm_validation_service import LLMValidationService


class LLMValidationAgent:

    @staticmethod
    def run(document):

        return LLMValidationService.validate(document)
