#this is a simple template parser that will load the template from the locales folder
# and return the template string with the variables replaced.
import os


class TemplateParser:

    def __init__(self, language: str = None, default_language='en'):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language #in case of missing language, we will use the default language.
        self.language = None

        self.set_language(language)

    def set_language(self, language: str):
        if not language:
            self.language = self.default_language

        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group: str, key: str, vars: dict = {}):
        if not group or not key:
            print("❌ group or key is empty")
            return None

        group_path = os.path.join(self.current_path, "locales", self.language, f"{group}.py") # {group}.py ==> rag.py
        print("CURRENT PATH:", self.current_path)
        print("LANGUAGE:", self.language)
        print("GROUP PATH:", group_path)
        print("EXISTS:", os.path.exists(group_path))
        targeted_language = self.language
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py")
            targeted_language = self.default_language

            print("FALLBACK PATH:", group_path)
            print("FALLBACK EXISTS:", os.path.exists(group_path))

        if not os.path.exists(group_path):
            print("❌ Template file does not exist")
            return None


        # import group module ... (rag.py) ... duck typing: we will assume that the module has the key attribute.
        module = __import__(f"stores.llm.templates.locales.{targeted_language}.{group}", fromlist=[group])


        if not module:
            print("❌ Module is None")
            return None

        print("MODULE:", module)
        print("KEY:", key)
        print("HAS KEY:", hasattr(module, key))

        key_attribute = getattr(module, key)
        return key_attribute.substitute(vars) # substitute take a dictionary of variables and replaces them in the template string.
