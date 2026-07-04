{
  "meta": {
    "app_type": "single-page internal operations dashboard",
    "audience": "content ops / marketing ops power users",
    "brand_attributes": [
      "fast",
      "trustworthy",
      "premium-neutral",
      "dense-but-readable",
      "action-first"
    ],
    "design_style_fusion": {
      "layout_principle": "Swiss/International Typographic Style (clear grid, strong hierarchy)",
      "component_style": "modern shadcn/ui with crisp borders + subtle elevation (no transparency)",
      "interaction_style": "ops-console micro-feedback (status dots, toasts, progress, keyboard-first)"
    }
  },

  "design_tokens": {
    "fonts": {
      "google_fonts_import": "@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');",
      "font_family": {
        "heading": "'Space Grotesk', ui-sans-serif, system-ui",
        "body": "'IBM Plex Sans', ui-sans-serif, system-ui",
        "mono": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace"
      },
      "type_scale_tailwind": {
        "h1": "text-4xl sm:text-5xl lg:text-6xl font-semibold tracking-tight",
        "h2": "text-base md:text-lg font-medium text-muted-foreground",
        "section_title": "text-sm font-semibold tracking-wide uppercase",
        "body": "text-sm md:text-base",
        "small": "text-xs text-muted-foreground"
      },
      "numbers": {
        "kpi": "tabular-nums",
        "duration": "font-mono tabular-nums"
      }
    },

    "spacing": {
      "page_padding": "px-4 sm:px-6 lg:px-8",
      "section_gap": "gap-4 sm:gap-6",
      "card_padding": "p-4 sm:p-5",
      "table_cell_padding": "py-2.5 px-3",
      "table_density_note": "Compact rows, but keep 44px min tap targets for mobile actions (use stacked card layout on mobile)."
    },

    "radius": {
      "--radius": "10px",
      "usage": {
        "cards": "rounded-xl",
        "inputs": "rounded-md",
        "chips": "rounded-full",
        "thumbnail": "rounded-md"
      }
    },

    "shadows": {
      "shadow_1": "0 1px 2px rgba(16,24,40,0.06)",
      "shadow_2": "0 8px 24px rgba(16,24,40,0.10)",
      "shadow_focus": "0 0 0 3px rgba(14,165,233,0.25)",
      "usage": {
        "cards": "shadow-[0_1px_2px_rgba(16,24,40,0.06)]",
        "sticky_header_shadow_on_scroll": "shadow-[0_2px_10px_rgba(16,24,40,0.06)]"
      }
    },

    "color_system": {
      "note": "No transparent backgrounds. Use solid surfaces + subtle borders. Accent is ocean-cyan (professional, non-purple).",
      "base": {
        "bg": "#F7F8FA",
        "surface": "#FFFFFF",
        "surface_2": "#F2F4F7",
        "text": "#0B1220",
        "text_muted": "#5B667A",
        "border": "#E4E7EC"
      },
      "accent": {
        "primary": "#0EA5E9",
        "primary_hover": "#0284C7",
        "primary_active": "#0369A1",
        "ring": "#38BDF8"
      },
      "semantic": {
        "success": "#16A34A",
        "success_bg": "#EAF7EF",
        "warning": "#D97706",
        "warning_bg": "#FFF4E5",
        "danger": "#DC2626",
        "danger_bg": "#FEECEC",
        "info": "#2563EB",
        "info_bg": "#EEF2FF",
        "neutral_bg": "#F2F4F7"
      },
      "table_row_state_tints": {
        "pending": {
          "bg": "#F8FAFC",
          "border": "#E2E8F0",
          "chip": "#64748B"
        },
        "preparing": {
          "bg": "#F0F9FF",
          "border": "#BAE6FD",
          "chip": "#0284C7"
        },
        "ready": {
          "bg": "#F0FDF4",
          "border": "#BBF7D0",
          "chip": "#16A34A"
        },
        "error": {
          "bg": "#FEF2F2",
          "border": "#FECACA",
          "chip": "#DC2626"
        }
      },
      "platform_badges": {
        "instagram": {
          "bg": "#FFF1F7",
          "text": "#9D174D",
          "border": "#FBCFE8",
          "note": "Use solid badge; optional tiny 2px left accent bar with IG gradient ONLY as decorative (<= 20% viewport rule)."
        },
        "tiktok": {
          "bg": "#ECFEFF",
          "text": "#155E75",
          "border": "#A5F3FC"
        },
        "youtube": {
          "bg": "#FEF2F2",
          "text": "#991B1B",
          "border": "#FECACA"
        },
        "facebook": {
          "bg": "#EFF6FF",
          "text": "#1D4ED8",
          "border": "#BFDBFE"
        }
      }
    },

    "css_custom_properties": {
      "instructions": "Update /app/frontend/src/index.css :root tokens to match these HSL values (shadcn uses HSL). Keep dark mode optional.",
      "light_hsl": {
        "--background": "210 20% 98%",
        "--foreground": "222 47% 11%",
        "--card": "0 0% 100%",
        "--card-foreground": "222 47% 11%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "222 47% 11%",
        "--primary": "199 89% 48%",
        "--primary-foreground": "0 0% 100%",
        "--secondary": "210 20% 96%",
        "--secondary-foreground": "222 47% 11%",
        "--muted": "210 20% 96%",
        "--muted-foreground": "215 16% 47%",
        "--accent": "210 20% 96%",
        "--accent-foreground": "222 47% 11%",
        "--destructive": "0 84% 60%",
        "--destructive-foreground": "0 0% 100%",
        "--border": "220 13% 91%",
        "--input": "220 13% 91%",
        "--ring": "199 89% 58%",
        "--radius": "0.625rem"
      },
      "dark_hsl_optional": {
        "--background": "222 47% 7%",
        "--foreground": "210 40% 98%",
        "--card": "222 47% 9%",
        "--card-foreground": "210 40% 98%",
        "--popover": "222 47% 9%",
        "--popover-foreground": "210 40% 98%",
        "--primary": "199 89% 58%",
        "--primary-foreground": "222 47% 11%",
        "--secondary": "217 19% 16%",
        "--secondary-foreground": "210 40% 98%",
        "--muted": "217 19% 16%",
        "--muted-foreground": "215 20% 65%",
        "--accent": "217 19% 16%",
        "--accent-foreground": "210 40% 98%",
        "--destructive": "0 63% 31%",
        "--destructive-foreground": "210 40% 98%",
        "--border": "217 19% 16%",
        "--input": "217 19% 16%",
        "--ring": "199 89% 58%"
      }
    }
  },

  "layout": {
    "page_structure": {
      "top_bar": {
        "left": "Title + subtitle + last updated",
        "right": "Theme toggle (optional) + help link",
        "height": "64px",
        "classes": "sticky top-0 z-30 bg-[var(--surface)] border-b"
      },
      "summary_strip": {
        "content": "3 KPI cards: Total links, Ready, Errors (+ optional Preparing)",
        "grid": "grid grid-cols-2 lg:grid-cols-4 gap-3",
        "kpi_card": "Card with icon + number (tabular-nums)"
      },
      "bulk_action_bar": {
        "placement": "below KPIs, above filters",
        "behavior": "stays visible on scroll on desktop; collapses into overflow menu on mobile",
        "classes": "sticky top-[64px] z-20 bg-[var(--surface)] border-b"
      },
      "filters": {
        "content": "Search input + platform filter chips + status filter",
        "layout": "flex flex-col gap-3 md:flex-row md:items-center md:justify-between"
      },
      "main": {
        "desktop": "Table with sticky header inside ScrollArea",
        "mobile": "Stacked cards (each row becomes a card with actions)"
      },
      "right_panel_optional": {
        "pattern": "Resizable panel or Sheet/Drawer on smaller screens",
        "content": "Selected row details: full URL, thumbnail large, metadata, errors"
      }
    },

    "grid_system": {
      "max_width": "max-w-[1200px]",
      "container": "mx-auto",
      "desktop_columns": "12-col mental model; table spans 12, optional detail panel spans 4 with resizable",
      "breakpoints": {
        "mobile": "<640px",
        "tablet": "640-1024px",
        "desktop": ">=1024px"
      }
    }
  },

  "components": {
    "component_path": {
      "table": "/app/frontend/src/components/ui/table.jsx",
      "badge": "/app/frontend/src/components/ui/badge.jsx",
      "button": "/app/frontend/src/components/ui/button.jsx",
      "input": "/app/frontend/src/components/ui/input.jsx",
      "select": "/app/frontend/src/components/ui/select.jsx",
      "scroll_area": "/app/frontend/src/components/ui/scroll-area.jsx",
      "skeleton": "/app/frontend/src/components/ui/skeleton.jsx",
      "tooltip": "/app/frontend/src/components/ui/tooltip.jsx",
      "hover_card": "/app/frontend/src/components/ui/hover-card.jsx",
      "sonner_toast": "/app/frontend/src/components/ui/sonner.jsx",
      "tabs_optional": "/app/frontend/src/components/ui/tabs.jsx",
      "sheet_drawer": "/app/frontend/src/components/ui/sheet.jsx",
      "drawer": "/app/frontend/src/components/ui/drawer.jsx",
      "collapsible": "/app/frontend/src/components/ui/collapsible.jsx",
      "progress": "/app/frontend/src/components/ui/progress.jsx",
      "switch": "/app/frontend/src/components/ui/switch.jsx",
      "separator": "/app/frontend/src/components/ui/separator.jsx",
      "card": "/app/frontend/src/components/ui/card.jsx"
    },

    "table_spec": {
      "columns": [
        "INF ID",
        "Platform",
        "Link (truncate + copy)",
        "Status",
        "Creator",
        "Duration",
        "Thumbnail",
        "Actions"
      ],
      "sticky_header": {
        "container": "ScrollArea with fixed height (calc(100vh - header - filters))",
        "header_classes": "sticky top-0 z-10 bg-white border-b",
        "avoid_transparency": true
      },
      "row_hover": "hover:bg-slate-50",
      "row_selected": "data-[state=selected]:bg-slate-100",
      "horizontal_scroll": "Wrap table in div with overflow-x-auto; keep min-w-[980px] on desktop",
      "mobile_fallback": "Render cards instead of table under sm breakpoint"
    },

    "row_states": {
      "pending": {
        "visual": "neutral chip + subtle left border",
        "classes": "bg-[#F8FAFC] border-l-4 border-l-[#E2E8F0]",
        "icon": "Clock / CircleDot",
        "primary_action": "Prepare"
      },
      "preparing": {
        "visual": "info tint + spinner",
        "classes": "bg-[#F0F9FF] border-l-4 border-l-[#BAE6FD]",
        "icon": "Loader2 (spin)",
        "primary_action": "Preparing… (disabled)"
      },
      "ready": {
        "visual": "success tint + status dot",
        "classes": "bg-[#F0FDF4] border-l-4 border-l-[#BBF7D0]",
        "icon": "CheckCircle",
        "primary_action": "Download MP4 / MP3"
      },
      "error": {
        "visual": "danger tint + expandable error",
        "classes": "bg-[#FEF2F2] border-l-4 border-l-[#FECACA]",
        "icon": "AlertTriangle",
        "primary_action": "Retry"
      }
    },

    "badges": {
      "platform_badges": {
        "instagram": "Badge variant=outline with bg-[#FFF1F7] text-[#9D174D] border-[#FBCFE8]",
        "tiktok": "Badge variant=outline with bg-[#ECFEFF] text-[#155E75] border-[#A5F3FC]",
        "youtube": "Badge variant=outline with bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]",
        "facebook": "Badge variant=outline with bg-[#EFF6FF] text-[#1D4ED8] border-[#BFDBFE]"
      },
      "status_chip": {
        "pending": "bg-slate-100 text-slate-700",
        "preparing": "bg-sky-100 text-sky-800",
        "ready": "bg-emerald-100 text-emerald-800",
        "error": "bg-red-100 text-red-800"
      }
    },

    "buttons": {
      "hierarchy": {
        "primary": {
          "use_for": ["Prepare", "Prepare All"],
          "style": "Button default (primary accent)",
          "classes": "bg-[#0EA5E9] hover:bg-[#0284C7] active:bg-[#0369A1] text-white",
          "radius": "rounded-lg",
          "motion": "hover: translateY(-1px) shadow increase; active: scale-[0.98]"
        },
        "secondary": {
          "use_for": ["Download MP4", "Download MP3", "Download All MP4", "Download All MP3"],
          "style": "Button outline or secondary",
          "classes": "border-[#CFE8F6] text-[#075985] hover:bg-[#F0F9FF]",
          "note": "MP4 and MP3 should be visually grouped (ToggleGroup or ButtonGroup-like spacing)."
        },
        "tertiary": {
          "use_for": ["Retry", "Reset", "Copy link"],
          "style": "ghost",
          "classes": "hover:bg-slate-100 text-slate-700"
        },
        "danger": {
          "use_for": ["Reset (confirm)", "Clear errors"],
          "style": "destructive",
          "classes": "bg-[#DC2626] hover:bg-[#B91C1C] text-white"
        }
      },
      "sizes": {
        "sm": "h-8 px-3 text-sm",
        "md": "h-9 px-4 text-sm",
        "icon": "h-9 w-9"
      }
    },

    "thumbnail_preview": {
      "default_size": "56px square",
      "component": "HoverCard or Tooltip + AspectRatio",
      "loading": "Skeleton square 56x56",
      "hover_preview": "Show 240px preview with border + shadow_2",
      "classes": {
        "thumb": "h-14 w-14 rounded-md border border-[#E4E7EC] bg-white object-cover",
        "preview": "w-[240px] rounded-lg border border-[#E4E7EC] bg-white p-2 shadow-[0_8px_24px_rgba(16,24,40,0.10)]"
      }
    },

    "error_expand": {
      "component": "Collapsible",
      "behavior": "Row shows short error label; expand reveals full message + copy button",
      "copy": "Use Button ghost + tooltip",
      "classes": "text-xs font-mono bg-[#FFF7ED] border border-[#FED7AA] rounded-md p-2"
    },

    "toasts": {
      "library": "sonner",
      "patterns": {
        "bulk_prepare": "persistent toast with progress bar + cancel",
        "bulk_download": "toast per batch start + completion summary",
        "errors": "toast with count + 'View errors' action"
      },
      "style": {
        "position": "top-right",
        "tone": "neutral surface with left accent bar (primary/info/success/danger)",
        "no_transparency": true
      }
    },

    "empty_states": {
      "before_any_prepare": {
        "headline": "No metadata fetched yet",
        "body": "Click Prepare on a row or use Prepare All to fetch creator, duration, and thumbnail.",
        "cta": "Prepare All",
        "visual": "simple icon + dashed border card (solid background)"
      },
      "no_results_filter": {
        "headline": "No matches",
        "body": "Try clearing filters or searching by INF ID.",
        "cta": "Reset filters"
      }
    },

    "loading_states": {
      "table_skeleton": "Use Skeleton rows (8-10) with sticky header visible",
      "thumbnail_skeleton": "Skeleton className='h-14 w-14 rounded-md'",
      "button_loading": "Use lucide Loader2 with animate-spin"
    }
  },

  "motion": {
    "principles": [
      "No universal transition: never use transition-all",
      "Prefer short, crisp easing for ops tools",
      "Motion communicates state changes (preparing -> ready)"
    ],
    "durations": {
      "fast": "150ms",
      "base": "200ms",
      "slow": "280ms"
    },
    "easing": {
      "standard": "cubic-bezier(0.2, 0.8, 0.2, 1)",
      "emphasized": "cubic-bezier(0.2, 0.9, 0.2, 1)"
    },
    "micro_interactions": {
      "row_hover": "background tint + show quick actions (copy, open) fade-in",
      "primary_button": "hover:-translate-y-[1px] hover:shadow-sm active:scale-[0.98]",
      "status_change": "chip crossfade + subtle pulse on ready",
      "bulk_bar": "when active, slide-down 8px + fade"
    },
    "reduced_motion": "Respect prefers-reduced-motion: disable translate animations and pulses"
  },

  "accessibility": {
    "contrast": "All text must meet WCAG AA; avoid light gray text on white.",
    "focus": "Use visible focus ring: ring-2 ring-[--ring] ring-offset-2 ring-offset-background",
    "keyboard": [
      "Search focuses on '/' hotkey (optional)",
      "Enter triggers Prepare on selected row",
      "Arrow keys navigate rows (optional)"
    ],
    "aria": {
      "table": "Use proper <Table>, <TableHead>, <TableRow> semantics",
      "buttons": "aria-label for icon-only buttons",
      "toasts": "announce completion and errors"
    }
  },

  "responsive_patterns": {
    "table_to_cards": {
      "breakpoint": "sm",
      "mobile_card": {
        "layout": "Card with top row: INF + platform + status; middle: link + creator/duration; bottom: actions",
        "thumbnail": "right aligned 56px",
        "actions": "full-width buttons stacked (MP4 then MP3)"
      }
    },
    "bulk_actions_mobile": {
      "pattern": "Primary CTA visible; secondary actions in DropdownMenu",
      "avoid": "4 buttons in a row on mobile"
    }
  },

  "data_testid_conventions": {
    "rule": "All interactive and key informational elements MUST include data-testid in kebab-case describing role.",
    "examples": {
      "bulk_prepare_all": "data-testid=\"bulk-prepare-all-button\"",
      "bulk_download_mp4": "data-testid=\"bulk-download-mp4-button\"",
      "bulk_download_mp3": "data-testid=\"bulk-download-mp3-button\"",
      "bulk_reset": "data-testid=\"bulk-reset-button\"",
      "search_input": "data-testid=\"links-search-input\"",
      "platform_filter": "data-testid=\"platform-filter-select\"",
      "row_prepare": "data-testid=\"row-prepare-button-INF50\"",
      "row_download_mp4": "data-testid=\"row-download-mp4-button-INF50\"",
      "row_download_mp3": "data-testid=\"row-download-mp3-button-INF50\"",
      "row_retry": "data-testid=\"row-retry-button-INF50\"",
      "row_status": "data-testid=\"row-status-chip-INF50\"",
      "thumbnail": "data-testid=\"row-thumbnail-INF50\"",
      "error_expand": "data-testid=\"row-error-expand-INF50\"",
      "copy_link": "data-testid=\"row-copy-link-button-INF50\""
    }
  },

  "image_urls": {
    "note": "This app is utility-first; avoid decorative stock photos. Use simple inline SVG icons (lucide-react) and optional subtle noise texture via CSS.",
    "textures": [
      {
        "category": "background-texture",
        "description": "CSS noise overlay (no image download) applied to page background only (<= 10% opacity).",
        "url": "css://noise"
      }
    ]
  },

  "libraries": {
    "recommended": [
      {
        "name": "lucide-react",
        "why": "icons for status + actions",
        "install": "npm i lucide-react",
        "usage": "import { Loader2, CheckCircle, AlertTriangle, Copy, Download } from 'lucide-react'"
      },
      {
        "name": "framer-motion (optional)",
        "why": "bulk bar slide/fade + row state transitions",
        "install": "npm i framer-motion",
        "usage": "Use motion.div for bulk bar; respect prefers-reduced-motion"
      }
    ]
  },

  "instructions_to_main_agent": [
    "Replace CRA default App.css styles; do NOT center the app container.",
    "Update /app/frontend/src/index.css tokens to the provided HSL values; keep surfaces solid (no transparency).",
    "Implement single dashboard page with: TopBar -> KPI cards -> BulkActionBar -> Filters -> Table/ScrollArea.",
    "Use shadcn Table + ScrollArea for sticky header; wrap in overflow-x-auto for mobile safety.",
    "Implement per-row finite states: pending/preparing/ready/error with left border + chip + icon.",
    "Thumbnail column: show Skeleton until ready; then show 56px image with HoverCard preview.",
    "Buttons: Prepare is primary; MP4/MP3 are secondary outline; Retry is ghost; Reset is destructive with AlertDialog confirm.",
    "Bulk actions: Prepare All primary; downloads secondary; Reset tertiary/danger with confirm.",
    "Add search + platform filter (Select) + status filter; show 'no results' empty state.",
    "All interactive and key informational elements MUST include stable data-testid attributes (kebab-case).",
    "Do not use gradients except tiny decorative accents; never exceed 20% viewport; never on text-heavy areas.",
    "Ensure keyboard focus rings are visible and consistent; add aria-labels for icon-only buttons."
  ],

  "general_ui_ux_design_guidelines_appendix": "<General UI UX Design Guidelines>  \n    - You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n    - You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n   - NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals.\n</General UI UX Design Guidelines>"
}
