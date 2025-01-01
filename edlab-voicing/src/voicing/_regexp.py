import re
import json

with open('.patterns', 'r') as f:
   regras = json.load(f)

test_cases = [
   "Isso é um texto [RUTRUM] com *sigla*",
   "[ABC]", 
   "quero AA me cabá no sumidô",
   "Ei ê lambá",
   "## A marquesa de Valença",
   "# A marquesa de Valença",
   "([MIS]{.smallcaps}-[rj]{.smallcaps})"
]

for caso in test_cases:
   resultado = caso
   for regra in regras:
       resultado = re.sub(regra['pattern'], regra['replacement'], resultado)
   print(f"Input: {caso}")
   print(f"Output: {resultado}\n")