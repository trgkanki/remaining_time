/* eslint-disable import/no-webpack-loader-syntax */
import { getAddonConfig } from '../utils/addonConfig'

const baseStyleCSS = require('!!raw-loader!sass-loader!../basestyle.scss').default as string
const rtbarTopCSS = require('!!raw-loader!../res/rtbar-top.css').default as string
const rtbarBottomCSS = require('!!raw-loader!../res/rtbar-bottom.css').default as string

export async function injectCSS (target: HTMLElement) {
  const verticalPositioningCSS = (await getAddonConfig('showAtBottom')) ? rtbarBottomCSS : rtbarTopCSS

  let styleEl = document.getElementById('rt-basestyle')
  if (!styleEl) {
    styleEl = document.createElement('style')
    styleEl.id = 'rt-basestyle'
    target.appendChild(styleEl)
  }
  styleEl.innerHTML = baseStyleCSS + verticalPositioningCSS
}
