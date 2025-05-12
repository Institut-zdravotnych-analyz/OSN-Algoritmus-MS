"""Functions related to evaluation of prilohy vyhlášky 531/2023 Z. z.

Main functions are named priloha_x or prilohy_x_y. These functions always return a list of assigned medicinske sluzby.
"""

from collections.abc import Callable

from osn_algoritmus.models import HospitalizacnyPripad, Marker
from osn_algoritmus.prilohy_preparation import prepare_tables

tables = prepare_tables()


def s_viacerymi_tazkymi_problemami(hp: HospitalizacnyPripad) -> bool:
    """Evaluate globálna funkcia "Viaceré ťažké problémy u novorodencov" v klasifikačnom systéme for hp.

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp "splnil podmienky pre globálnu funkciu „Viaceré ťažké problémy u novorodencov“."

    """
    tazke_problemy = {line["kod_diagnozy"] for line in tables["p5_tazke_problemy_u_novorodencov"]}
    pocet_tazkych_problemov = sum(1 for d in hp.diagnozy if d in tazke_problemy)
    return pocet_tazkych_problemov >= 2


def so_signifikantnym_vykonom(hp: HospitalizacnyPripad) -> bool:
    """Evaluate globálna funkcia "Signifikantný operačný výkon" v klasifikačnom systéme for hp.

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp "splnil podmienky pre globálnu funkciu „Signifikantný operačný výkon“."

    """
    return any(line["kod_vykonu"] in hp.vykony for line in tables["p5_signifikantne_OP"])


