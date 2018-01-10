# anki_plugins [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=4YEDX8978UQUG)

Some useful plugins for anki.

If you find these plugins useful, feel free to donate via paypal.

## Automatic switch from Basic to Cloze = basic_to_cloze

[AnkiWeb page](https://ankiweb.net/shared/info/2105427255)
This plugin prevents you from creating Cloze note in basic note types. If you try to do so, this plugin just automatically changes the note type to Cloze. So you can make both cloze type and basic type note via Basic note type.

![bas2cloz example](basic_to_cloze/bas2cloz.gif)

## Cloze (Hide all)

[AnkiWeb page](https://ankiweb.net/shared/info/1709973686)
This addon creates a new card type. On this card type, all clozes except what you're reviewing now are hidden with a yellow box.

![Cloze (Hide all) example](cloze_hide_all/cloze_hide_all.png)

## Word autocompleter

[AnkiWeb page](https://ankiweb.net/shared/info/1299759105)
This adds sublime text-like fuzzy word autocompletion to anki.

![wcomplete example](word_autocompleter/autocompleter.png)

## IME caret fixer = caretfix  (Experimental)

This is still an experimental addon. QtWebView which Anki uses to render card and editor has some weird bug, that when you try to type non-latin characters, carets (vertical bar indicating where you're typing) suddenly disappears. This hacky addon tries to fix it. 

