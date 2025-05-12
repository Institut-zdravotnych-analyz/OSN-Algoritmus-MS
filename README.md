# Zaraďovanie hospitalizačných prípadov do medicínskych služieb

**[ENG]** Algorithm to assign hospital stays to specific medical services within the [hospital network optimization reform](https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2021/540).

**[SK]** Informatívny algoritmus na zaraďovanie hospitalizačných prípadov k medicínskym službám podľa kategorizačnej vyhlášky. Jedná sa o technickú implementáciu [Príloh 5 - 17 vyhlášky 531/2023 Z. z.](https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2023/531#prilohy) v rámci zákona [540/2021 Z. z.](https://www.slov-lex.sk/pravne-predpisy/SK/ZZ/2021/540) o kategorizácii ústavnej zdravotnej starostlivosti a o zmene a doplnení niektorých zákonov.

## Report chýb
V prípade, že identifikujete chyby v rámci kódu, prosím zaznamenajte ich na GitHub cez Issues, navrhnite priamo cez Pull Request zmenu, alebo nám napíšte email na sietnemocnic@health.gov.sk.

## Changelog
- **v2025.2** (*1.7.2025*): 
   - Implementácia novelizácie vyhlášky 531/2023 účinnej od 1.7.2025
   - Pridané vstupné stĺpce `markery` a `druh_prijatia`
   - Výroba balíčka `osn_algoritmus`
   - Nový spôsob spúšťania
   - Pridaný voliteľný parameter na špecifikáciu výstupného súboru
   - Pridané end-to-end testy
- **v2025.1** (*1.1.2025*): Implementácia novelizácie vyhlášky 531/2023 účinnej od 1.1.2025
- **v2024.2** (*1.8.2024*): Implementácia novelizácie vyhlášky 531/2023 účinnej od 1.8.2024.
- **v2024.1** (*28.5.2024*): Prepis technickej implementácie. Zmena názvov príloh. Zmena názvu hlavného súboru a spôsobu spúšťania.
- **v2024.0** (*21.12.2023*): Prvá verzia technickej implementácie vyhlášok pre rok 2024 publikovaná

# Technické readme

## Základný opis programu
Skript je určený na priradenie kódov medicínskych služieb podľa aktuálne platnej vyhlášky o kategorizácii ústavnej starostlivosti.

Implementácie starších verzií vyhlášky nájdete v časti [Releases](https://github.com/Institut-zdravotnych-analyz/OSN-Algoritmus-MS/releases)

Súčasťou repozitára sú relevantné prílohy vyhlášky v počítačovo spracovateľnej podobe.

## Práca so skriptom
Skript je napísaný v jazyku Python.

**Požiadavky:**
- Python >= 3.11

**Inštalácia:**
1. Naklonujte repozitár:
   ```bash
   git clone https://github.com/Institut-zdravotnych-analyz/OSN-Algoritmus-MS.git
   cd OSN-Algoritmus-MS
   ```
2. Nainštalujte balík pomocou pip:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install .
   ```

**Spustenie:**
Program sa spustí príkazom:
```bash
python -m osn_algoritmus [-h] [--vsetky_vykony_hlavne] [--vyhodnot_neuplne_pripady] [--ponechaj_duplicity] input_path [output_path]
```

Vstupný súbor musí mať nižšie uvedenú štruktúru. Výstupom spracovania je kópia vstupného súboru, kde ku každému riadku je pripojený stĺpec `ms` so zoznamom nájdených medicínskych služieb oddelených znakom `~`, kde prvá medicínska služba je hlavná. V prípade, že chýbajú niektoré povinné dáta (a nie je použitý príznak `-n`), algoritmus vráti pre daný prípad kód `ERROR`.

Pri spúšťaní programu je možné pridať príznaky, ktoré ovplyvňujú, ako algoritmus jednotlivé prípady vyhodnocuje.

`--vsetky_vykony_hlavne`, `-v` spôsobí, že algoritmus bude predpokladať, že ktorýkoľvek z vykázaných výkonov môže byť hlavný.

`--vyhodnot_neuplne_pripady`, `-n` spôsobí, že aj v prípade, keď nie je vyplnená nejaká povinná hodnota, algoritmus pokračuje vo vyhodnocovaní daného prípadu. Bez tohto príznaku vráti hodnotu `ERROR`.

`--ponechaj_duplicity`, `-d`: spôsobí, že vo výstupnom zozname medicínskych služieb zostanú ponechané aj duplicitné záznamy.

### Popis vstupného súboru
Vstupný súbor musí byť vo formáte csv, kde každý riadok reprezentuje jeden hospitalizačný prípad. Oddeľovačom je bodkodčiarka `;`.

Algoritmus predpokladá, že vstupný súbor je bez hlavičky, je nutné zachovať správne poradie.

Popis položiek:

| Č. | Interný názov položky   | Formát položky | Popis položky                                                                                                                                                        | Povinná položka                           |
|----|-------------------------|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| 1  | id                      | string         | Identifikátor hospitalizačného prípadu, jeho hodnota nemá vplyv na algoritmus                                                                                        | áno                                       |
| 2  | vek                     | int            | Vek pacienta ku dňu prijatia v rokoch, musí byť vyplnený, pre deti do 1 roka sa uvádza `0`                                                                           | áno                                       |
| 3  | hmotnost                | float          | Hmotnosť pacienta ku dňu prijatia v gramoch. Používaná len pre hospitalizačné prípady s vekom 0                                                                      | pre hospitalizačné prípady s vekom 0      |
| 4  | umela_plucna_ventilacia | int            | Počet hodín umelej pľúcnej ventilácie                                                                                                                                | áno                                       |
| 5  | diagnozy                | string         | Zoznam kódov diagnóz pacienta oddelený znakom `~`, ako prvá sa uvádza hlavná diagnóza. Kódy diagnóz sa uvádzajú bez bodky                                            | nie                                       |
| 6  | vykony                  | string         | Zoznam kódov výkonov pacienta v tvare `kod_vykonu&lokalizacia&datum_vykonu` oddelený znakom `~`, ako prvý sa uvádza hlavný výkon. Kódy výkonov sa uvádzajú bez bodky | nie                                       |
| 7  | markery                 | string         | Zoznam markerov pacienta v tvare `kod_markera&hodnota_markera` oddelený znakom `~`                                                                                   | nie                                       |
| 8  | drg                     | string         | DRG skupina, do ktorej bol hospitalizačný prípad zaradený                                                                                                            | nie                                       |
| 9  | druh_prijatia           | int            | Druh prijatia do ÚZZ, číslo medzi 1 a 9. (Zodpovedá položke 36 z dátového rozhrania 274*)                                                                            | pre hospitalizačné prípady s vyplneným drg|


Príklad vstupného súboru je v [`test/data/example_data_10.csv`](test/data/example_data_10.csv)

## Development

Pre nainštalovanie development a test dependencies:
```bash
pip install '.[dev]'
```
### Testovanie
Tento projekt používa `pytest` na testovanie. Viac informácii je v [`test/README.md`](test/README.md) (v angličtine).


# Definície z vyhlášky

§ 5

(1)
Hlavným zdravotným výkonom je zdravotný výkon, ktorý je poistencovi poskytnutý počas poskytovania ústavnej zdravotnej starostlivosti v nemocnici (ďalej len „hospitalizácia“) touto nemocnicou a pri ukončení hospitalizácie je stanovený ako jej hlavný dôvod, ktorý je najnáročnejším výkonom z hospitalizácie.

(2)
Ak v odseku 3 nie je ustanovené inak, medicínska služba sa určuje týmto spôsobom v tomto poradí:

a) pri poskytnutej ústavnej zdravotnej starostlivosti (ďalej len „hospitalizačný prípad“), v rámci ktorej bol vykázaný hlavný výkon zo zoznamu zdravotných výkonov uvedených v prílohe č. 17, medicínska služba sa určí podľa prílohy č. 17, inak,

b) medicínska služba sa určí podľa skupiny klasifikačného systému diagnosticko-terapeutických skupín (ďalej len „klasifikačný systém“), do ktorej je hospitalizačný prípad, na ktorý sa vzťahuje povinnosť poskytovateľa ústavnej zdravotnej starostlivosti zasielať v elektronickej podobe centru pre klasifikačný systém údaje o poskytnutej zdravotnej starostlivosti a povinnosť zdravotnej poisťovne uhrádzať zdravotnú starostlivosť podľa klasifikačného systému, zaradený alebo podľa skupiny klasifikačného systému a zdravotného výkonu alebo diagnózy podľa doplňujúceho kritéria podľa prílohy č. 5, inak,

c) ak je hospitalizačný prípad zaradený do skupiny podľa klasifikačného systému začínajúcej na písmeno „W“, medicínska služba sa určí podľa skupiny klasifikačného systému, do ktorej je hospitalizačný prípad zaradený, a diagnózy podľa prílohy č. 6, inak,

d) ak je poistencovi počas hospitalizácie poskytnutý hlavný zdravotný výkon a jeden alebo viac zdravotných výkonov zo zoznamu ďalších zdravotných výkonov podľa prílohy č. 7, medicínska služba sa určí podľa kombinácie hlavného zdravotného výkonu a vykázaného zdravotného výkonu alebo zdravotných výkonov, ak má poistenec 18 rokov alebo menej, podľa prílohy č. 7, inak,

e) ak je poistencovi počas hospitalizácie poskytnutý marker a jeden alebo viac zdravotných výkonov zo zoznamu ďalších zdravotných výkonov podľa prílohy č. 7a, medicínska služba sa určí podľa kombinácie markera a vykázaného zdravotného výkonu alebo zdravotných výkonov, ak má poistenec 18 rokov alebo menej, podľa prílohy č. 7a, inak,

f) ak je poistencovi počas hospitalizácie poskytnutý hlavný zdravotný výkon a jeden alebo viac zdravotných výkonov zo zoznamu ďalších zdravotných výkonov podľa prílohy č. 8, medicínska služba sa určí podľa kombinácie hlavného zdravotného výkonu a vykázaného zdravotného výkonu alebo zdravotných výkonov, ak má poistenec viac ako 18 rokov, podľa prílohy č. 8, inak,

g) ak je poistencovi počas hospitalizácie poskytnutý marker a jeden alebo viac zdravotných výkonov zo zoznamu ďalších zdravotných výkonov podľa prílohy č. 8a, medicínska služba sa určí podľa kombinácie markera a vykázaného zdravotného výkonu alebo zdravotných výkonov, ak má poistenec viac ako 18 rokov, podľa prílohy č. 8a, inak,

h) ak je poistencovi počas hospitalizácie poskytnutý zdravotný výkon pri vykázanej diagnóze, ktorý zodpovedá kombinácii zdravotného výkonu a diagnózy podľa prílohy č. 9, medicínska služba sa určí podľa kombinácie hlavného zdravotného výkonu a diagnózy podľa prílohy č. 9, inak,

i) ak je poistencovi počas hospitalizácie pri vykázanej diagnóze vykázaný marker, ktorý zodpovedá kombinácii markera a diagnózy podľa prílohy č. 9a, medicínska služba sa určí podľa kombinácie markera a diagnózy podľa prílohy č. 9a, inak,

j) ak je poistencovi počas hospitalizácie vykázaná kombinácia hlavnej diagnózy a vedľajšej diagnózy, ktorá zodpovedá kombinácii hlavnej diagnózy a vedľajšej diagnózy podľa prílohy č. 10, medicínska služba sa určí podľa kombinácie hlavnej diagnózy a vedľajšej diagnózy podľa prílohy č. 10, inak,

k) ak má poistenec 18 rokov alebo menej a je mu počas hospitalizácie poskytnutý hlavný zdravotný výkon zo zoznamu podľa prílohy č. 12, medicínska služba sa určí podľa prílohy č. 12, inak,

l) ak má poistenec viac ako 18 rokov a je mu počas hospitalizácie poskytnutý hlavný zdravotný výkon zo zoznamu v prílohe č. 13, medicínska služba sa určí podľa prílohy č. 13, inak,

m) v prípadoch iných ako podľa písmen a) až c) a e) až h), pre poistenca vo veku 18 rokov alebo menej, sa medicínska služba určí podľa hlavnej diagnózy podľa prílohy č. 14; ak hlavná diagnóza pre hospitalizáciu nie je určená poskytovateľom zdravotnej starostlivosti, za hlavnú diagnózu sa považuje diagnóza pri prepustení poistenca, inak,

n) v hospitalizačných prípadoch iných ako podľa písmen b), d) až g) a i), pre poistencov vo veku viac ako 18 rokov, sa medicínska služba určí podľa hlavnej diagnózy podľa prílohy č. 15; ak hlavná diagnóza pre hospitalizáciu nie je určená poskytovateľom zdravotnej starostlivosti, za hlavnú diagnózu sa považuje diagnóza pri prepustení poistenca, inak,

o) hospitalizačnému prípadu, ktorému nebola určená medicínska služba podľa tohto odseku alebo odseku 3, sa určuje medicínska služba S99-99.

(3)
Medicínska služba určená podľa prílohy č. 16, ktorá sa môže vykonať spolu s medicínskymi službami určenými podľa odseku 2 písm. b) až n), je medicínska služba „Identifikácia mŕtveho darcu orgánov“.

(4)
Zdravotné výkony, ktoré sú kategorizované v programe I. úrovne, sú zdravotné výkony jednodňovej zdravotnej starostlivosti, ktoré sú kompletne uverejňované na webovom sídle podľa osobitného predpisu;2) to neplatí pre

a) Nefrologický program I. úrovne, Program pre doliečovaciu starostlivosť I. úrovne, Program pre rehabilitačnú starostlivosť I. úrovne a

b) medicínsku službu „Neinvazívna muskuloskeletálna starostlivosť“ v Muskuloskeletálnom programe I. úrovne, medicínsku službu „Následky NCMP“ v Programe pediatrickej neurológie I. úrovne, medicínsku službu „Dlhodobá intenzívna starostlivosť“ v Programe anestéziológie a intenzívnej medicíny I. úrovne.