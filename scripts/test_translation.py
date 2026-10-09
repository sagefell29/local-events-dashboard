
import argostranslate.translate

text = (
    "Ontdek wat er te doen is in Delft en Rijswijk."
)

translated = argostranslate.translate.translate(
    text,
    "nl",
    "en",
)

print("Dutch: ", text)
print("English:", translated)