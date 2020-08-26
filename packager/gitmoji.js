const emojis = [
  {
    emoji: '🎨',
    code: ':art:'
  },
  {
    emoji: '⚡️',
    code: ':zap:'
  },
  {
    emoji: '🔥',
    code: ':fire:'
  },
  {
    emoji: '🐛',
    code: ':bug:'
  },
  {
    emoji: '🚑',
    code: ':ambulance:'
  },
  {
    emoji: '✨',
    code: ':sparkles:'
  },
  {
    emoji: '📝',
    code: ':pencil:'
  },
  {
    emoji: '🚀',
    code: ':rocket:'
  },
  {
    emoji: '💄',
    code: ':lipstick:'
  },
  {
    emoji: '🎉',
    code: ':tada:'
  },
  {
    emoji: '✅',
    code: ':white_check_mark:'
  },
  {
    emoji: '🔒',
    code: ':lock:'
  },
  {
    emoji: '🍎',
    code: ':apple:'
  },
  {
    emoji: '🐧',
    code: ':penguin:'
  },
  {
    emoji: '🏁',
    code: ':checkered_flag:'
  },
  {
    emoji: '🤖',
    code: ':robot:'
  },
  {
    emoji: '🍏',
    code: ':green_apple:'
  },
  {
    emoji: '🔖',
    code: ':bookmark:'
  },
  {
    emoji: '🚨',
    code: ':rotating_light:'
  },
  {
    emoji: '🚧',
    code: ':construction:'
  },
  {
    emoji: '💚',
    code: ':green_heart:'
  },
  {
    emoji: '⬇️',
    code: ':arrow_down:'
  },
  {
    emoji: '⬆️',
    code: ':arrow_up:'
  },
  {
    emoji: '📌',
    code: ':pushpin:'
  },
  {
    emoji: '👷',
    code: ':construction_worker:'
  },
  {
    emoji: '📈',
    code: ':chart_with_upwards_trend:'
  },
  {
    emoji: '♻️',
    code: ':recycle:'
  },
  {
    emoji: '🐳',
    code: ':whale:'
  },
  {
    emoji: '➕',
    code: ':heavy_plus_sign:'
  },
  {
    emoji: '➖',
    code: ':heavy_minus_sign:'
  },
  {
    emoji: '🔧',
    code: ':wrench:'
  },
  {
    emoji: '🔨',
    code: ':hammer:'
  },
  {
    emoji: '🌐',
    code: ':globe_with_meridians:'
  },
  {
    emoji: '✏️',
    code: ':pencil2:'
  },
  {
    emoji: '💩',
    code: ':poop:'
  },
  {
    emoji: '⏪',
    code: ':rewind:'
  },
  {
    emoji: '🔀',
    code: ':twisted_rightwards_arrows:'
  },
  {
    emoji: '📦',
    code: ':package:'
  },
  {
    emoji: '👽',
    code: ':alien:'
  },
  {
    emoji: '🚚',
    code: ':truck:'
  },
  {
    emoji: '📄',
    code: ':page_facing_up:'
  },
  {
    emoji: '💥',
    code: ':boom:'
  },
  {
    emoji: '🍱',
    code: ':bento:'
  },
  {
    emoji: '👌',
    code: ':ok_hand:'
  },
  {
    emoji: '♿️',
    code: ':wheelchair:'
  },
  {
    emoji: '💡',
    code: ':bulb:'
  },
  {
    emoji: '🍻',
    code: ':beers:'
  },
  {
    emoji: '💬',
    code: ':speech_balloon:'
  },
  {
    emoji: '🗃',
    code: ':card_file_box:'
  },
  {
    emoji: '🔊',
    code: ':loud_sound:'
  },
  {
    emoji: '🔇',
    code: ':mute:'
  },
  {
    emoji: '👥',
    code: ':busts_in_silhouette:'
  },
  {
    emoji: '🚸',
    code: ':children_crossing:'
  },
  {
    emoji: '🏗',
    code: ':building_construction:'
  },
  {
    emoji: '📱',
    code: ':iphone:'
  },
  {
    emoji: '🤡',
    code: ':clown_face:'
  },
  {
    emoji: '🥚',
    code: ':egg:'
  },
  {
    emoji: '🙈',
    code: ':see_no_evil:'
  },
  {
    emoji: '📸',
    code: ':camera_flash:'
  },
  {
    emoji: '⚗',
    code: ':alembic:'
  },
  {
    emoji: '🔍',
    code: ':mag:'
  },
  {
    emoji: '☸️',
    code: ':wheel_of_dharma:'
  },
  {
    emoji: '🏷️',
    code: ':label:'
  },
  {
    emoji: '🌱',
    code: ':seedling:'
  },
  {
    emoji: '🚩',
    code: ':triangular_flag_on_post:'
  },
  {
    emoji: '💫',
    code: ':dizzy:'
  },
  {
    emoji: '🥅',
    code: ':goal_net:'
  },
  {
    emoji: '🗑',
    code: ':wastebasket:'
  }
]

function replaceAll (str, searchStr, replaceStr) {
  return str.split(searchStr).join(replaceStr)
}

exports.codeToEmoji = function (text) {
  for (const { emoji, code } of emojis) {
    text = replaceAll(text, code, emoji)
  }
  return text
}

exports.emojiToCode = function (text) {
  for (const { emoji, code } of emojis) {
    text = replaceAll(text, emoji, code)
  }
  return text
}
