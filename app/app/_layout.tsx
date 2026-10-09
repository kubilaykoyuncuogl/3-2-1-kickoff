// Kök düzen: font, ayarlar, bağlantı, tema; sayfa yığını (sağdan kayarak gelir, "hareketi azalt" açıksa anında).
import { Sora_400Regular, Sora_500Medium, Sora_600SemiBold, Sora_700Bold, Sora_800ExtraBold, useFonts } from "@expo-google-fonts/sora";
import { ErrorBoundary as RouterErrorBoundary, type ErrorBoundaryProps, Stack, useSegments } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import React, { useEffect } from "react";
import { Platform, View } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { useKeyboard, watchKeyboard } from "@/keyboard";
import { connect } from "@/net/socket";
import { useSettings } from "@/store";
import { useTheme } from "@/theme";
import { initializeClarity, reportClientError, Sentry, trackScreen } from "@/telemetry";
import { Txt } from "@/ui";
import { UpdateCard } from "@/ui/update";

SplashScreen.preventAutoHideAsync().catch(() => {});

export function ErrorBoundary(props: ErrorBoundaryProps) {
  useEffect(() => { reportClientError(props.error, "router.render"); }, [props.error]);
  return <RouterErrorBoundary {...props} />;
}

function RootLayout() {
  const segments = useSegments();
  const screen = segments.length ? segments.join("/") : "home";
  const [fontsLoaded] = useFonts({ Sora_400Regular, Sora_500Medium, Sora_600SemiBold, Sora_700Bold, Sora_800ExtraBold });
  const loaded = useSettings((s) => s.loaded);
  const reduce = useSettings((s) => s.reduce_motion);
  const { c, dark } = useTheme();

  const view = useKeyboard();
  const web = Platform.OS === "web";

  useEffect(() => { useSettings.getState().load(); watchKeyboard(); }, []);
  useEffect(() => { if (web && typeof document !== "undefined") document.body.style.backgroundColor = c.bg; }, [c.bg]);
  useEffect(() => { if (loaded) connect(); }, [loaded]);
  useEffect(() => { if (fontsLoaded && loaded) SplashScreen.hideAsync().catch(() => {}); }, [fontsLoaded, loaded]);
  useEffect(() => { if (fontsLoaded && loaded) initializeClarity(); }, [fontsLoaded, loaded]);
  useEffect(() => { trackScreen(screen); }, [screen]);

  if (!fontsLoaded || !loaded) return <View style={{ flex: 1, backgroundColor: c.bg }} />;
  return (
    <SafeAreaProvider>
      <StatusBar style={dark ? "light" : "dark"} />
      {/* web: klavye açıkken kök, ekranın görünen kısmına (klavyenin üstüne) sığar; yoksa içerik klavyenin altında kalır */}
      <View style={[{ flex: 1, backgroundColor: c.bg }, web && view.open ? ({ position: "fixed", flex: 0, top: view.top, left: 0, right: 0, height: view.height } as any) : null]}>
        <Stack screenOptions={{ headerShown: false, animation: reduce ? "none" : "slide_from_right", contentStyle: { backgroundColor: c.bg } }} />
        <UpdateCard />
      </View>
      {__DEV__ && view.fake ? <FakeKeyboard h={view.fake} /> : null}
    </SafeAreaProvider>
  );
}

// Yalnızca geliştirme (?kb=1): ekran görüntülerinde klavyenin kapladığı alanı gösterir
function FakeKeyboard({ h }: { h: number }) {
  const { dark } = useTheme();
  const bg = dark ? "#2B2B2E" : "#D3D5DB", key = dark ? "#6A6A6E" : "#FFFFFF", ink = dark ? "#FFFFFF" : "#1B1A21";
  const rows = ["qwertyuıopğü", "asdfghjklşi", "zxcvbnmöç"];
  return (
    <View style={{ position: "fixed", left: 0, right: 0, bottom: 0, height: h, backgroundColor: bg, paddingTop: 70, paddingHorizontal: 4, gap: 12 } as any}>
      {rows.map((r, i) => (
        <View key={i} style={{ flexDirection: "row", justifyContent: "center", gap: 5 }}>
          {r.split("").map((ch) => <View key={ch} style={{ flex: 1, maxWidth: 34, height: 44, borderRadius: 6, backgroundColor: key, alignItems: "center", justifyContent: "center" }}><Txt size={18} w={500} style={{ color: ink }}>{ch}</Txt></View>)}
        </View>
      ))}
      <View style={{ flexDirection: "row", gap: 6, paddingHorizontal: 2 }}>
        <View style={{ width: 90, height: 44, borderRadius: 6, backgroundColor: key, opacity: 0.6 }} />
        <View style={{ flex: 1, height: 44, borderRadius: 6, backgroundColor: key }} />
        <View style={{ width: 90, height: 44, borderRadius: 6, backgroundColor: key, opacity: 0.6 }} />
      </View>
    </View>
  );
}

export default Sentry.wrap(RootLayout);
