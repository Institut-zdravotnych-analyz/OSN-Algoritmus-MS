"""
Funkcie na vyhodnotenie jednotlivých príloh zákona 531/2023 Z. z.

Hlavnými funkicami sú funkcie nazvané priloha_x, prípadne prilohy_x_y. Tieto funkcie vždy vracajú zoznam nájdených medicínskych služieb.
"""

import re
from OSN_Algoritmus.priprava_priloh import priprav_vsetky_prilohy

tabulky = priprav_vsetky_prilohy()


def s_viacerymi_tazkymi_problemami(diagnozy):
    """
    Vyhodnocuje splnenie podmienky pre globálnu funkciu „Viaceré ťažké problémy u novorodencov“ v klasifikačnom systéme.

    Interne je táto definícia implementovaná pomocou zoznamu diagnóz zapísaného v tabuľke. Je nutné mať aspoň 2 diagnózy z tohto zoznamu.

    Args:
        diagnozy (List[str]): zoznam diagnóz

    Returns:
        bool: Splnenie "Viaceré ťažké problémy u novorodencov"
    """
    if diagnozy is None:
        return False

    pocet_tazkych_problemov = len(
        [
            d
            for d in diagnozy
            if d in tabulky["p5_tazke_problemy_u_novorodencov_diagnozy"]
        ]
    )
    return pocet_tazkych_problemov >= 2


def so_signifikantnym_vykonom(vykony):
    """
    Vyhodnocuje splnenie podmienky pre globálnu funkciu „Signifikantný operačný výkon“ v klasifikačnom systéme.

    Interne je táto definícia implementovaná pomocou zoznamu výkonov zapísaného v tabuľke.

    Args:
        vykony (List[str]): zoznam výkonov

    Returns:
        bool: Splnenie globálnej funkcie "Signifikantný operačný výkon"
    """
    return any(vykon in tabulky["p5_signifikantne_OP_vykony"] for vykon in vykony)


