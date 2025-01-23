# Zaraďovanie hospitalizačných prípadov do medicínskych služieb

**[ENG]** Algorithm to assign hospital stays to specific medical services within the [hospital network optimization reform](https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2021/540).

**[SK]** Informatívny algoritmus na zaraďovanie hospitalizačných prípadov k medicínskym službám podľa kategorizačnej vyhlášky. Jedná sa o technickú implementáciu [Príloh 5 - 17 vyhlášky 531/2023 Z. z.](https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2023/531#prilohy) v rámci zákona [540/2021 Z. z.](https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2021/540) o kategorizácii ústavnej zdravotnej starostlivosti a o zmene a doplnení niektorých zákonov. Viac informácií o Vyhláška nájdete na [https://sietnemocnic.sk/kategorizacna-vyhlaska](https://sietnemocnic.sk/kategorizacna-vyhlaska).

## Change log
V prípade, že identifikujete chyby v rámci kódu, prosím zaznamenajte ich na GitHub cez Issues, navrhnite priamo cez Pull Request zmenu, alebo nám napíšte email na sietnemocnic@health.gov.sk.

**Change log:**
- **v2024.0** (*21.12.2023*): Prvá verzia technickej implementácie vyhlášok pre rok 2024 publikovaná
- **v2024.1** (*28.5.2024*): Prepis technickej implementácie. Zmena názvov príloh. Zmena názvu hlavného súboru a spôsobu spúšťania.
- **v2024.2** (*1.8.2024*): Implementácia novelizácie vyhlášky 531/2023 účinnej od 1.8.2024.
- **v2025.1** (*1.1.2025*): Implementácia novelizácie vyhlášky 531/2023 účinnej od 1.1.2025

# Technické readme

## Časť 1: Základný opis programu
Skript je určený na priradenie kódov medicínskych služieb podľa vyhlášky platnej pre rok 2024.

Súčasťou skriptu sú prílohy, ktoré boli vytvorené podľa aktuálne platnej verzie vyhlášky o kategorizácii. V prípade zmien v prílohách (bez zmien v algoritme), bude potrebné vytvoriť tieto prílohy nanovo v rovnakej štruktúre a s rovnakým názvom.

## Časť 2: Práca so skriptom
Skript je napísaný v jazyku Python, na spustenie je potrebná inštalácia Python 3.0.

Program sa spustí príkazom: `python3 ./main.py cesta/k/suboru.csv`. Vstupný súbor musí mať nižšie uvedenú štruktúru. Výstupom spracovania je kópia vstupného súboru, kde ku každému riadku je pripojený zoznam nájdených medicínskych služieb. V prípade, že chýbajú niektoré povinné dáta, algoritmus vráti pre daný prípad kód ERROR. V prípade, že sa nenájde žiadna vyhovujúca medicínska služba, vráti sa prázdna hodnota.

Pri spúšťaní programu je možné pridať príznaky, ktoré ovplyvňujú, ako algoritmus jednotlivé prípady vyhodnocuje. 

`--vsetky_vykony_hlavne`, `-v` spôsobí, že algoritmus bude predpokladať, že ktorýkoľvek z vykázaných výkonov môže byť hlavný. Tento príznak je teda vhodný použiť aj v prípade, keď sa algoritmus používa na dáta z roku 2023.

`--vyhodnot_neuplne_pripady`, `-n` spôsobí, že aj v prípade, keď nie je vyplnená nejaká povinná hodnota, algoritmus pokračuje vo vyhodnocovaní daného prípadu. Bez tohto príznaku vráti hodnotu 'ERROR'.

`--ponechaj_duplicity`, `-d`: spôsobí, že vo výstupnom zozname medicínskych služieb zostanú ponechané aj duplicitné záznamy.

### Popis vstupného súboru
Vstupný súbor musí byť vo formáte csv, kde každý riadok reprezentuje jeden hospitalizačný prípad. Oddeľovačom je bodkodčiarka `;`.

Algoritmus predpokladá, že vstupný súbor je bez hlavičky, je nutné zachovať správne poradie.

Popis položiek:
| Č. | interný názov položky   | formát položky | popis položky                                                                                                                  |
|----|-------------------------|----------------|--------------------------------------------------------------------------------------------------------------------------------|
| 1  | id                      | string         | identifikátor hospitalizačného prípadu, umožňuje spätné priradenie kódu MS k HP                                                |
| 2  | vek                     | int            | vek pacienta ku dňu prijatia v rokoch, musí byť vyplnený, pre deti do 1 roka sa uvádza 0                                       |
| 3  | hmotnost                | int            | hmotnosť pacienta ku dňu prijatia v gramoch, musí byť vyplnený pre deti do 28 dní vrátane, pre ostatných pacientov sa uvádza 0 |
| 4  | umela_plucna_ventilacia | int            | počet hodín umelej pľúcnej ventilácie                                                                                          |
| 5  | diagnozy                | list\[string\] | zoznam kódov diagnóz pacienta oddelený znakom „~“, ako prvá sa uvádza hlavná diagnóza; kódy diagnóz sa uvádzajú bez bodky      |
| 6  | vykony                  | list\[string\] | zoznam kódov výkonov pacienta v tvare "kod_vykonu&lokalizacia&datum_vykonu" oddelený znakom „~“, ako prvý sa uvádza hlavný výkon; kódy výkonov sa uvádzajú bez bodky         |                                          |
| 7  | drg                     | string         | DRG skupina, do ktorej bol hospitalizačný prípad zaradený                                                                      |



# Definície z vyhlášky 
§ 5

(1) Hlavným zdravotným výkonom je zdravotný výkon, ktorý je poistencovi poskytnutý počas poskytovania ústavnej zdravotnej starostlivosti v nemocnici (ďalej len „hospitalizácia“) touto nemocnicou a pri ukončení hospitalizácie je stanovený ako jej hlavný dôvod.

(2) Ak v odseku 3 nie je ustanovené inak, medicínska služba sa určuje týmto spôsobom v tomto poradí:

a) pri poskytnutej ústavnej zdravotnej starostlivosti (ďalej len „hospitalizačný prípad“), v rámci ktorej bol vykázaný hlavný výkon zo zoznamu zdravotných výkonov uvedených v prílohe č. 17, medicínska služba sa určí podľa prílohy č. 17, inak,

