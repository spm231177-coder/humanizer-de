#!/usr/bin/env python3
"""Zaehlt typische KI-Merkmale in deutschen Texten (Begleitskript zu humanizer-de).

Aufruf:
    python pruefe_ki_merkmale.py datei.txt [weitere.txt ...]
    python pruefe_ki_merkmale.py --vergleich vorher.txt nachher.txt
    echo "Text" | python pruefe_ki_merkmale.py -

Das Skript ersetzt das Lesen nicht. Null Treffer heisst nicht "menschlich",
ein Treffer in einem Zitat ist kein Fehler. Es misst nur, was sich zaehlen laesst.
"""
import re
import sys

# (Paragraf im Skill, Bezeichnung, Muster). Muster sind regulaere Ausdruecke, Gross/Klein egal.
MUSTER = [
    ("§1", "nicht nur ... sondern", r"\bnicht nur\b[^.!?]{0,120}\bsondern\b"),
    ("§1", "es geht nicht um ... es geht um", r"\bes geht nicht (?:um|darum)\b"),
    ("§1", "nicht X, sondern Y", r"\bnicht (?:einfach|bloß|bloss|nur)?\s*\w+[^.!?]{0,60},\s*sondern\b"),
    ("§2", "Pointensatz", r"(?:genau das macht den unterschied|und das ist erst der anfang|lesen sie das (?:ruhig )?noch einmal|die botschaft war klar|das zeigt, wie wichtig)"),
    ("§2", "Fragmentreihe", r"(?:(?:^|(?<=[.!?]))\s*(?:kein|keine|keinen|nie|ohne|mehr|weniger)\s+\w+(?:\s\w+)?[.!]){3,}"),
    ("§6", "Anapher-Dreier", r"\b(\w+)\s\w+,\s\1\s\w+,?\s(?:und\s)?\1\s\w+"),
    ("§3", "Tiefsinn-Floskel", r"\b(?:im kern|letztlich|worauf es wirklich ankommt|im grunde genommen|das herzstück|der schlüssel zu|die währung de[rs]|die dna (?:von|de[rs]))\b"),
    ("§4", "inszenierter Anlauf", r"\b(?:lassen sie uns|lass uns|tauchen wir|werfen wir einen blick|schauen wir uns|hier ist, was sie wissen müssen|ohne umschweife|hand aufs herz|mal ehrlich|seien wir ehrlich|die sache ist die)\b"),
    ("§4", "Doppelpunkt-Frage", r"(?:^|[.!]\s+)(?:das ergebnis|der haken|die antwort|der grund|das geheimnis|ehrlich)\?"),
    ("§5", "Streit mit niemandem", r"\b(?:versteh(?:en sie)? mich nicht falsch|um es klar zu sagen|man könnte versucht sein|naheliegend wäre|manche werden sagen)\b"),
    ("§9", "gestapelte Einschraenkung", r"\b(?:unter umständen möglicherweise|möglicherweise eventuell|könnte unter umständen|fairerweise muss man sagen)\b"),
    ("§10", "Uebersetzungsdeutsch", r"\b(?:macht? (?:es |das )?(?:keinen |wenig |viel )?sinn|am ende des tages|einen unterschied mach|nicht wirklich|in 20\d\d\b|game ?changer|nächsten level|mehrwert generier|mindset|learnings|deep dive|pain points?)"),
    ("§12", "KI-Modewort", r"\b(?:maßgeblich\w*|essenziell\w*|ganzheitlich\w*|nahtlos\w*|facettenreich\w*|zukunftsweisend\w*|wegweisend\w*|revolutionär\w*|bildungslandschaft|lernreise|tapisserie|zusammenspiel|herzstück|meilenstein\w*|mehrwert|unterstreich\w*|beleucht\w*|eintauch\w*|darüber hinaus|des weiteren|nicht zuletzt|gleichermaßen|in der heutigen (?:schnelllebigen |digitalen )?(?:welt|zeit)|im zeitalter (?:von|der|des))\b"),
    ("§12", "Modewort (schwach)", r"\b(?:entscheidend\w*|spannend\w*|beeindruckend\w*|bemerkenswert\w*|innovativ\w*|vielfältig\w*|umfassend\w*|zudem|ermöglich\w*)\b"),
    ("§13", "aufgeblaehte Bedeutung", r"\b(?:spielt eine (?:zentrale|entscheidende|wichtige|maßgebliche) rolle|ebnet den weg|legt den grundstein|setzt\s(?:\w+\s){0,3}maßstäbe|bleibendes vermächtnis|die zukunft sieht vielversprechend aus|spannende zeiten|ein schritt in die richtige richtung|trotz dieser herausforderungen)\b"),
    ("§15", "angehaengte Deutung", r",\s*(?:was|wodurch)\b[^.!?]{0,80}\b(?:widerspiegelt|unterstreicht|verdeutlicht|symbolisiert|zeigt)\b"),
    ("§16", "Werbesprache", r"\b(?:eingebettet in|im herzen (?:von|der|des)|malerisch\w*|atemberaubend\w*|unvergesslich\w*|erstklassig\w*|maßgeschneidert\w*|rundum sorglos|ihr starker partner|mit leidenschaft|auf höchstem niveau|qualität, die überzeugt)\b"),
    ("§17", "geliehene Autoritaet", r"\b(?:experten sind sich einig|studien zeigen|fachleute empfehlen|laut branchenberichten|zahlreiche zufriedene kunden|bekannt aus)\b"),
    ("§18", "umgangenes ist/hat", r"\b(?:fungiert als|dient als|verfügt über|zeichnet sich durch|wartet mit)\b"),
    ("§22", "Chatbot-Rest", r"(?:ich hoffe, (?:das|dies) hilft|sehr gute frage|gute frage!|da haben sie (?:völlig|absolut) recht|möchten sie, dass ich|soll ich (?:noch|ihnen)|lassen sie mich wissen|zusammenfassend lässt sich sagen|ich stehe ihnen gerne)"),
    ("§23", "Wissensgrenze", r"\b(?:stand meines (?:letzten )?trainings|nach verfügbaren informationen|nicht umfassend dokumentiert|nicht öffentlich bekannt|es wird angenommen, dass)\b"),
    ("§25", "ueber den Text", r"\b(?:im folgenden wird|die folgende tabelle (?:zeigt|vergleicht)|dieser abschnitt (?:ist|beschreibt|erläutert))\b"),
]