def splna_kriterium_podla_5(kriterium, diagnozy, vykony, hmotnost, upv):
    """
    Vyhodnotenie doplňujúcich kritérií podľa prílohy 5.

    Args:
        kriterium (str): názov kritéria
        diagnozy (List[str]): zoznam diagnóz
        vykony (Listr[str]): zoznam výkonov
        hmotnost (int): hmotnosť pacienta v gramoch
        upv (int): trvanie umelej pľúcnej ventilácie v hodinách

    Returns:
        bool: spĺňa doplňujúce kritérium
    """

    # Doplňujúce kritérium „Nekonvenčná UPV (vysokofrekvenčná, NO ventilácia)“ sa je splnené, ak mal pacient vykázaný najmenej jeden z definovaných výkonov
    if kriterium == "Nekonvenčná UPV (vysokofrekvenčná, NO ventilácia)":
        return any(
            vykon in tabulky["p5_kriterium_nekonvencna_upv_vykony"] for vykon in vykony
        )

    # Doplňujúce kritérium „Riadená hypotermia“ je splnené, ak mal pacient vykázaný najmenej jeden z definovaných výkonov
    if kriterium == "Riadená hypotermia":
        return any(
            vykon in tabulky["p5_kriterium_riadena_hypotermia_vykony"]
            for vykon in vykony
        )

    # Doplňujúce kritérium „Paliatívna starostlivosť u novorodencov“ je splnené, ak mal pacient vykázanú najmenej jednu z definovaných diagnóz
    if kriterium == "Paliatívna starostlivosť u novorodencov":
        return diagnozy is not None and any(
            diagnoza in tabulky["p5_kriterium_paliativna_starostlivost_diagnozy"]
            for diagnoza in diagnozy
        )

    # Doplňujúce kritérium „Potreba výmennej transfúzie“ je splnené, ak mal pacient vykázaný najmenej jeden z definovaných výkonov
    if kriterium == "Potreba výmennej transfúzie":
        return any(
            vykon in tabulky["p5_kriterium_potreba_vymennej_transfuzie_vykony"]
            for vykon in vykony
        )

    # Doplňujúce kritérium „Akútny pôrod novorodenca v prípade ohrozenia života bez ohľadu na gestačný vek a hmotnosť” je splnené, ak mal pacient vykázaný aj tento výkon: 93083, Akútny pôrod novorodenca v prípade ohrozenia života
    if (
        kriterium
        == "Akútny pôrod novorodenca v prípade ohrozenia života bez ohľadu na gestačný vek a hmotnosť"
    ):
        return "93083" in vykony

    # Doplňujúce kritérium „Novorodenec pod hranicou viability (< 24 týždeň alebo < 500 g)” je splnené, ak mal hospitalizovaný pacient hmotnosť menej ako 500g alebo gestačný vek nižší ako 24 týždňov.
    # Gestačný vek aktuálne nie je možné z dát zistiť, kontrolujeme iba hmotnosť.
    if kriterium == "Novorodenec pod hranicou viability (< 24 týždeň alebo < 500 g)":
        return hmotnost is not None and hmotnost < 500

    # Doplňujúce kritérium „So signifikantným OP výkonom“ je splnené, ak hospitalizačný prípad pacienta splnil podmienky pre globálnu funkciu „Signifikantný operačný výkon“ v klasifikačnom systéme.
    if kriterium == "So signifikantným OP výkonom":
        return so_signifikantnym_vykonom(vykony)

    # Doplňujúce kritérium „Bez signifikantného OP výkonu, s UPV > 95 hodín, s viacerými ťažkými problémami“ je splnené, ak hospitalizačný prípad pacienta nesplnil podmienky pre globálnu funkciu „Signifikantný operačný výkon“ v klasifikačnom systéme, ale dĺžka umelej pľúcnej ventilácie poskytnutej počas hospitalizácie v súlade s pravidlami kódovania pre umelú pľúcnu ventiláciu bola vyššia ako 95 hodín a hospitalizačný prípad splnil podmienky pre globálnu funkciu „Viaceré ťažké problémy u novorodencov“ v klasifikačnom systéme.
    if (
        kriterium
        == "Bez signifikantného OP výkonu, s UPV > 95 hodín, s viacerými ťažkými problémami"
    ):
        return (
            not so_signifikantnym_vykonom(vykony)
            and upv is not None
            and upv > 95
            and s_viacerymi_tazkymi_problemami(diagnozy)
        )

    # Doplňujúce kritérium „Bez signifikantného OP výkonu a bez UPV > 95 hodín a viacerých ťažkých problémov“ je splnené, ak hospitalizačný prípad pacienta nesplnil podmienky pre globálnu funkciu „Signifikantný operačný výkon“ v klasifikačnom systéme a zároveň dĺžka umelej pľúcnej ventilácie poskytnutej počas hospitalizácie v súlade s pravidlami kódovania pre umelú pľúcnu ventiláciu nebola vyššia ako 95 hodín alebo hospitalizačný prípad nesplnil podmienky pre globálnu funkciu „Viaceré ťažké problémy u novorodencov“ v klasifikačnom systéme.
    if (
        kriterium
        == "Bez signifikantného OP výkonu a bez UPV > 95 hodín a viacerých ťažkých problémov"
    ):
        return not so_signifikantnym_vykonom(vykony) and (
            (upv is not None and upv <= 95)
            or not s_viacerymi_tazkymi_problemami(diagnozy)
        )


def priloha_5(hmotnost, upv, diagnozy, vykony, drg):
    """
    Medicínska služba sa určí podľa skupiny klasifikačného systému, do ktorej bol hospitalizačný prípad zaradený alebo podľa skupiny klasifikačného systému a zdravotného výkonu alebo diagnózy podľa doplňujúceho kritéria (NOV).

    Args:
        hmotnost (int): hmotnosť poistenca v gramoch
        upv (int): doba umelej pľúcnej ventilácie v hodinách
        diagnozy (List[str]): zoznam diagnóz
        vykony (List[str]): zoznam výkonov
        drg (str): skupina klasifikačného systému DRG

    Returns:
        List[str]: Zoznam priradených medicínskych služieb
    """

    return [
        line["kod_ms"]
        for line in tabulky["p5_NOV"]
        if drg.startswith(line["drg"])
        and (
            not line["doplnujuce_kriterium"]
            or splna_kriterium_podla_5(
                line["doplnujuce_kriterium"],
                diagnozy,
                vykony,
                hmotnost,
                upv,
            )
        )
    ]


