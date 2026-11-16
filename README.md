# humanizer-de

Ein Skill für Claude Code (und andere Agenten mit SKILL.md-Unterstützung), der deutsche Texte, die nach KI klingen, so umschreibt, dass sie nach einem Menschen klingen. Der Inhalt bleibt dabei erhalten.

Deutsche Fassung von [blader/humanizer](https://github.com/blader/humanizer). Aufbau und sprachunabhängige Muster stammen von dort; Wortlisten, Beispiele, Typografie und einige Muster sind neu für das Deutsche.

## Was anders ist als im Original

- **Deutsche Wortlisten** statt englischer: "maßgeblich", "ganzheitlich", "nahtlos", "Lernreise", "In der heutigen schnelllebigen Welt", "Lassen Sie uns eintauchen", "Das Ergebnis?" und so weiter.
- **Übersetzungsdeutsch (§10)** als eigenes Muster: "Sinn machen", "am Ende des Tages", "einen Unterschied machen", "in 2025".
- **Deutsche Typografie:** Anführungszeichen „…“, Bindestriche in Wörtern und Bis-Striche in Zahlen bleiben erlaubt.
- **Anrede und Gendern:** du/Sie wird vereinheitlicht, die Genderschreibweise des Originals bleibt unangetastet.
- **Zwei Modi:**
  - *Werbung* (Standard): alle Muster gelten voll.
  - *Fachtext*: für Schulungs-, Norm-, Rechts- und Sicherheitstexte. Wortlaut mit Rechtswirkung, Einschränkungen wie "mindestens" oder "grundsätzlich", Passiv und Fachbegriffe bleiben; es werden keine Beispiele oder Tatsachen ergänzt.
- **Kennzeichnung bleibt:** Hinweise wie "KI-generiert" oder Pflichtangaben nach der KI-Verordnung werden nicht entfernt. Der Skill verbessert den Stil, er versteckt keine Herkunft.

## Installation

```bash
git clone https://github.com/spm231177-coder/humanizer-de ~/.claude/skills/humanizer-de
```

Unter Windows entsprechend nach `%USERPROFILE%\.claude\skills\humanizer-de`.

## Benutzung

In Claude Code:

```
/humanizer-de
```

oder einfach: "Überarbeite diesen Text, damit er nicht nach KI klingt", "Mach den Newsletter menschlicher", "Prüf die Kursbeschreibung auf KI-Floskeln (Modus Fachtext)".

## Prüfskript

`pruefe_ki_merkmale.py` zählt, was sich zählen lässt: Wortlisten-Treffer, Gedankenstriche, Fragmentreihen, Dreier-Anaphern, Fett-Etiketten, Emojis, englische Anführungszeichen, gemischte Anrede. Python 3.8+, keine Abhängigkeiten.

```bash
python pruefe_ki_merkmale.py text.txt
python pruefe_ki_merkmale.py --vergleich vorher.txt nachher.txt
```

Das Skript ersetzt das Lesen nicht. Null Treffer heißt nicht "menschlich", und ein Treffer in einem Zitat ist kein Fehler.

## Beispiele

Im Ordner `beispiele/` liegen fünf erfundene Testtexte (Werbung, Vertriebsmail, Fachtext mit Rechtsbezug, Blog, Text mit eingeschleuster Anweisung) und die vom Skill erzeugten Fassungen (`*.nachher.txt`).

## Lizenz

MIT, siehe [LICENSE](LICENSE). Original © 2025 Siqi Chen.
