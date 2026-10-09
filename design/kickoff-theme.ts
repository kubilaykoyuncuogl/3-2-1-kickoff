/** Proposed Kickoff design baseline. Values use React Native logical units. */
export const kickoffTokens = {
  "version": "0.2.0",
  "status": "proposed-design-baseline",
  "units": "React Native logical units; text scales with OS preference",
  "color": {
    "light": {
      "background": "#F2F2F5",
      "surface": "#FFFFFF",
      "surfaceSubtle": "#E9E9EF",
      "textPrimary": "#1B1A21",
      "textSecondary": "#5F5D6B",
      "border": "#C9C8D3",
      "controlBorder": "#858292",
      "primary": "#5E4BC9",
      "primaryPressed": "#4A3AAE",
      "primaryText": "#FFFFFF",
      "secondary": "#E9E5FA",
      "secondaryPressed": "#DCD5F7",
      "secondaryText": "#4A3AAE",
      "focus": "#5E4BC9",
      "self": "#5E4BC9",
      "selfText": "#4A3AAE",
      "selfSubtle": "#E9E5FA",
      "opponent": "#E9A23B",
      "opponentText": "#895706",
      "opponentSubtle": "#FBEFD8",
      "successText": "#167A52",
      "successSubtle": "#DCF3E8",
      "dangerText": "#B72E48",
      "dangerSubtle": "#FBE1E7",
      "warningText": "#895706",
      "warningSubtle": "#FBEFD8",
      "disabledSurface": "#E9E9EF",
      "disabledText": "#5F5D6B",
      "timerFill": "#5F5D6B",
      "timerTrack": "#C9C8D3",
      "textPlaceholder": "#5F5D6B",
      "iconSecondary": "#5F5D6B"
    },
    "dark": {
      "background": "#131218",
      "surface": "#1C1B23",
      "surfaceSubtle": "#272630",
      "textPrimary": "#ECEBF2",
      "textSecondary": "#A09EAD",
      "border": "#3A3946",
      "controlBorder": "#747184",
      "primary": "#8C7CF0",
      "primaryPressed": "#9C8DF5",
      "primaryText": "#131218",
      "secondary": "#272443",
      "secondaryPressed": "#343057",
      "secondaryText": "#B3A7FF",
      "focus": "#B3A7FF",
      "self": "#8C7CF0",
      "selfText": "#B3A7FF",
      "selfSubtle": "#272443",
      "opponent": "#F0B45A",
      "opponentText": "#F4C77A",
      "opponentSubtle": "#3A2D14",
      "successText": "#4FCF93",
      "successSubtle": "#163528",
      "dangerText": "#FF7D96",
      "dangerSubtle": "#3C1B25",
      "warningText": "#F4C77A",
      "warningSubtle": "#3A2D14",
      "disabledSurface": "#272630",
      "disabledText": "#A09EAD",
      "timerFill": "#A09EAD",
      "timerTrack": "#3A3946",
      "textPlaceholder": "#A09EAD",
      "iconSecondary": "#A09EAD"
    }
  },
  "fontFamily": {
    "regular": "Sora-Regular",
    "medium": "Sora-Medium",
    "semibold": "Sora-SemiBold",
    "bold": "Sora-Bold",
    "extrabold": "Sora-ExtraBold"
  },
  "typography": {
    "display": {
      "fontFamily": "Sora-ExtraBold",
      "fontSize": 40,
      "lineHeight": 48
    },
    "screenTitle": {
      "fontFamily": "Sora-Bold",
      "fontSize": 28,
      "lineHeight": 36
    },
    "sectionTitle": {
      "fontFamily": "Sora-Bold",
      "fontSize": 20,
      "lineHeight": 28
    },
    "score": {
      "fontFamily": "Sora-Bold",
      "fontSize": 32,
      "lineHeight": 40
    },
    "timer": {
      "fontFamily": "Sora-Bold",
      "fontSize": 24,
      "lineHeight": 32
    },
    "body": {
      "fontFamily": "Sora-Regular",
      "fontSize": 16,
      "lineHeight": 24
    },
    "bodyStrong": {
      "fontFamily": "Sora-SemiBold",
      "fontSize": 16,
      "lineHeight": 24
    },
    "label": {
      "fontFamily": "Sora-SemiBold",
      "fontSize": 16,
      "lineHeight": 22
    },
    "input": {
      "fontFamily": "Sora-Regular",
      "fontSize": 18,
      "lineHeight": 26
    },
    "caption": {
      "fontFamily": "Sora-Medium",
      "fontSize": 14,
      "lineHeight": 20
    },
    "navigationTitle": {
      "fontFamily": "Sora-SemiBold",
      "fontSize": 20,
      "lineHeight": 28
    },
    "fieldLabel": {
      "fontFamily": "Sora-SemiBold",
      "fontSize": 14,
      "lineHeight": 20
    },
    "scoreCompact": {
      "fontFamily": "Sora-Bold",
      "fontSize": 20,
      "lineHeight": 28
    },
    "countdown": {
      "fontFamily": "Sora-ExtraBold",
      "fontSize": 64,
      "lineHeight": 72
    }
  },
  "space": {
    "1": 4,
    "2": 8,
    "3": 12,
    "4": 16,
    "5": 20,
    "6": 24,
    "8": 32,
    "10": 40,
    "12": 48
  },
  "radius": {
    "small": 8,
    "control": 12,
    "card": 16,
    "sheet": 24,
    "pill": 999
  },
  "size": {
    "touchTargetMin": 48,
    "buttonMinHeight": 52,
    "inputMinHeight": 56,
    "suggestionMinHeight": 56,
    "settingsRowMinHeight": 56,
    "screenGutter": 20,
    "icon": 24,
    "maxContentWidth": 560
  },
  "borderWidth": {
    "decorative": 1,
    "control": 1,
    "focus": 2
  },
  "motion": {
    "pressMs": 100,
    "feedbackMs": 160,
    "transitionMs": 220,
    "reducedMs": 0
  }
} as const;

export type KickoffThemeName = keyof typeof kickoffTokens.color;
export type KickoffColors = typeof kickoffTokens.color[KickoffThemeName];
export type KickoffTextVariant = keyof typeof kickoffTokens.typography;
export type KickoffThemePreference = "system" | KickoffThemeName;

export function resolveKickoffTheme(preference: KickoffThemePreference, systemScheme: "light" | "dark" | null | undefined): KickoffThemeName {
  return preference === "system" ? (systemScheme === "dark" ? "dark" : "light") : preference;
}
