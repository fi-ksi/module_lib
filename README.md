# Knihovny pro programovací moduly KSI webu

Eval skript je spuštěn v kořenovém aresáři tohoto repozitáře. Toto repo je určené
pro knihovny umožňující evaluaci programovacích modulů KSI webu.

## ksi_turtle
Jelikož knihovna turtle je silně vázaná na Tk, které je potenciálně nebezpečné,
nelze tuto knihovnu používat v našem sandboxu. Napsali jsme proto vlastní implementaci želv,
která vygeneruje seznam příkazů, které se následně provedou mimo sandbox v post processingu.

## Závislosti

* python modul Pillow
* python modul image