b) medicínska služba sa určí podľa skupiny klasifikačného systému diagnosticko-terapeutických skupín (ďalej len „klasifikačný systém“), do ktorej je hospitalizačný prípad, na ktorý sa vzťahuje povinnosť poskytovateľa ústavnej zdravotnej starostlivosti zasielať v elektronickej podobe centru pre klasifikačný systém údaje o poskytnutej zdravotnej starostlivosti a povinnosť zdravotnej poisťovne uhrádzať zdravotnú starostlivosť podľa klasifikačného systému, zaradený alebo podľa skupiny klasifikačného systému a zdravotného výkonu alebo diagnózy podľa doplňujúceho kritéria podľa prílohy č. 5, inak,

c) ak je hospitalizačný prípad zaradený do skupiny podľa klasifikačného systému začínajúcej na písmeno „W“, medicínska služba sa určí podľa skupiny klasifikačného systému, do ktorej je hospitalizačný prípad zaradený, a diagnózy podľa prílohy č. 6, inak,

d) ak je poistencovi počas hospitalizácie poskytnutý hlavný zdravotný výkon a jeden alebo viac zdravotných výkonov zo zoznamu ďalších zdravotných výkonov podľa prílohy č. 7, medicínska služba sa určí podľa kombinácie hlavného zdravotného výkonu a vykázaného zdravotného výkonu alebo zdravotných výkonov, ak má poistenec 18 rokov alebo menej, podľa prílohy č. 7, inak,

e) ak je poistencovi počas hospitalizácie poskytnutý hlavný zdravotný výkon a jeden alebo viac zdravotných výkonov zo zoznamu ďalších zdravotných výkonov podľa prílohy č. 8, medicínska služba sa určí podľa kombinácie hlavného zdravotného výkonu a vykázaného zdravotného výkonu alebo zdravotných výkonov, ak má poistenec viac ako 18 rokov, podľa prílohy č. 8, inak,

f) ak je poistencovi počas hospitalizácie poskytnutý zdravotný výkon pri vykázanej diagnóze, ktorý zodpovedá kombinácii zdravotného výkonu a diagnózy podľa prílohy č. 9, medicínska služba sa určí podľa kombinácie hlavného zdravotného výkonu a diagnózy podľa prílohy č. 9, inak,

g) ak je poistencovi počas hospitalizácie vykázaná kombinácia hlavnej diagnózy a vedľajšej diagnózy, ktorá zodpovedá kombinácii hlavnej diagnózy a vedľajšej diagnózy podľa prílohy č. 10, medicínska služba sa určí podľa kombinácie hlavnej diagnózy a vedľajšej diagnózy podľa prílohy č. 10, inak,

h) ak má poistenec 18 rokov alebo menej a je mu počas hospitalizácie poskytnutý hlavný zdravotný výkon zo zoznamu podľa prílohy č. 12, medicínska služba sa určí podľa prílohy č. 12, inak,

i) ak má poistenec viac ako 18 rokov a je mu počas hospitalizácie poskytnutý hlavný zdravotný výkon zo zoznamu v prílohe č. 13, medicínska služba sa určí podľa prílohy č. 13, inak,

j) v prípadoch iných ako podľa písmen a) až c) a e) až h), pre poistenca vo veku 18 rokov alebo menej, sa medicínska služba určí podľa hlavnej diagnózy podľa prílohy č. 14; ak hlavná diagnóza pre hospitalizáciu nie je určená poskytovateľom zdravotnej starostlivosti, za hlavnú diagnózu sa považuje diagnóza pri prepustení poistenca, inak,

k) v hospitalizačných prípadoch iných ako podľa písmen b), d) až g) a i), pre poistencov vo veku viac ako 18 rokov, sa medicínska služba určí podľa hlavnej diagnózy podľa prílohy č. 15; ak hlavná diagnóza pre hospitalizáciu nie je určená poskytovateľom zdravotnej starostlivosti, za hlavnú diagnózu sa považuje diagnóza pri prepustení poistenca, inak,

l) hospitalizačnému prípadu, ktorému nebola určená medicínska služba podľa tohto odseku alebo odseku 3, sa určuje medicínska služba S99-99.

(3) Medicínska služba určená podľa prílohy č. 16, ktorá sa môže vykonať spolu s medicínskymi službami určenými podľa odseku 2 písm. b) až k), je medicínska služba „Identifikácia mŕtveho darcu orgánov“.