def s_kraniocerebralnou_traumou(diagnozy):
    """
    Diagnóza patrí do skupiny diagnóz „Kraniocerebrálna trauma“, ak mal poistenec vykázanú najmenej jednu diagnózu s kódom začínajúcim v rozsahu kódov diagnóz „S02“ až „S09“.

    Args:
        diagnozy (List[str]): zoznam diagnóz

    Returns:
        bool: aspoň 1 z diagnóz je v rozsahu kódov diagnóz „S02“ až „S09“
    """
    return any(
        diagnoza[:3] in ["s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09"]
        for diagnoza in diagnozy
    )


def splna_kriterium_podla_6(kriterium, diagnozy):
    """
    Diagnóza musí zodpovedať stĺpcu skupiny diagnóz.

    Aktuálne sú 2 skupiny: „Kraniocerebrálna trauma“ a "bez diagnózy Kraniocerebrálna trauma".

    Args:
        kriterium (_type_): názov kritéria
        diagnozy (_type_): zoznam diagnóz

    Returns:
        bool: spĺňa kritérium skupiny diagnóz
    """
    if kriterium == "Kraniocerebrálna trauma":
        return s_kraniocerebralnou_traumou(diagnozy)

    if kriterium == "bez diagnózy Kraniocerebrálna trauma":
        return not s_kraniocerebralnou_traumou(diagnozy)


def priloha_6(drg, diagnozy, je_dieta):
    """
    Ak bol hospitalizačný prípad poistenca zaradený podľa klasifikačného systému do skupiny podľa stĺpca "Skupina klasifikačného systému" pri diagnóze zodpovedajúcej stĺpcu „skupina diagnóz“, hospitalizácii sa určí medicínska služba podľa stĺpca "medicínska služba" (DRGD).

    Napr.
    Skupina klasifikačného systému: Skupina klasifikačného systému začínajúca na „W“
    Skupina diagnóz: Kraniocerebrálna trauma
    Medicínska služba: Polytrauma s kraniocerebrálnou traumou (S02-01)

    Rozdelené podľa veku.

    Args:
        drg (str): skupina klasifikačného systému DRG
        diagnozy (List[str]): zoznam diagnóz
        je_dieta (bool): poistenec vo veku 18 rokov a menej

    Returns:
        List[str]: Zoznam priradených medicínskych služieb
    """
    nazov_tabulky = "p6_DRGD_deti" if je_dieta else "p6_DRGD_dospeli"

    return [
        line["kod_ms"]
        for line in tabulky[nazov_tabulky]
        if drg.startswith(line["drg"])
        and splna_kriterium_podla_6(line["doplnujuce_kriterium"], diagnozy)
    ]


def poskytnuty_vedlajsi_vykon(vykony, skupina_vykonov, nazov_tabulky):
    """
    Bol vykázaný minimálne jeden výkon z uvedenej skupiny výkonov.

    Args:
        vykony (List[str]): zoznam výkonov
        skupina_vykonov (str): skupina výkonov podľa hlavného výkonu
        nazov_tabulky (str): názov tabuľky, v ktorej sa nachádzajú prislúchajúce skupiny výkonov

    Returns:
        bool: aspoň jeden vykázaný výkon sa nachádza v uvedenej skupine výkonov.
    """
    cielove_vykony = [
        vykon["kod_vykonu"]
        for vykon in tabulky[nazov_tabulky]
        if vykon["kod_ms"] == skupina_vykonov
    ]

    return any(vykon in cielove_vykony for vykon in vykony)


