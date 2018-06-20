from translate import Translator

translator= Translator(to_lang="es")

phrase = "Hello my friend!"

translation = translator.translate(phrase)

print phrase

print translation
