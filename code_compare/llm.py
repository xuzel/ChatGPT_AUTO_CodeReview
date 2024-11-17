from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import JsonOutputParser
from .prompt import *
import markdown


class LLMCodeReviewer:
    def __init__(self, model_name="llama3"):
        self.prompt_template = ChatPromptTemplate([
            ("system", io_system_prompt),
            ("user", "{code_changes}")
        ])
        self.model = OllamaLLM(model=model_name, temperature=0)
        self.chain = self.prompt_template | self.model
        self.parser = JsonOutputParser()

    def generate_review(self, code_changes):
        # Step 1: Generate review from the code change
        review = self.chain.invoke({"code_changes": code_changes})
        print("LLM Output:", review)
        # review = review.replace(" ", "")

        # Step 2: Parse the review to ensure it is a valid text response
        # review_text = self._convert_to_text(review)
        return review

    def _convert_to_text(self, review):
        # Use the JsonOutputParser to convert the review to a valid text
        try:
            review_text = self.parser.parse(review)
            if isinstance(review_text, str):
                return review_text
        except ValueError as e:
            print(f"error output: {e}")
            pass

        # If the review is not valid, regenerate with LLM
        retry_prompt = (f"System: You provided an invalid review. Please generate only a string response providing "
                        f"feedback on the code change. Do not include additional text, explanations, or characters. "
                        f"Example: 'The new import statement is unnecessary. The module is already imported earlier.' "
                        f"Original response: {review}")
        corrected_review = self.chain.invoke({"code_changes": retry_prompt})
        print("LLM Corrected Review:", corrected_review)

        # Convert the corrected review using the parser
        try:
            review_text = self.parser.parse(corrected_review)
        except BaseException as e:
            return "Review generation failed."

        if isinstance(review_text, str):
            return review_text
        else:
            raise ValueError("Failed to generate a valid review after multiple attempts.")

    def process(self, code_changes):
        return markdown.markdown(self.generate_review(code_changes))
        # return self.generate_review(code_changes)



