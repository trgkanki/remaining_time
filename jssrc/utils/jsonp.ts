// Copyright (C) 2020 Hyun Woo Park
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

interface JsonpQueueEntry {
  url: string;
  callbackName: string;
  resolve: (value: any) => void;
  reject: (reason: any) => void;
}

/**
 * Main JSONP runner
 */
function requestJSONPMain (entry: JsonpQueueEntry): void {
  const { url, callbackName, resolve, reject } = entry
  const windowAny = window as any
  const scriptEl = document.createElement('script')

  scriptEl.async = true
  windowAny[callbackName] = (data: any) => {
    scriptEl.remove()
    delete windowAny[callbackName]
    resolve(data)
  }

  scriptEl.src = url
  scriptEl.onerror = (err: any) => {
    scriptEl.remove()
    delete windowAny[callbackName]
    console.error(err)
    reject(err)
  }

  document.getElementsByTagName('head')[0].appendChild(scriptEl)
}

/**
 * Queuer. sequentially call requestJSONPMain
 *
 * Since one may reuse callback name between jsonp calls, (ex: calling static
 * .js within medias) it's quite risky to just allow jsonp to be called
 * asynchronously. This function queues JSONP calls and calls them sequentially.
 */

const queue = [] as JsonpQueueEntry[]
let isJsonPRunning = false

function runQueue (): void {
  if (isJsonPRunning) return
  const entry = queue.pop()
  if (!entry) return

  isJsonPRunning = true
  requestJSONPMain({
    url: entry.url,
    callbackName: entry.callbackName,
    resolve: (res: any) => {
      isJsonPRunning = false
      runQueue()
      entry.resolve(res)
    },
    reject: (res: any) => {
      isJsonPRunning = false
      runQueue()
      entry.reject(res)
    }
  })
}

/**
 * Main export
 */
export function requestJSONP (url: string, callbackName: string): Promise<any> {
  return new Promise((resolve, reject) => {
    queue.push({ url, callbackName, resolve, reject })
    runQueue()
  })
}
