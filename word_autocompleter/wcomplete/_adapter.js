// Initialize only once
if (!window._wcomplete) {
    window._wcomplete = true;

    (function() {
        function ranker(target, matched_text) {
            var max_prioritized_char_dist = 3;
            var max_prioritized_wordstart_dist = 4;
            var slen = matched_text.length;
            var index = 0,
                rank = 0;

            target = target.toLowerCase();
            matched_text = matched_text.toLowerCase();

            for (var i = 0; i < target.length; i++) {
                var ch = target[i];
                var previndex = index;

                // Find matching index
                while (matched_text[index] != ch) {
                    index++;
                    if (index >= slen) return -1; // Match failed
                }

                // Value smaller distance between match characters
                var chdist = index - previndex;
                var chd_mul = Math.max(1, max_prioritized_char_dist - chdist);
                var wsd_mul = Math.max(1, max_prioritized_wordstart_dist - index);
                rank += 100 * chd_mul * wsd_mul;
                index++;
            }

            if (slen < 100) rank += 100 - slen;

            return rank;
        }

        function getAutocompleteList(target, wordList, callback) {
            var N = wordList.length;
            var acceptanceTable = new Array(N);
            var indirectSorter = new Array(N);

            var checkPerLoop = 1000;
            var i = 0;

            function checker() {
                var j = 0;
                for (j = 0; j < checkPerLoop; j++) {
                    if (i == wordList.length) {
                        indirectSorter.sort(function(a, b) {
                            return acceptanceTable[b] - acceptanceTable[a];
                        });

                        var ret = [];
                        for (i = 0; i < Math.min(N, 5); i++) {
                            var idx = indirectSorter[i];
                            if (acceptanceTable[idx] < 0) break;
                            ret.push(wordList[idx]);
                        }
                        return callback(ret);
                    }
                    indirectSorter[i] = i;
                    acceptanceTable[i] = ranker(target, wordList[i]);
                    i++;
                }
                setTimeout(checker, 1);
            }
            setTimeout(checker, 1);
        }

        function getCaretParentElement() {
            var range = window.getSelection().getRangeAt(0);
            return range.startContainer;
        }

        // http://stackoverflow.com/questions/4811822/get-a-ranges-start-and-end-offsets-relative-to-its-parent-container/4812022#4812022
        // also: http://stackoverflow.com/questions/22935320/uncaught-indexsizeerror-failed-to-execute-getrangeat-on-selection-0-is-not
        function getCaretCharacterOffsetWithin(element) {
            var caretOffset = 0;
            var doc = element.ownerDocument || element.document;
            var win = doc.defaultView || doc.parentWindow;
            var range, preCaretRange;
            if (typeof win.getSelection !== 'undefined' && win.getSelection().rangeCount > 0) {
                range = win.getSelection().getRangeAt(0);
                preCaretRange = range.cloneRange();
                preCaretRange.selectNodeContents(element);
                preCaretRange.setEnd(range.endContainer, range.endOffset);
                caretOffset = preCaretRange.toString().length;
            }
            return caretOffset;
        }

        function getWordStart(text, from, allowTrailingSpaces) {
            var endedWithAlphabet = false;
            var j = from - 1;
            var spaces = 0;
            if (allowTrailingSpaces) {
                for (; j >= 0; j--) {
                    if (!text.charAt(j) == ' ') break;
                }
                spaces = (from - 1) - j;
            }
            for (; j >= 0; j--) {
                var ch = text.charAt(j);
                if (
                    'a' <= ch && ch <= 'z' ||
                    'A' <= ch && ch <= 'Z') {
                    endedWithAlphabet = true;
                    continue;
                } else if ('0' <= ch && ch <= '9') {
                    endedWithAlphabet = false;
                    continue;
                } else break;
            }
            if (!endedWithAlphabet) return null;
            else if (allowTrailingSpaces) return [j + 1, spaces];
            else return j + 1;
        }

        // https://github.com/gr2m/contenteditable-autocomplete
        function getCurrentQuery() {
            var container = getCaretParentElement();
            var $container = $(container);
            var cursorAt = getCaretCharacterOffsetWithin(container);
            var text = $container.text();
            var wordStart = getWordStart(text, cursorAt);
            if (wordStart == null) return null;
            return text.substring(wordStart, cursorAt);
        }

        // https://github.com/gr2m/contenteditable-autocomplete
        function replaceCurrentQuery(newText) {
            var container = getCaretParentElement();
            var $container = $(container);
            var cursorAt = getCaretCharacterOffsetWithin(container);
            var text = container.textContent;
            var ws = getWordStart(text, cursorAt, true);
            if (ws == null) return;
            var wordStart = ws[0],
                spaces = ws[1];
            for (var i = 0; i < spaces; i++) newText += ' ';

            // First of oldtext is capital → Capitalize
            var oldText = text.substring(wordStart, cursorAt);
            if (oldText.charAt(0) == oldText.charAt(0).toUpperCase()) { // A-Z
                newText = newText.substring(0, 1).toUpperCase() + newText.substring(1);
            }
            var repText =
                text.substring(0, wordStart) +
                newText +
                text.substring(cursorAt);
            container.textContent = repText;
            setCursorAt($container, wordStart + newText.length);
        }

        // https://github.com/gr2m/contenteditable-autocomplete
        function setCursorAt($this, position) {
            var range = document.createRange()
            var sel = window.getSelection()
            var textNode = $this[0].childNodes.length ? $this[0].childNodes[0] : $this[0]
            position = Math.min(textNode.length, position)
            range.setStart(textNode, position)
            range.collapse(true)
            sel.removeAllRanges()
            sel.addRange(range)
        }

        function getAutoCompleterSpan() {
            var $el = $('.wautocompleter');
            if ($el.length == 0) {
                $el = $('<span></span>')
                    .css({
                        margin: '.3em',
                        padding: '.3em',
                        'background-color': '#ddd',
                        border: '1px solid black'
                    })
                    .addClass('wautocompleter')
                    .appendTo('body');
            }
            return $el;
        }

        function clearAutocompleteSpan() {
            var $el = getAutoCompleterSpan();
            $el.data('autocomplete', null);
            $el.html("-------");
        }

        var isFindingAutocomplete = false;
        var anotherAutocompleteQueued = false;
        var issueAutocompleteQueued = null;

        function queueAutocompleteIssue(index) {
            if (!isFindingAutocomplete) issueAutocomplete(index);
            else issueAutocompleteQueued = index;
        }

        function issueAutocomplete(index) {
            var $el = getAutoCompleterSpan();
            var candidates = $el.data('autocomplete');
            if (candidates == null) return; // No autocomplete available.
            var candidateIndex = index;
            if (candidates.length > candidateIndex) {
                replaceCurrentQuery($el.data('autocomplete')[candidateIndex]);
                clearAutocompleteSpan();
            }
        }

        function queueAutocomplete(query, callback) {
            if (isFindingAutocomplete) {
                anotherAutocompleteQueued = query;
                return;
            }

            function popTaskQueue() {
                if (issueAutocompleteQueued !== null) {
                    // Wait for next autocomplete issue.
                    if (issueAutocompleteQueued < 0) { // Already waited once.
                        anotherAutocompleteQueued = null;
                        issueAutocompleteQueued += 1000; // Reset to positive
                    }
                    if (anotherAutocompleteQueued) {
                        // Make negative → Wait for one more autocomplete query.
                        issueAutocompleteQueued -= 1000;
                    } else {
                        issueAutocomplete(issueAutocompleteQueued);
                        issueAutocompleteQueued = null;
                    }
                }
                if (anotherAutocompleteQueued) {
                    anotherAutocompleteQueued = null;
                    queueAutocomplete(anotherAutocompleteQueued);
                }
            }

            var $el = getAutoCompleterSpan();
            var query = getCurrentQuery();
            if (!(query && query.length >= 2)) {
                clearAutocompleteSpan();
                popTaskQueue();
                return;
            }

            isFindingAutocomplete = true;
            getAutocompleteList(query, wordSet, function(autocomplete) {
                if (autocomplete.length == 0) {
                    clearAutocompleteSpan();
                } else {
                    $el.css('display', 'inline-block');
                    var html = "<b title='Press Tab'>" + autocomplete[0] + "</b>";
                    for (var i = 1; i < autocomplete.length; i++) {
                        html += " / <span title='Press Ctrl+" + i + "'>" + autocomplete[i] + "</span>";
                    }
                    $el.html(html);
                    $el.data('autocomplete', autocomplete);
                    $el.insertAfter(currentField);
                }
                isFindingAutocomplete = false;
                popTaskQueue();
            })
        }

        var CTRL = 17;
        var DIGIT_0 = 49,
            DIGIT_9 = 57;
        var ESC = 27;
        var TAB = 9;

        var ctrlPressed = false;
        $('body').on('keydown', '[contenteditable]', function(event) {
            var $this = $(this);
            var $el = getAutoCompleterSpan();

            if (event.keyCode == CTRL) ctrlPressed = true;

            // Ctrl 1-9
            if (
                ctrlPressed &&
                (DIGIT_0 <= event.keyCode && event.keyCode <= DIGIT_9) &&
                $el.data('autocomplete')
            ) {
                queueAutocompleteIssue(event.keyCode - DIGIT_9);
                event.preventDefault();
                return;
            }

            // ESC -> clear autocomplete
            if (event.keyCode == ESC && $el.data('autocomplete')) {
                clearAutocompleteSpan();
                event.preventDefault();
                return;
            }

            // Tab
            if (event.keyCode == TAB && $el.data('autocomplete')) {
                queueAutocompleteIssue(0);
                event.preventDefault();
                return;
            }
        });

        $('body').on('input', '[contenteditable]', function(event) {
            var query = getCurrentQuery();
            queueAutocomplete(query);
        });

        $('body').on('blur', '[contenteditable]', function(event) {
            clearAutocompleteSpan();
        });

        $('body').on('keyup', '[contenteditable]', function(event) {
            if (event.keyCode == 17) ctrlPressed = false;
        });
    })();
}