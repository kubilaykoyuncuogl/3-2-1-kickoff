"""Kurallar ve süreler. Değerler game.gd ile birebir; level design çalışmasına kadar değişmez (docs/expo-plan.md)."""
from enum import IntEnum


class State(IntEnum):
    LOBBY = 0
    PICK_TEAMS = 1
    COUNTDOWN = 2
    REVEAL = 3
    ROUND = 4
    ROUND_END = 5
    GAME_OVER = 6


PROTO = 3                      # istemci-sunucu sözleşme sürümü (JSON protokolü; Godot RPC'si 2'ydi). Mesaj biçimi değişince artır.
ROUND_MS = 15000
COUNTDOWN_MS = 3000
REVEAL_MS = 1800
PICK_MS = 45000                # takım seçimi; dolunca seçmeyen turu kaybeder
QUICK_AT_MS = 20000            # bu kadar geçince istemci hızlı seçenekleri gösterir
PENALTY_MS = 5000
ROUND_END_MS = 4000
NO_COMMON_MS = 3000            # ortak oyuncusu olmayan çift: uyarı süresi, sonra takım seçimine dönülür
WIN_SCORE = 3
MAX_INVALID_PAIRS = 3
ELO_K = 32
ELO_K_NEW = 40
BAND_START = 75
BAND_STEP = 50                 # her BAND_STEP_MS'de
BAND_STEP_MS = 20000
BAND_MAX = 500
CROSS_SCOPE_MS = 45000         # bu kadar bekleyenler kapsam/dönem fark etmeksizin eşleşir
SAME_OPP_MS = 20000            # az önceki rakiple yeniden eşleşmeden önce bekleme
RECONNECT_MS = 10000
SCOPE_ORDER = ["big5", "top", "all"]   # dar → geniş
LEAGUES = ("GB1", "ES1", "IT1", "L1", "FR1", "TR1", "NL1", "PO1")     # tek lig kapsamı: değer lig kodu (index_service.LEAGUES ile aynı)
BIG5 = {"GB1", "ES1", "IT1", "L1", "FR1"}
SCOPES = {"all", "top", "big5", *LEAGUES}


def widen_scope(a: str, b: str) -> str:
    """Eşleşmede kapsamlar farklıysa ikisini de kapsayan en dar kapsam. Tek lig < 5 büyük lig < üst ligler < tümü."""
    if a == b: return a
    def rank(s): return SCOPE_ORDER.index(s) if s in SCOPE_ORDER else -1
    def floor(s): return s if s in SCOPE_ORDER else ("big5" if s in BIG5 else "top")     # ligin içinde olduğu en dar genel kapsam
    fa, fb = floor(a), floor(b)
    return SCOPE_ORDER[max(rank(fa), rank(fb))]
SINGLE_LIVES = {"ladder": 3, "blitz": 1, "career": 3, "chain": 3, "versus": 1}
CAREER_REVEAL_MS = 8000        # kariyer yolu: bu aralıkla bir kulüp daha açılır
CAREER_LAST_MS = 15000         # hepsi açıldıktan sonra son tahmin süresi
CHAIN_STEP_MS = 20000
IN_MATCH = {State.PICK_TEAMS, State.COUNTDOWN, State.REVEAL, State.ROUND, State.ROUND_END}


def scope_ok(s) -> str:
    return s if s in SCOPES else "all"


def era_ok(e) -> int:
    """On yıl bit maskesi (1=80'ler … 16=20'ler); 0 ya da hepsi = tümü."""
    try: e = int(e or 0) & 31
    except (TypeError, ValueError): e = 0
    return 0 if e == 31 else e
