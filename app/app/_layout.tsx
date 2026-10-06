// Kök düzen: font, ayarlar, bağlantı, tema; sayfa yığını (sağdan kayarak gelir, "hareketi azalt" açıksa anında).
import { Sora_500Medium, Sora_600SemiBold, Sora_700Bold, Sora_800ExtraBold, useFonts } from "@expo-google-fonts/sora";
import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import React, { useEffect } from "react";
import { View } from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { connect } from "@/net/socket";
import { useSettings } from "@/store";
import { useTheme } from "@/theme";
import { UpdateCard } from "@/ui/update";

SplashScreen.preventAutoHideAsync().catch(() => {});

export default function RootLayout() {
  const [fontsLoaded] = useFonts({ Sora_500Medium, Sora_600SemiBold, Sora_700Bold, Sora_800ExtraBold });
  const loaded = useSettings((s) => s.loaded);
  const reduce = useSettings((s) => s.reduce_motion);
  const { c, dark } = useTheme();

  useEffect(() => { useSettings.getState().load(); }, []);
  useEffect(() => { if (loaded) connect(); }, [loaded]);
  useEffect(() => { if (fontsLoaded && loaded) SplashScreen.hideAsync().catch(() => {}); }, [fontsLoaded, loaded]);

  if (!fontsLoaded || !loaded) return <View style={{ flex: 1, backgroundColor: c.bg }} />;
  return (
    <SafeAreaProvider>
      <StatusBar style={dark ? "light" : "dark"} />
      <View style={{ flex: 1, backgroundColor: c.bg }}>
        <Stack screenOptions={{ headerShown: false, animation: reduce ? "none" : "slide_from_right", contentStyle: { backgroundColor: c.bg } }} />
        <UpdateCard />
      </View>
    </SafeAreaProvider>
  );
}
