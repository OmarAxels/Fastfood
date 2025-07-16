export const colors = {
  primary: '#1A202C',      // Deep charcoal for text
  secondary: '#4A5568',    // Medium gray for secondary elements
  background: '#F7FAFC',   // Clean off-white background
  surface: '#FFFFFF',      // Pure white for cards
  accent: '#E53E3E',       // Vibrant red for prices and highlights
  success: '#38A169',      // Green for positive actions
  info: '#3182CE',         // Blue for informational elements
  warning: '#D69E2E',      // Orange for warnings
  purple: '#805AD5',       // Purple for variety
  pink: '#D53F8C',         // Pink for variety
  white: '#FFFFFF',
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6', 
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827'
  }
} as const

export const restaurantThemes = {
  'KFC': '#E4002B',
  'Domino\'s Pizza': '#0078D4', 
  'Subway': '#00A651',
  'Hlöllabátar': '#DC291A',
  'Búllan': '#DC291A',
  'Noodle Station': '#FF6B35'
} as const

export type ColorKey = keyof typeof colors
export type RestaurantName = keyof typeof restaurantThemes 