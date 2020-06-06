import $ from 'jquery'
import './basestyle.scss'

export function updateProgressBar (b64svg: string, progressBarMessage: string) {
  let $barEl = $('#remainingTimeBar')
  if ($barEl.length === 0) {
    $barEl = $('<div></div>')
    $barEl.attr('id', 'remainingTimeBar')
    $('body').append($barEl)
  }
  $barEl.css('background', `url('data:image/svg+xml;base64,${b64svg}')`)
  $barEl.html(`${progressBarMessage} &nbsp; <a href=#resetRT onclick="pycmd('_rt_pgreset');return false;" title='Reset progress bar for this deck'>[⥻]</a>`)
}
