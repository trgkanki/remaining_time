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

            var checkPerLoop = 10000;
            var i = 0;
            function checker() {
                var j = 0;
                for(j = 0 ; j < checkPerLoop ; j++) {
                    if(i == wordList.length) {
                        indirectSorter.sort(function(a, b) {
                            return acceptanceTable[b] - acceptanceTable[a];
                        });

                        var ret = [];
                        for(i = 0 ; i < Math.min(N, 5) ; i++) {
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
            checker();
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

        function getWordStart(text, from) {
            var endedWithAlphabet = false;
            for (var j = from - 1 ; j >= 0 ; j--) {
                var ch = text.charAt(j);
                if(
                    'a' <= ch && ch <= 'z' ||
                    'A' <= ch && ch <= 'Z') {
                    endedWithAlphabet = true;
                    continue;
                }
                else if('0' <= ch && ch <= '9') {
                    endedWithAlphabet = false;
                    continue;
                }
                else break;
            }
            if(!endedWithAlphabet) return null;
            else return j + 1;
        }

        // https://github.com/gr2m/contenteditable-autocomplete
        function getCurrentQuery() {
            var container = getCaretParentElement();
            var $container = $(container);
            var cursorAt = getCaretCharacterOffsetWithin(container);
            var text = $container.text();
            var wordStart = getWordStart(text, cursorAt);
            if(wordStart == null) return null;
            return text.substring(wordStart, cursorAt);
        }

        // https://github.com/gr2m/contenteditable-autocomplete
        function replaceCurrentQuery(newText) {
            var container = getCaretParentElement();
            var $container = $(container);
            var cursorAt = getCaretCharacterOffsetWithin(container);
            var text = $container.text();
            var wordStart = getWordStart(text, cursorAt);
            if(wordStart == null) return;
            var repText = 
                text.substring(0, wordStart) +
                newText +
                text.substring(cursorAt);
            container.textContent = repText;
            setCursorAt($container, wordStart + repText.length);
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

        var isFindingAutocomplete = false;
        var nextQueue = false;
        function queueAutocomplete(query, callback) {
            if(isFindingAutocomplete) {
                nextQueue = query;
                return;
            }

            function resolveNextQueue() {
                if(nextQueue) {
                    nextQueue = null;
                    queueAutocomplete(nextQueue);
                }
            }

            var $el = getAutoCompleterSpan();
            var query = getCurrentQuery();
            if(!(query && query.length >= 2)) {
                resolveNextQueue();
                return;
            }

            isFindingAutocomplete = true;
            getAutocompleteList(query, wordSet, function(autocomplete) {
                if(autocomplete.length == 0) {
                    $el.data('autocomplete', null);
                    $el.html("-------");
                }

                else {
                    $el.css('display', 'inline-block');
                    var html = "<b>" + autocomplete[0] + "</b>";
                    for(var i = 1 ; i < autocomplete.length ; i++) {
                        html += " / " + autocomplete[i];
                    }
                    $el.html(html);
                    $el.data('autocomplete', autocomplete);
                    $el.insertAfter(currentField);
                }
                isFindingAutocomplete = false;
                resolveNextQueue();
            })
        }

        var ctrlPressed = false;
        $('body').on('input keydown', '[contenteditable]', function(event) {
            var $this = $(this);
            var $el = getAutoCompleterSpan();
            if(event.keyCode == 17) ctrlPressed = true;

            if(ctrlPressed && 49 <= event.keyCode && event.keyCode <= 57) {
                if($el.data('autocomplete')) {
                    var candidates = $el.data('autocomplete');
                    var candidateIndex = event.keyCode - 49;
                    if(candidates.length > candidateIndex) {
                        replaceCurrentQuery($el.data('autocomplete')[candidateIndex]);
                        $el.data('autocomplete', null);
                        $el.html("-------");
                    }
                }
                event.preventDefault();
                return;
            }

            if(event.keyCode == 9 && $el.data('autocomplete')) {
                replaceCurrentQuery($el.data('autocomplete')[0]);
                event.preventDefault();
                $el.data('autocomplete', null);
                $el.html("-------");
                return;
            }

            var query = getCurrentQuery();
            queueAutocomplete(query);
        });

        $('body').on('blur', '[contenteditable]', function(event) {
            var $el = getAutoCompleterSpan();
            $el.data('autocomplete', null);
            $el.html("-------");
        });

        $('body').on('keyup', '[contenteditable]', function(event) {
            if(event.keyCode == 17) ctrlPressed = false;
        });
    })();
}