def prilohy_7_8(vykony, je_dieta, vsetky_vykony_hlavne):
    """
    Ak bol poistencovi poskytnutý hlavný zdravotný výkon podľa stĺpca "zdravotný výkon" a minimálne jeden výkon z uvedených výkonov (VV, kombinácia Výkon - Výkon).

    Hlavné výkony sú v tabuľkách p7_VV_deti a p8_VV_dospelí.
    Vedľajšie výkony sa kontrolujú z tabuliek p7_vedlajsie_vykony a p8_vedlajsie_vykony podľa parametru skupina_vedlajsich_vykonov.

    Args:
        vykony (List[str]): zoznam výkonov
        je_dieta (bool): poistenec vo veku 18 rokov a menej
        vsetky_vykony_hlavne (bool): skúša všetky možné hlavné výkony

    Returns:
        List[str]: Zoznam priradených medicínskych služieb
    """
    nazov_tabulky = "p7_VV_deti" if je_dieta else "p8_VV_dospeli"
    nazov_vedlajsej_tabulky = (
        "p7_vedlajsie_vykony" if je_dieta else "p8_vedlajsie_vykony"
    )

    hlavny_vykon = vykony[0]
    if not vsetky_vykony_hlavne and not hlavny_vykon:
        return []
    vedlajsie_vykony = vykony[1:]

    out = [
        line["kod_ms"]
        for line in tabulky[nazov_tabulky]
        if line["kod_hlavneho_vykonu"] == hlavny_vykon
        and poskytnuty_vedlajsi_vykon(
            vedlajsie_vykony,
            line["kod_ms"],
            nazov_vedlajsej_tabulky,
        )
    ]

    if vsetky_vykony_hlavne:
        for i, hlavny_vykon in enumerate(vykony[1:]):
            vedlajsie_vykony = vykony[: i + 1] + vykony[i + 2 :]
            out.extend(
                [
                    line["kod_ms"]
                    for line in tabulky[nazov_tabulky]
                    if line["kod_hlavneho_vykonu"] == hlavny_vykon
                    and poskytnuty_vedlajsi_vykon(
                        vedlajsie_vykony,
                        line["kod_ms"],
                        nazov_vedlajsej_tabulky,
                    )
                ]
            )

    return out


def splna_diagnoza_zo_skupiny_podla_9(hlavna_diagnoza, skupina_diagnoz):
    """
    Kontroluj, či prípad má hlavnú diagnózu patriacu skupine definovaných diagnóz.

        Args:
            hlavna_diagnoza (List[str]): hlavná diagnóza hospitalizačného prípadu
            skupina_diagnoz (str): Názov skupiny diagnóz podľa prílohy 9
            je_dieta (bool): poistenec vo veku 18 rokov a menej

        Returns:
            bool: hlavná diagnóza je z uvedenej skupiny diagnóz
    """
    cielove_diagnozy = [
        line["kod_hlavnej_diagnozy"]
        for line in tabulky["p9_skupiny_diagnoz"]
        if line["skupina_diagnoz"] == skupina_diagnoz
    ]

    return any(
        hlavna_diagnoza.startswith(cielova_diagnoza)
        for cielova_diagnoza in cielove_diagnozy
    )


def priloha_9(diagnozy, vykony, je_dieta, vsetky_vykony_hlavne):
    """
    Ak bol poistencovi poskytnutý hlavný zdravotný výkon podľa stĺpca "názov zdravotného výkonu" pri hlavnej diagnóze zo skupiny diagnóz podľa stĺpca „Skupina diagnóz“, hospitalizácii sa určí medicínska služba podľa stĺpca "Názov medicínskej služby" (VD).

    Args:
        diagnozy (List[str]): zoznam diagnóz
        vykony (List[str]): zoznam výkonov
        je_dieta (bool): poistenec vo veku 18 rokov a menej
        vsetky_vykony_hlavne (bool): skúša všetky možné hlavné výkony

    Returns:
        List[str]: zoznam priradených medicínskych služieb
    """
    nazov_tabulky = "p9_VD_deti" if je_dieta else "p9_VD_dospeli"

    hlavny_vykon = vykony[0]
    if not vsetky_vykony_hlavne and not hlavny_vykon:
        return []

    hlavna_diagnoza = diagnozy[0]

    out = [
        line["kod_ms"]
        for line in tabulky[nazov_tabulky]
        if line["kod_hlavneho_vykonu"] == hlavny_vykon
        and splna_diagnoza_zo_skupiny_podla_9(hlavna_diagnoza, line["skupina_diagnoz"])
    ]

    if vsetky_vykony_hlavne:
        for hlavny_vykon in vykony[1:]:
            out.extend(
                [
                    line["kod_ms"]
                    for line in tabulky[nazov_tabulky]
                    if line["kod_hlavneho_vykonu"] == hlavny_vykon
                    and splna_diagnoza_zo_skupiny_podla_9(
                        hlavna_diagnoza, line["skupina_diagnoz"]
                    )
                ]
            )

    return out


