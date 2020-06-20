import $ from 'jquery'
import './basestyle.scss'

export function updateProgressBar (b64svg: string, progressBarMessage: string) {
  let $barEl = $('#remainingTimeBar')
  if ($barEl.length === 0) {
    $barEl = $('<div></div>')
    $barEl.attr('id', 'remainingTimeBar')
    $('body').append($barEl)
  }
  $barEl.html(`${progressBarMessage} &nbsp; <a href=#resetRT onclick="pycmd('_rt_pgreset');return false;" title='Reset progress bar for this deck'>[⥻]</a>`)

  let styleEl = document.getElementById('remainingTimeStylesheet')
  if (!styleEl) {
    styleEl = document.createElement('style')
    styleEl.id = 'remainingTimeStylesheet'
    document.head.appendChild(styleEl)
  }
  styleEl.textContent = `
    #remainingTimeBar {
      background: url('data:image/svg+xml;base64,${b64svg}')
    }
  `
}
