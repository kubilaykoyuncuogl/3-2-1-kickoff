// Klavye durumu: açık mı ve ekranın klavyenin üstünde kalan görünen alanı.
// Web'de (telefon tarayıcısı) klavye sayfayı küçültmez, üstüne biner; görünen alanı visualViewport verir, kök düzen kendini ona sığdırır.
// Telefon uygulamasında yer açmayı KeyboardAvoidingView yapar; burada yalnızca "açık" bilgisi tutulur (ekranlar sıkı düzene geçer).
import { Keyboard, Platform } from "react-native";
import { create } from "zustand";

type Kb = { open: boolean; height: number; top: number; fake: number };
export const useKeyboard = create<Kb>(() => ({ open: false, height: 0, top: 0, fake: 0 }));

const OPEN_GAP = 120;        // görünen alan en büyük halinden bu kadar kısaldıysa klavye açık sayılır (adres çubuğu oynaması sayılmaz)
export const FAKE_KB = 440;  // yalnızca geliştirme (?kb=1): ekran görüntüsünde klavye + tarayıcı çubuğu yerine geçen alan

let started = false;
export function watchKeyboard() {
  if (started) return;
  started = true;
  if (Platform.OS !== "web") {
    Keyboard.addListener(Platform.OS === "ios" ? "keyboardWillShow" : "keyboardDidShow", () => useKeyboard.setState({ open: true }));
    Keyboard.addListener(Platform.OS === "ios" ? "keyboardWillHide" : "keyboardDidHide", () => useKeyboard.setState({ open: false }));
    return;
  }
  if (typeof window === "undefined") return;
  if (__DEV__ && new URLSearchParams(location.search).get("kb") === "1") {
    const fit = () => useKeyboard.setState({ open: true, height: window.innerHeight - FAKE_KB, top: 0, fake: FAKE_KB });
    fit(); window.addEventListener("resize", fit); return;
  }
  const vv = window.visualViewport;
  if (!vv) return;
  let full = vv.height, width = vv.width;
  const fit = () => {
    if (vv.width !== width) { width = vv.width; full = vv.height; }      // ekran döndü: ölçüyü sıfırla
    full = Math.max(full, vv.height);
    const open = vv.height < full - OPEN_GAP;
    // klavye açılınca tarayıcı sayfayı yukarı kaydırabilir; kök düzen görünen alanın tam üstüne oturur
    useKeyboard.setState({ open, height: Math.round(vv.height), top: Math.round(vv.offsetTop) });
  };
  fit(); vv.addEventListener("resize", fit); vv.addEventListener("scroll", fit);
}