STRICH = re.compile(r"(?<=\s)[–—](?=\s)|(?<=\w)—(?=\w)|\s--\s|(?<=\w)\s-\s(?=\w)")
FETT = re.compile(r"\*\*[^*\n]+\*\*")
FETT_ETIKETT = re.compile(r"^\s*[-*]\s+\*\*[^*\n]+:\*\*|^\s*[-*]\s+\*\*[^*\n]+\*\*:", re.M)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿→]")
DE_PAAR = re.compile("„[^“”\\n]{0,300}[“”]")
ENGL_ANF = re.compile(r"[“”]|(?<![=\w])\"[^\"\n]{2,80}\"")
DREIER = re.compile(r"\b\w+(?:\s\w+)?,\s\w+(?:\s\w+)?\s(?:und|oder)\s\w+", re.I)
ANREDE_DU = re.compile(r"\b(?:du|dich|dir|dein\w*)\b")
ANREDE_SIE = re.compile(r"(?<![.!?]\s)(?<!^)\b(?:Sie|Ihnen|Ihr\w*)\b")
CODE = re.compile(r"```.*?```|`[^`\n]+`", re.S)


def pruefe(text):
    roh = CODE.sub(" ", text)
    klein = roh.lower()
    treffer = []
    belegt = []  # (start, ende, paragraf): gleiche Stelle nicht doppelt zaehlen
    for par, name, muster in MUSTER:
        for m in re.finditer(muster, klein, re.I | re.M):
            if any(par == bp and m.start() < be and m.end() > bs for bs, be, bp in belegt):
                continue
            belegt.append((m.start(), m.end(), par))
            treffer.append((par, name, roh[m.start():m.end()].strip()[:60]))
    for m in STRICH.finditer(roh):
        treffer.append(("§8", "Gedankenstrich", roh[max(0, m.start() - 15):m.end() + 15].replace("\n", " ")))
    for m in FETT_ETIKETT.finditer(roh):
        treffer.append(("§19", "Fett-Etikett", m.group(0).strip()[:60]))
    for m in EMOJI.finditer(roh):
        treffer.append(("§20", "Emoji/Pfeil", m.group(0)))
    ohne_de = DE_PAAR.sub(" ", roh)  # deutsche Paare „…“ zuerst heraus
    for m in ENGL_ANF.finditer(ohne_de):
        treffer.append(("§21", "englische Anfuehrung", m.group(0)[:40]))
    woerter = len(re.findall(r"\w+", roh))
    dreier = len(DREIER.findall(roh))
    fett = len(FETT.findall(roh))
    du = len(ANREDE_DU.findall(roh))
    sie = len(ANREDE_SIE.findall(roh))
    return treffer, {"woerter": woerter, "dreier_verdacht": dreier, "fett": fett, "du": du, "sie": sie}


def bericht(name, text, ausfuehrlich=True):
    treffer, z = pruefe(text)
    je1000 = 1000 * len(treffer) / max(z["woerter"], 1)
    print(f"== {name}: {z['woerter']} Woerter, {len(treffer)} Treffer ({je1000:.1f} je 1000 Woerter), "
          f"Dreier-Verdacht {z['dreier_verdacht']}, Fettdruck {z['fett']}")
    if z["du"] and z["sie"]:
        print(f"   §Anrede: du-Formen {z['du']} und Sie-Formen {z['sie']} gemischt (pruefen)")
    if ausfuehrlich:
        for par, kat, stelle in sorted(treffer, key=lambda t: int(re.sub(r'\D', '', t[0]) or 0)):
            print(f"   {par:<4} {kat:<26} {stelle}")
    return len(treffer), je1000


def lies(pfad):
    if pfad == "-":
        return sys.stdin.buffer.read().decode("utf-8", "replace")
    with open(pfad, encoding="utf-8") as f:
        return f.read()


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--vergleich" and len(argv) == 3:
        a, ja = bericht("vorher " + argv[1], lies(argv[1]), False)
        b, jb = bericht("nachher " + argv[2], lies(argv[2]))
        print(f"-> Treffer {a} -> {b}, je 1000 Woerter {ja:.1f} -> {jb:.1f}")
        return 0
    for p in argv:
        bericht(p, lies(p))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
