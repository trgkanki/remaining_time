# Always add config.json!!!!

from .utils.configrw import getConfig, setConfig

a = int(getConfig("t1", 0))
a += 1
setConfig("t1", a)