def priloha_10(diagnozy):
    """
    Ak bola poistencovi pri hospitalizácii vykázaná hlavná diagnóza podľa stĺpca „skupina diagnóz pre hlavnú diagnózu“ a vedľajšia diagnóza podľa stĺpca „názov vedľajšej diagnózy“, hospitalizácii sa určí medicínska služba podľa stĺpca "medicínska služba" (DD).

    Args:
        diagnozy (List[str]): zoznam diagnóz

    Returns:
        List[str]: zoznam medicínskych služieb
    """
    return [
        line["kod_ms"]
        for line in tabulky["p10_DD"]
        if line["kod_hlavnej_diagnozy"] == diagnozy[0]
        and line["kod_vedlajsej_diagnozy"] in diagnozy[1:]
    ]


def ms_podla_hlavneho_vykonu(vykony, nazov_tabulky, vsetky_vykony_hlavne):
    """
    Vráť zoznam medicínskych služieb podľa vykázaného hlavného výkonu.

    Mechanizmus použitý v prílohách 12, 13 a 17.

    Args:
        vykony (List[str]): zoznam výkonov
        nazov_tabulky (bool): názov tabuľky, v ktorej sú definované medicínske služby
        vsetky_vykony_hlavne (bool): skúša všetky možné hlavné výkony

    Returns:
        List[str]: zoznam medicínskych služieb
    """

    hlavny_vykon = vykony[0]
    if not vsetky_vykony_hlavne and not hlavny_vykon:
        return []

    out = [
        line["kod_ms"]
        for line in tabulky[nazov_tabulky]
        if line["kod_hlavneho_vykonu"] == hlavny_vykon
    ]

    if vsetky_vykony_hlavne:
        for hlavny_vykon in vykony[1:]:
            out.extend(
                [
                    line["kod_ms"]
                    for line in tabulky[nazov_tabulky]
                    if line["kod_hlavneho_vykonu"] == hlavny_vykon
                ]
            )

    return out


def prilohy_12_13(vykony, je_dieta, vsetky_vykony_hlavne):
    """
    Ak bol poistencovi poskytnutý hlavný zdravotný výkon podľa stĺpca "zdravotný výkon", hospitalizácii sa určí medicínska služba podľa stĺpca "medicínska služba" (V).

    Rozdelené podľa veku.

    Args:
        vykony (List[str]): zoznam výkonov
        je_dieta (bool): poistenec vo veku 18 rokov a menej
        vsetky_vykony_hlavne (bool): skúša všetky možné hlavné výkony

    Returns:
        List[str]: zoznam medicínskych služieb
    """
    nazov_tabulky = "p12_V_deti" if je_dieta else "p13_V_dospeli"

    return ms_podla_hlavneho_vykonu(vykony, nazov_tabulky, vsetky_vykony_hlavne)


def prilohy_14_15(diagnozy, je_dieta):
    """Ak bola poistencov pri hospitalizácii vykázaná hlavná diagnóza podľa stĺpca "hlavná diagnóza", hospitalizácii sa určí medicínska služba podľa stĺpca "medicínska služba" (D).

    Rozdelené podľa veku.

    Args:
        diagnozy (List[str]): zoznam diagnóz
        je_dieta (bool): pacient vo veku 18 rokov a menej

    Returns:
        List[str]: Zoznam medicínskych služieb
    """
    nazov_tabulky = "p14_D_deti" if je_dieta else "p15_D_dospeli"

    return [
        line["kod_ms"]
        for line in tabulky[nazov_tabulky]
        if line["kod_hlavnej_diagnozy"] == diagnozy[0]
    ]


