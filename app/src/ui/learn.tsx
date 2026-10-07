// Moda girerken çıkan aşama aşama "nasıl oynanır" (eski Nasıl oynanır sayfasının yerine). Her mod için ayrı.
// "Bir daha gösterme" yalnızca o modu kapatır (settings.learn_off); Ayarlar'daki anahtar hepsini topluca açar ya da kapatır.
import React, { useState } from "react";
import { Pressable, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { t } from "../i18n";
import { useSettings } from "../store";
import { useTheme } from "../theme";
import { Btn, Eyebrow, Panel, Txt } from "./index";

// Adım: [metin anahtarı, üst etiket, üst yazı, alt etiket, alt yazı]. Etiket ve yazılar dil anahtarıysa çevrilir, değilse (kulüp / oyuncu adı) aynen yazılır.
type Step = [string, string, string, string, string];
const STEPS: Record<string, Step[]> = {
  online: [
    ["howto.1.body", "you", "Galatasaray", "learn.ex.opponent", "Inter Milan"],
    ["howto.2.body", "you", "3 · 2 · 1", "learn.ex.opponent", "learn.ex.ready"],
    ["howto.3.body", "learn.ex.typed", "Snei", "learn.ex.answer", "Wesley Sneijder  +1"],
    ["howto.4.body", "learn.ex.guess", "howto.4.a", "learn.ex.result", "howto.4.b"],
    ["howto.5.body", "you", "3 : 1", "learn.ex.result", "won"],
  ],
  ladder: [
    ["learn.ladder.1", "learn.ex.clubs", "Real Madrid × Juventus", "learn.ex.answer", "Zinédine Zidane"],
    ["learn.ladder.2", "learn.ex.guess", "Lukas Podolski", "learn.ex.result", "learn.ex.life_lost"],
    ["learn.ladder.3", "learn.ex.step_first", "learn.ex.secs20", "learn.ex.step_late", "learn.ex.secs14"],
  ],
  blitz: [
    ["learn.blitz.1", "learn.ex.clubs", "Chelsea × AC Milan", "learn.ex.one_of_five", "Andriy Shevchenko"],
    ["learn.blitz.2", "learn.ex.guess", "Didier Drogba", "learn.ex.result", "learn.ex.run_over"],
    ["learn.blitz.3", "learn.ex.combo", "×1.0  →  ×2.0", "learn.ex.time", "learn.ex.secs8to3"],
  ],
  career: [
    ["learn.career.1", "learn.ex.path", "Sporting  →  ?", "learn.ex.reveal", "learn.ex.every8"],
    ["learn.career.2", "learn.ex.path", "Sporting → Man United → Real Madrid", "learn.ex.answer", "Cristiano Ronaldo"],
    ["learn.career.3", "learn.ex.guess", "Luís Figo", "learn.ex.result", "learn.ex.tried_out"],
  ],
  chain: [
    ["learn.chain.1", "learn.ex.player", "Wesley Sneijder", "learn.ex.first_club", "Ajax"],
    ["learn.chain.2", "learn.ex.hints", "learn.ex.hint_line", "learn.ex.next_club", "Real Madrid"],
    ["learn.chain.3", "learn.ex.guess", "Chelsea", "learn.ex.result", "learn.ex.shown_next"],
  ],
  weekly: [
    ["learn.weekly.1", "learn.ex.w_q", "Hami Mandıralı", "learn.ex.or", "Feyyaz Uçar"],
    ["learn.weekly.2", "learn.ex.w_side", "learn.ex.w_pick", "learn.ex.result", "learn.ex.w_added"],
    ["learn.weekly.3", "learn.ex.guess", "Feyyaz Uçar", "learn.ex.result", "learn.ex.run_over"],
  ],
  weekly_career: [
    ["learn.wcareer.1", "learn.ex.w_side", "Liverpool", "learn.ex.first_club", "Sporting CP"],
    ["learn.wcareer.2", "learn.ex.guess", "Luis Suárez", "learn.ex.result", "learn.ex.w_early"],
    ["learn.wcareer.3", "learn.ex.w_side", "Liverpool", "learn.ex.result", "learn.ex.w_added"],
  ],
  versus: [
    ["learn.versus.1", "learn.ex.more_goals", "Hakan Şükür", "learn.ex.or", "Burak Yılmaz"],
    ["learn.versus.2", "learn.ex.result", "learn.ex.right_next", "learn.ex.bonus", "learn.ex.fast_bonus"],
    ["learn.versus.3", "learn.ex.guess", "Burak Yılmaz", "learn.ex.result", "learn.ex.run_over"],
  ],
};

export function LearnSteps({ id, title }: { id: string; title: string }) {
  const { c, s, col } = useTheme();
  const insets = useSafeAreaInsets();
  const learn = useSettings((x) => x.learn);
  const off = useSettings((x) => x.learn_off);
  const [open, setOpen] = useState(true);
  const [i, setI] = useState(0);
  const steps = STEPS[id];
  if (!steps || !learn || !open || off.includes(id)) return null;
  const st = steps[i]; const last = i === steps.length - 1;
  const never = () => { const cur = useSettings.getState(); cur.set({ learn_off: [...cur.learn_off.filter((x) => x !== id), id] }); setOpen(false); };
  return (
    <View style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, backgroundColor: c.bg }}>
      <View style={{ flex: 1, width: col, alignSelf: "center", gap: s(12), paddingTop: Math.max(insets.top, s(16)), paddingBottom: Math.max(insets.bottom, s(16)) }}>
        <View style={{ flexDirection: "row", alignItems: "center", minHeight: s(40) }}>
          <Eyebrow style={{ flex: 1 }}>{t("learn.header") + "  ·  " + title}</Eyebrow>
          <Pressable onPress={() => setOpen(false)} hitSlop={10}><Txt size={14} w={700} color="violet_ink">{t("learn.skip")}</Txt></Pressable>
        </View>
        <View style={{ backgroundColor: c.fg, borderRadius: s(12), padding: s(14) }}>
          <Txt size={15} w={600} color="bg" style={{ lineHeight: s(21) }}>{t(st[0])}</Txt>
        </View>
        <Txt size={13} w={700} color="muted">{`${i + 1} / ${steps.length}`}</Txt>
        <Panel kind="violet" style={{ flex: 1 }}>
          <Eyebrow color="violet_ink">{t(st[1])}</Eyebrow>
          <Txt size={22} w={800} color="violet_ink">{t(st[2])}</Txt>
        </Panel>
        <Panel kind="amber" style={{ flex: 1 }}>
          <Eyebrow color="amber_ink">{t(st[3])}</Eyebrow>
          <Txt size={22} w={800} color="amber_ink">{t(st[4])}</Txt>
        </Panel>
        <View style={{ flexDirection: "row", gap: s(8) }}>
          <Btn text={t("back")} kind="line" disabled={i === 0} onPress={() => setI(i - 1)} style={{ flex: 1 }} />
          <Btn text={last ? t("learn.ok") : t("next")} onPress={() => (last ? setOpen(false) : setI(i + 1))} style={{ flex: 1 }} />
        </View>
        <Btn text={t("learn.never")} kind="ghost" onPress={never} />
      </View>
    </View>
  );
}