def kriterium_nekonvencna_upv(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „Nekonvenčná UPV (vysokofrekvenčná, NO ventilácia)“ for hp.

    Vyhláška:
    Doplňujúce kritérium „Nekonvenčná UPV (vysokofrekvenčná, NO ventilácia)“ sa je splnené, ak mal pacient vykázaný
    najmenej jeden z týchto výkonov:
        - 8p107 Vysokofrekvenčná ventilácia
        - 8p133 Inhalačná aplikácia oxidu dusnatého

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „Nekonvenčná UPV (vysokofrekvenčná, NO ventilácia)“.

    """
    return any(vykon in hp.vykony for vykon in ["8p107", "8p133"])


def kriterium_riadena_hypotermia(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „Riadená hypotermia“ for hp.

    Vyhláška:
    Doplňujúce kritérium „Riadená hypotermia“ je splnené, ak mal pacient vykázaný najmenej jeden z týchto výkonov:
        - 8q902 Aktívne kontrolované chladenie po resuscitácii, terapeutická hypotermia

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „Riadená hypotermia“.

    """
    return "8q902" in hp.vykony


def kriterium_paliativna_starostlivost(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „Paliatívna starostlivosť u novorodencov“ for hp.

    Vyhláška:
    Doplňujúce kritérium „Paliatívna starostlivosť u novorodencov“ je splnené, ak mal pacient vykázanú najmenej jednu z
    týchto diagnóz:
        - Z515 Paliatívna starostlivosť

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „Paliatívna starostlivosť u novorodencov“.

    """
    return "z515" in hp.diagnozy


def kriterium_potreba_vymennej_transfuzie(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „Potreba výmennej transfúzie“ for hp.

    Vyhláška:
    Doplňujúce kritérium „Potreba výmennej transfúzie“ je splnené, ak mal pacient vykázaný najmenej jeden z týchto
    výkonov:
        - 8r2637 Výmenná transfúzia u novorodencov

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „Potreba výmennej transfúzie“.

    """
    return "8r2637" in hp.vykony


def kriterium_akutny_porod(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „Akútny pôrod novorodenca v prípade ohrozenia života bez ohľadu na gestačný vek a hmotnosť“ for hp.

    Vyhláška:
    Doplňujúce kritérium „Akútny pôrod novorodenca v prípade ohrozenia života bez ohľadu na gestačný vek a hmotnosť"
    je splnené, ak mal pacient vykázaný aj tento výkon:
        - 93083	Akútny pôrod novorodenca v prípade ohrozenia života

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „Akútny pôrod novorodenca v prípade ohrozenia života bez ohľadu na gestačný
        vek a hmotnosť“.

    """  # noqa: E501
    return "93083" in hp.vykony


def kriterium_marker_nemoznost_transportu(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „Marker - nemožnosť transportu novorodenca z medicínskych príčin na vyššie pracovisko“ for hp.

    Vyhláška:
    Doplňujúce kritérium „Marker - nemožnosť transportu novorodenca z medicínskych príčin na vyššie pracovisko“ je
    splnené, ak mal pacient vykázaný aj marker a hodnotu markera:
        - Kód markera: mOSN
        - Hodnota markera: novor

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „Marker - nemožnosť transportu novorodenca z medicínskych príčin na vyššie
        pracovisko“.

    """
    return Marker(kod="mOSN", hodnota="novor") in hp.markery


def kriterium_vykon_8p1007_upv_menej_96_hod(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „Výkon 8p1007 s dobou UPV nižšiou ako 96 hodín“ for hp.

    Vyhláška:
    Doplňujúce kritérium „Výkon 8p1007 s dobou UPV nižšiou ako 96 hodín“ je splnené, ak hospitalizačný prípad pacienta
    splnil podmienku dĺžka umelej pľúcnej ventilácie poskytnutej počas hospitalizácie v súlade s pravidlami kódovania
    pre umelú pľúcnu ventiláciu bola nižšia ako 96 hodín a zároveň ak mal pacient vykázaný aj tento výkon:
        - 8p1007 Neinvazívna ventilácia u novorodencov

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „Výkon 8p1007 s dobou UPV nižšiou ako 96 hodín“.

    """
    return "8p1007" in hp.vykony and hp.upv is not None and hp.upv < 96


def kriterium_pod_hranicou_viability(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „Novorodenec pod hranicou viability (< 24 týždeň alebo < 500 g)“ for hp.

    Vyhláška
    Doplňujúce kritérium „Novorodenec pod hranicou viability (< 24 týždeň alebo < 500 g)” je splnené, ak mal
    hospitalizovaný pacient hmotnosť menej ako 500g alebo gestačný vek nižší ako 24 týždňov. Gestačný vek nižší ako 24
    týždňov sa určuje výkázaním markera a hodnotou markera:
        - Kód markera: mGVK
        - Hodnota markera: 1 - 46

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „Novorodenec pod hranicou viability (< 24 týždeň alebo < 500 g)“.

    """
    pod_500g = hp.hmotnost is not None and hp.hmotnost < 500
    nizsi_gest_vek = any(m.kod == "mGVK" and 1 <= int(m.hodnota) <= 46 for m in hp.markery)
    return pod_500g or nizsi_gest_vek


def kriterium_so_signifikantnym_op_vykonom(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „So signifikantným OP výkonom“ for hp.

    Vyhláška:
    Doplňujúce kritérium „So signifikantným OP výkonom“ je splnené, ak hospitalizačný prípad pacienta splnil podmienky
    pre globálnu funkciu „Signifikantný operačný výkon“ v klasifikačnom systéme.

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „So signifikantným OP výkonom“.

    """
    return so_signifikantnym_vykonom(hp)


def kriterium_bez_signifikantneho_op_s_upv_viac_95_hod_viacere_tazke_problemy(hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium „Bez signifikantného OP výkonu, s UPV > 95 hodín, s viacerými ťažkými problémami“ for hp.

    Vyhláška:
    Doplňujúce kritérium „Bez signifikantného OP výkonu, s UPV > 95 hodín, s viacerými ťažkými problémami“ je splnené,
    ak hospitalizačný prípad pacienta nesplnil podmienky pre globálnu funkciu „Signifikantný operačný výkon“ v
    klasifikačnom systéme, ale dĺžka umelej pľúcnej ventilácie poskytnutej počas hospitalizácie v súlade s pravidlami
    kódovania pre umelú pľúcnu ventiláciu bola vyššia ako 95 hodín a hospitalizačný prípad splnil podmienky pre globálnu
    funkciu „Viaceré ťažké problémy u novorodencov“ v klasifikačnom systéme.

    Args:
        hp: HospitalizacnyPripad

    Returns:
        True, if the hp fulfills kriterium „Bez signifikantného OP výkonu, s UPV > 95 hodín, s viacerými ťažkými
        problémami“.

    """
    bez_signifikantneho_op = not so_signifikantnym_vykonom(hp)
    s_upv_gt_95 = hp.upv is not None and hp.upv > 95
    return bez_signifikantneho_op and s_upv_gt_95 and s_viacerymi_tazkymi_problemami(hp)


def kriterium_bez_signifikantneho_op_bez_upv_viac_95_hod_a_viacerych_tazkych_problemov(
    hp: HospitalizacnyPripad,
) -> bool:
    """Evaluate kritérium „Bez signifikantného OP výkonu a bez UPV > 95 hodín a viacerých ťažkých problémov“ for hp.

    Vyhláška:
    Doplňujúce kritérium „Bez signifikantného OP výkonu a bez UPV > 95 hodín a viacerých ťažkých problémov“ je splnené,
    ak hospitalizačný prípad pacienta nesplnil podmienky pre globálnu funkciu „Signifikantný operačný výkon“ v
    klasifikačnom systéme a zároveň dĺžka umelej pľúcnej ventilácie poskytnutej počas hospitalizácie v súlade s
    pravidlami kódovania pre umelú pľúcnu ventiláciu nebola vyššia ako 95 hodín alebo hospitalizačný prípad nesplnil
    podmienky pre globálnu funkciu „Viaceré ťažké problémy u novorodencov“ v klasifikačnom systéme.

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium „Bez signifikantného OP výkonu a bez UPV > 95 hodín a viacerých ťažkých
        problémov“.

    """
    nesplnil_so_signifikantnym_op = not so_signifikantnym_vykonom(hp)
    bez_upv_viac_ako_95_hod = hp.upv is not None and not hp.upv > 95
    nesplnil_s_viacerymi_tazkymi_problemami = not s_viacerymi_tazkymi_problemami(hp)
    return nesplnil_so_signifikantnym_op and (bez_upv_viac_ako_95_hod or nesplnil_s_viacerymi_tazkymi_problemami)


def splna_kriterium_podla_5(kriterium: str, hp: HospitalizacnyPripad) -> bool:
    """Evaluate kritérium from priloha 5 for hp.

    Args:
        kriterium: Kriterium name
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium from priloha 5.

    """
    kriteria_logic = {
        "Nekonvenčná UPV (vysokofrekvenčná, NO ventilácia)": kriterium_nekonvencna_upv,
        "Riadená hypotermia": kriterium_riadena_hypotermia,
        "Paliatívna starostlivosť u novorodencov": kriterium_paliativna_starostlivost,
        "Potreba výmennej transfúzie": kriterium_potreba_vymennej_transfuzie,
        "Akútny pôrod novorodenca v prípade ohrozenia života bez ohľadu na gestačný vek a hmotnosť": kriterium_akutny_porod,  # noqa: E501
        "Marker - nemožnosť transportu novorodenca z medicínskych príčin na vyššie pracovisko": kriterium_marker_nemoznost_transportu,  # noqa: E501
        "Výkon 8p1007 s dobou UPV nižšiou ako 96 hodín": kriterium_vykon_8p1007_upv_menej_96_hod,
        "Novorodenec pod hranicou viability (< 24 týždeň alebo < 500 g)": kriterium_pod_hranicou_viability,
        "So signifikantným OP výkonom": kriterium_so_signifikantnym_op_vykonom,
        "Bez signifikantného OP výkonu, s UPV > 95 hodín, s viacerými ťažkými problémami": kriterium_bez_signifikantneho_op_s_upv_viac_95_hod_viacere_tazke_problemy,  # noqa: E501
        "Bez signifikantného OP výkonu a bez UPV > 95 hodín a viacerých ťažkých problémov": kriterium_bez_signifikantneho_op_bez_upv_viac_95_hod_a_viacerych_tazkych_problemov,  # noqa: E501
    }
    if kriterium in kriteria_logic:
        return kriteria_logic[kriterium](hp)
    return False


def priloha_5(hp: HospitalizacnyPripad) -> list[str]:
    """Assign medicinske sluzby according to priloha 5.

    Vyhláška:
    Medicínska služba sa určí podľa vykázania druhu prijatia do ÚZZ s hodnotou "3 - 6" a skupiny klasifikačného systému,
    do ktorej bol hospitalizačný prípad zaradený alebo druhu prijatia do ÚZZ s hodnotou "3 - 6" a podľa skupiny
    klasifikačného systému a zdravotného výkonu alebo diagnózy podľa doplňujúceho kritéria (NOV).

    Args:
        hp: Hospitalizacny pripad

    Returns:
        List of assigned medicinske sluzby

    """
    if hp.druh_prijatia is None or not 3 <= hp.druh_prijatia <= 6 or hp.drg is None:
        return []

    return [
        line["kod_ms"]
        for line in tables["p5_NOV"]
        if hp.drg.startswith(line["drg"])
        and (line["doplnujuce_kriterium"] == "" or splna_kriterium_podla_5(line["doplnujuce_kriterium"], hp))
    ]


def s_kraniocerebralnou_traumou(hp: HospitalizacnyPripad) -> bool:
    """Evaluate if hp had kraniocerebralna trauma.

    Vyhláška:
    Diagnóza patrí do skupiny diagnóz "Kraniocerebrálna trauma", ak mal poistenec vykázanú najmenej jednu diagnózu s
    kódom začínajúcim v rozsahu kódov diagnóz "S02" až "S09".

    Args:
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp had kraniocerebralna trauma

    """
    return any(diagnoza[:3] in ["s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09"] for diagnoza in hp.diagnozy)


def splna_kriterium_podla_6(kriterium: str, hp: HospitalizacnyPripad) -> bool:
    """Evaluate if hp fulfills kriterium from priloha 6.

    Args:
        kriterium: Kriterium name
        hp: Hospitalizacny pripad

    Returns:
        True, if the hp fulfills kriterium

    """
    if kriterium == "diagnózy Kraniocerebrálna trauma":
        return s_kraniocerebralnou_traumou(hp)

    if kriterium == "bez diagnózy Kraniocerebrálna trauma":
        return not s_kraniocerebralnou_traumou(hp)

    if kriterium == "marker Pacient nespĺňa medicínske kritériá polytraumy":
        return Marker(kod="mOSN", hodnota="nopol") in hp.markery
    return False


def priloha_6(hp: HospitalizacnyPripad) -> list[str]:
    """Assign medicinske sluzby according to priloha 6.

    Vyhláška:
    Ak bol hospitalizačný prípad poistenca zaradený podľa klasifikačného systému do skupiny podľa stĺpca "Skupina
    klasifikačného systému" pri doplňujúcom kritériu zodpovedajúcemu stĺpcu "doplňujúce kritérium", hospitalizácii sa
    určí medicínska služba podľa stĺpca "medicínska služba" (DRGD).

    Args:
        hp: Hospitalizacny pripad

    Returns:
        List of assigned medicinske sluzby

    """
    if not hp.diagnozy or hp.drg is None or hp.je_dieta is None:
        return []

    table_name = "p6_DRGD_deti" if hp.je_dieta else "p6_DRGD_dospeli"

    return [
        line["kod_ms"]
        for line in tables[table_name]
        if hp.drg.startswith(line["drg"]) and splna_kriterium_podla_6(line["doplnujuce_kriterium"], hp)
    ]


def poskytnuty_vedlajsi_vykon(vedlajsie_vykony: list[str], skupina_vykonov: str, table_name: str) -> bool:
    """Evaluate if the hp had at least one vedlajsi vykon from the given group of vykony.

    Args:
        vedlajsie_vykony: List of vedlajsie vykony
        skupina_vykonov: Identifier of the group of vykony
        table_name: Name of the table where the group of vykony is located

    Returns:
        True, if the hp had at least one vedlajsi vykon from the given group of vykony

    """
    vykony = [vykon["kod_vykonu"] for vykon in tables[table_name] if vykon["kod_ms"] == skupina_vykonov]

    return any(vykon in vykony for vykon in vedlajsie_vykony)


def apply_all_vykony_hlavne(
    hp: HospitalizacnyPripad,
    apply_priloha: Callable[[HospitalizacnyPripad], list[str]],
) -> list[str]:
    """Apply the given priloha function to all possible hlavne vykony of the hp.

    Args:
        hp: Hospitalizacny pripad
        apply_priloha: Function to apply the priloha

    Returns:
        List of assigned medicinske sluzby

    """
    sluzby = []

    for i in range(1, len(hp.vykony)):
        hlavny_vykon = hp.vykony[i]
        vedlajsie_vykony = [*hp.vykony[:i], *hp.vykony[i + 1 :]]
        new_hp = hp._replace(vykony=[hlavny_vykon, *vedlajsie_vykony])
        sluzby.extend(apply_priloha(new_hp))

    return sluzby


def prilohy_7_8(hp: HospitalizacnyPripad, *, all_vykony_hlavne: bool) -> list[str]:
    """Assign medicinske sluzby according to priloha 7 and 8.

    Vyhláška:
    Ak bol poistencovi poskytnutý hlavný zdravotný výkon podľa stĺpca "hlavný zdravotný výkon" a minimálne jeden výkon z
    uvedených výkonov (VV).

    Args:
        hp: Hospitalizacny pripad
        all_vykony_hlavne: True, if all possible hlavne vykony should be evaluated

    Returns:
        List of assigned medicinske sluzby

    """
    if len(hp.vykony) < 2 or hp.vykony[0] == "" or hp.je_dieta is None:
        return []

    nazov_tabulky = "p7_VV_deti_hv" if hp.je_dieta else "p8_VV_dospeli_hv"
    nazov_vedlajsej_tabulky = "p7_VV_deti_vv" if hp.je_dieta else "p8_VV_dospeli_vv"

    def apply_priloha(hp: HospitalizacnyPripad) -> list[str]:
        return [
            line["kod_ms"]
            for line in tables[nazov_tabulky]
            if line["kod_hlavneho_vykonu"] == hp.vykony[0]
            and poskytnuty_vedlajsi_vykon(hp.vykony[1:], line["kod_ms"], nazov_vedlajsej_tabulky)
        ]

    sluzby = apply_priloha(hp)

    if all_vykony_hlavne:
        sluzby.extend(apply_all_vykony_hlavne(hp, apply_priloha))

    return sluzby


def prilohy_7a_8a(hp: HospitalizacnyPripad) -> list[str]:
    """Assign medicinske sluzby according to priloha 7a and 8a.

    Vyhláška:
    Ak bol poistencovi vykázaný marker podľa stĺpca "Kód markera" s hodnotou markera podľa stĺpca "Hodnota markera" a
    minimálne jeden výkon z uvedených výkonov (MV).

    Args:
        hp: Hospitalizacny pripad

    Returns:
        List of assigned medicinske sluzby

    """
    if not hp.vykony or not hp.markery or hp.je_dieta is None:
        return []

    table_name = "p7a_MV_deti" if hp.je_dieta else "p8a_MV_dospeli"

    return [
        line["kod_ms"]
        for line in tables[table_name]
        if line["kod_vykonu"] in hp.vykony and line["marker"] in hp.markery
    ]


def splna_diagnoza_zo_skupiny_podla_9(hlavna_diagnoza: str, skupina_diagnoz: str) -> bool:
    """Evaluate if the hlavna diagnoza is in the given group of diagnozy.

    Args:
        hlavna_diagnoza: hlavna diagnoza
        skupina_diagnoz: Name of the group of diagnozy

    Returns:
        True, ak hlavná diagnóza je z uvedenej skupiny diagnóz, inak False

    """
    cielove_diagnozy = [
        line["kod_hlavnej_diagnozy"] for line in tables["p9_VD_diagnozy"] if line["skupina_diagnoz"] == skupina_diagnoz
    ]

    return any(hlavna_diagnoza == cielova_diagnoza for cielova_diagnoza in cielove_diagnozy)


def priloha_9(hp: HospitalizacnyPripad, *, all_vykony_hlavne: bool) -> list[str]:
    """Assign medicinske sluzby according to priloha 9.

    Vyhláška:
    Ak bol poistencovi poskytnutý hlavný zdravotný výkon podľa stĺpca "názov zdravotného výkonu" pri hlavnej diagnóze zo
    skupiny diagnóz podľa stĺpca "Skupina diagnóz", hospitalizácii sa určí medicínska služba podľa stĺpca
    "Názov medicínskej služby" (VD).

    Args:
        hp: Hospitalizacny pripad
        all_vykony_hlavne: True, if all possible hlavne vykony should be evaluated

    Returns:
        List of assigned medicinske sluzby

    """
    if not hp.vykony or hp.vykony[0] == "" or not hp.diagnozy or hp.je_dieta is None:
        return []

    table_name = "p9_VD_deti" if hp.je_dieta else "p9_VD_dospeli"

    def apply_priloha(hp: HospitalizacnyPripad) -> list[str]:
        return [
            line["kod_ms"]
            for line in tables[table_name]
            if line["kod_hlavneho_vykonu"] == hp.vykony[0]
            and splna_diagnoza_zo_skupiny_podla_9(hp.diagnozy[0], line["skupina_diagnoz"])
        ]

    sluzby = apply_priloha(hp)

    if all_vykony_hlavne:
        sluzby.extend(apply_all_vykony_hlavne(hp, apply_priloha))

    return sluzby


def priloha_9a(hp: HospitalizacnyPripad) -> list[str]:
    """Assign medicinske sluzby according to priloha 9a.

    Vyhláška:
    Ak bol poistencovi vykázaný marker podľa stĺpca "Kód markera" s hodnotou markera podľa stĺpca "Hodnota markera" pri
    hlavnej diagnóze zo skupiny diagnóz podľa stĺpca "Skupina diagnóz", hospitalizácii sa určí medicínska služba podľa
    stĺpca "Názov medicínskej služby" (MD).

    Args:
        hp: Hospitalizacny pripad

    Returns:
        List of assigned medicinske sluzby

    """
    if not hp.diagnozy or not hp.markery or hp.je_dieta is None or hp.je_dieta:
        return []

    return [
        line["kod_ms"]
        for line in tables["p9a_MD_dospeli"]
        if hp.diagnozy[0].startswith(line["kod_hlavnej_diagnozy"]) and line["marker"] in hp.markery
    ]


def priloha_10(hp: HospitalizacnyPripad) -> list[str]:
    """Assign medicinske sluzby according to priloha 10.

    Vyhláška:
    Ak bola poistencovi pri hospitalizácii vykázaná hlavná diagnóza podľa stĺpca "skupina diagnóz pre hlavnú diagnózu" a
    vedľajšia diagnóza podľa stĺpca "názov vedľajšej diagnózy", hospitalizácii sa určí medicínska služba podľa stĺpca
    "medicínska služba" (DD).

    Args:
        hp: Hospitalizacny pripad

    Returns:
        List of assigned medicinske sluzby

    """
    if len(hp.diagnozy) < 2 or hp.je_dieta is None:
        return []

    hlavne_diagnozy = [line["kod_hlavnej_diagnozy"] for line in tables["p10_DD_diagnozy"]]
    table_vedlajsie_diagnozy = tables["p10_DD_deti"] if hp.je_dieta else tables["p10_DD_dospeli"]

    return [
        vedlajsia_diagnoza["kod_ms"]
        for vedlajsia_diagnoza in table_vedlajsie_diagnozy
        if vedlajsia_diagnoza["kod_vedlajsej_diagnozy"] in hp.diagnozy[1:] and hp.diagnozy[0] in hlavne_diagnozy
    ]


def prilohy_12_13(hp: HospitalizacnyPripad, *, all_vykony_hlavne: bool) -> list[str]:
    """Assign medicinske sluzby according to priloha 12 and 13.

    Vyhláška:
    Ak bol poistencovi vo veku 18 rokov a menej poskytnutý hlavný zdravotný výkon podľa stĺpca 'zdravotný výkon',
    hospitalizácii sa určí medicínska služba podľa stĺpca 'medicínska služba' [V].

    Args:
        hp: Hospitalizacny pripad
        all_vykony_hlavne: True, if all possible hlavne vykony should be evaluated

    Returns:
        List of assigned medicinske sluzby

    """
    if not hp.vykony or hp.je_dieta is None:
        return []

    table_name = "p12_V_deti" if hp.je_dieta else "p13_V_dospeli"

    def apply_priloha(hp: HospitalizacnyPripad) -> list[str]:
        return [line["kod_ms"] for line in tables[table_name] if line["kod_vykonu"] == hp.vykony[0]]

    sluzby = apply_priloha(hp)

    if all_vykony_hlavne:
        sluzby.extend(apply_all_vykony_hlavne(hp, apply_priloha))

    return sluzby


def prilohy_14_15(hp: HospitalizacnyPripad) -> list[str]:
    """Assign medicinske sluzby according to priloha 14 and 15.

    Vyhláška:
    Ak bola poistencov vo veku 18 rokov a menej pri hospitalizácii vykázaná hlavná diagnóza podľa stĺpca
    'hlavná diagnóza', hospitalizácii sa určí medicínska služba podľa stĺpca 'medicínska služba' [D].

    Args:
        hp: Hospitalizacny pripad

    Returns:
        List of assigned medicinske sluzby

    """
    if not hp.diagnozy or hp.je_dieta is None:
        return []

    table_name = "p14_D_deti" if hp.je_dieta else "p15_D_dospeli"
    return [line["kod_ms"] for line in tables[table_name] if line["kod_diagnozy"] == hp.diagnozy[0]]


def priloha_16(hp: HospitalizacnyPripad) -> list[str]:
    """Assign medicinske sluzby according to priloha 16.

    Vyhláška:
    Medicínska služba "Identifikácia mŕtveho darcu orgánov" sa určí, ak je pri hospitalizačnom prípade vykázaná aspoň
    jedna diagnóza zo skupiny diagnóz "Kóma" a súčasne aspoň jedna diagnóza zo skupiny "Opuch mozgu" a súčasne aspoň
    jedna z diagnóz zo skupiny "Vybrané ochorenia mozgu" (S).

    Args:
        hp: Hospitalizacny pripad

    Returns:
        List of assigned medicinske sluzby

    """
    if not hp.diagnozy:
        return []

    kod_ms = "S17-22"
    table_names = ["p16_koma", "p16_opuch_mozgu", "p16_vybrane_ochorenia"]

    for table_name in table_names:
        if not any(line["kod_diagnozy"] in hp.diagnozy for line in tables[table_name]):
            return []
    return [kod_ms]


def priloha_17(hp: HospitalizacnyPripad) -> list[str]:
    """Assign medicinske sluzby according to priloha 17.

    Vyhláška:
    V hospitalizačných prípadoch, v ktorých bol vykázaný marker podľa stĺpca "Kód markera" s hodnotou markera podľa
    stĺpca "Hodnota markera", hospitalizácii sa určí medicínska služba podľa stĺpca "Medicínska služba".

    Args:
        hp: Hospitalizacny pripad

    Returns:
        List of assigned medicinske sluzby

    """
    if not hp.markery:
        return []

    return [line["kod_ms"] for line in tables["p17_M"] if line["marker"] in hp.markery]


def prirad_ms(hp: HospitalizacnyPripad, *, all_vykony_hlavne: bool) -> list[str]:
    """Evaluate hp against all prilohy.

    If the hp does not match any medicinska sluzba according to prilohy, code "S99-99" is assigned.

    Args:
        hp: Hospitalizacny pripad
        all_vykony_hlavne: True, if all possible hlavne vykony should be evaluated

    Returns:
        List of assigned medicinske sluzby, first medicinska sluzba in the list is hlavna.

    """
    sluzby = [
        *priloha_17(hp),
        *priloha_16(hp),
        *priloha_5(hp),
        *priloha_6(hp),
        *prilohy_7_8(hp, all_vykony_hlavne=all_vykony_hlavne),
        *prilohy_7a_8a(hp),
        *priloha_9(hp, all_vykony_hlavne=all_vykony_hlavne),
        *priloha_9a(hp),
        *priloha_10(hp),
        *prilohy_12_13(hp, all_vykony_hlavne=all_vykony_hlavne),
        *prilohy_14_15(hp),
    ]

    return sluzby or ["S99-99"]