def priloha_16(diagnozy):
    """
    Medicínska služba „Identifikácia mŕtveho darcu orgánov“ (S17-22) sa určí, ak je pri hospitalizačnom prípade vykázaná aspoň jedna diagnóza zo skupiny diagnóz „Kóma“ a súčasne aspoň jedna diagnóza zo skupiny „Opuch mozgu“ a súčasne aspoň jedna z diagnóz so skupiny „Vybrané ochorenia mozgu“ (S)

    Args:
        diagnozy (List[str]): Zoznam diagnóz hospitalizačného prípadu.

    Returns:
        [List[str]]: Zoznam medicínskych služieb.
    """

    kod_ms = "S17-22"
    nazvy_zoznamov_diagnoz = [
        "p16_koma_diagnozy",
        "p16_opuch_mozgu_diagnozy",
        "p16_vybrane_ochorenia_diagnozy",
    ]

    for cielovy_zoznam in nazvy_zoznamov_diagnoz:
        if not any(
            cielova_diagnoza in diagnozy for cielova_diagnoza in tabulky[cielovy_zoznam]
        ):
            return []
    return [kod_ms]


def priloha_17(vykony, vsetky_vykony_hlavne):
    """
    V hospitalizačných prípadoch, v ktorých bol vykázaný hlavný výkon podľa stĺpca "zdravotný výkon", hospitalizácii sa určí medicínska služba podľa stĺpca "medicínska služba".

    Jedná sa o špeciálne prípady, kedy HP dobre nezapadá do aktuálneho nastavenie medicínskych služieb.

    Príloha 17 má prednosť pred ostatnými prílohami.

    Zdieľa mechanizmus vyhodnocovania s prílohami 12 a 13.

    Args:
        vykony (List[str]): Zoznam výkonov hospitalizačného prípadu.
        vsetky_vykony_hlavne (bool): skúša všetky možné hlavné výkony

    Returns:
        [List[str]]: Zoznam medicínskych služieb.
    """
    return ms_podla_hlavneho_vykonu(vykony, "p17", vsetky_vykony_hlavne)


def prirad_ms(hp, vsetky_vykony_hlavne):
    """Vyhodnoť všetky prílohy a vytvor zoznam medicínskych služieb priraditeľných k hospitalizačnému prípadu.

    Príloha sa vyhodnocuje, iba pokiaľ hospitalizačný prípad má vyplnené polia nutné pre vyhodnotenie prílohy.

    Ako prvá sa vyhodnocuje príloha 17 s analytickými medicínskymi službami.

    Pokiaľ hospitalizačný prípad nezapadá do žiadnej medicínskej služby podľa príloh, je mu priradená služba S99-99.

    Args:
        hp (dict): hospitalizačný prípad
        vsetky_vykony_hlavne (bool): skúša všetky možné hlavné výkony

    Returns:
        List[str]: zoznam medicínskych služieb
    """
    services = []

    je_dieta = hp["vek"] is not None and hp["vek"] <= 18

    if hp["vykony"]:
        services.extend(priloha_17(hp["vykony"], vsetky_vykony_hlavne))

    if hp["drg"]:
        services.extend(
            priloha_5(
                hp["hmotnost"],
                hp["umela_plucna_ventilacia"],
                hp["diagnozy"],
                hp["vykony"],
                hp["drg"],
            )
        )

    if hp["drg"] and hp["vek"] is not None and hp["diagnozy"]:
        services.extend(priloha_6(hp["drg"], hp["diagnozy"], je_dieta))

    if hp["vek"] is not None and hp["vykony"]:
        services.extend(prilohy_7_8(hp["vykony"], je_dieta, vsetky_vykony_hlavne))

    if hp["vek"] is not None and hp["diagnozy"] and hp["vykony"]:
        services.extend(
            priloha_9(hp["diagnozy"], hp["vykony"], je_dieta, vsetky_vykony_hlavne)
        )

    if hp["diagnozy"]:
        services.extend(priloha_10(hp["diagnozy"]))

    if hp["vek"] is not None and hp["vykony"]:
        services.extend(prilohy_12_13(hp["vykony"], je_dieta, vsetky_vykony_hlavne))

    if hp["vek"] is not None and hp["diagnozy"]:
        services.extend(prilohy_14_15(hp["diagnozy"], je_dieta))

    if hp["diagnozy"]:
        services.extend(priloha_16(hp["diagnozy"]))

    if not services:
        services = ["S99-99"]

    return services
