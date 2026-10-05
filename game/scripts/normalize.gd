class_name Normalize
## tools/normalize.py ile birebir aynı davranmalı.
const TR := {"ç":"c","ğ":"g","ı":"i","ö":"o","ş":"s","ü":"u","Ç":"c","Ğ":"g","İ":"i","Ö":"o","Ş":"s","Ü":"u"}
static var _re := RegEx.create_from_string("[^a-z0-9 ]+")
static var _ws := RegEx.create_from_string("\\s+")

static func norm(s: String) -> String:
	for k in TR: s = s.replace(k, TR[k])
	s = s.to_lower()
	s = _re.sub(s, " ", true)
	return _ws.sub(s, " ", true).strip_edges()
