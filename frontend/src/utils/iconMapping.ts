import { colors } from '@/config/colors'

// Icon mapping for food items
export const getFoodIcon = (type: string, category: string): string => {
  // Map by specific food types first
  const typeIcons: Record<string, string> = {
    // Chicken
    'chicken': 'mdi:food-drumstick',
    'wings': 'mdi:food-drumstick',
    'breast': 'mdi:food-drumstick',
    
    // Beef
    'beef': 'mdi:food-steak',
    'burger': 'fluent-emoji:hamburger',
    'steak': 'mdi:food-steak',
    
    // Pizza
    'pizza': 'twemoji:pizza',
    
    // Fish
    'fish': 'mdi:fish',
    'salmon': 'mdi:fish',
    'cod': 'mdi:fish',
    
    // Sides
    'fries': 'noto:french-fries',
    'potato': 'mdi:food-french-fries',
    'rice': 'mdi:rice',
    'salad': 'noto:green-salad',
    'vegetables': 'mdi:food-apple',
    
    // Drinks
    'soda': 'mdi:cup',
    'cola': 'mdi:cup',
    'water': 'mdi:cup-water',
    'beer': 'mdi:beer',
    'wine': 'mdi:glass-wine',
    'coffee': 'mdi:coffee',
    'tea': 'mdi:tea',
    
    // Desserts
    'ice-cream': 'mdi:ice-cream',
    'cake': 'mdi:cake-variant',
    'cookie': 'mdi:cookie',
    
    // Sauces
    'sauce': 'mdi:food-variant',
    'ketchup': 'mdi:food-variant',
    'mayo': 'mdi:food-variant',
    'mustard': 'mdi:food-variant',
    
    // Generic by category
    'main': 'mdi:food',
    'side': 'mdi:food-fork-drink',
    'drink': 'mdi:cup',
    'dessert': 'mdi:cake-variant',
  }

  // Try to find by type first
  const typeKey = type.toLowerCase()
  if (typeIcons[typeKey]) {
    return typeIcons[typeKey]
  }

  // Fallback to category
  const categoryKey = category.toLowerCase()
  if (typeIcons[categoryKey]) {
    return typeIcons[categoryKey]
  }

  // Default fallback
  return 'mdi:food'
}

// Get icon color based on food type and category
export const getFoodIconColor = (type: string, category: string): string => {
  // Map by specific food types first
  const typeColors: Record<string, string> = {
    // Chicken - golden brown
    'chicken': '#D4AF37',
    'wings': '#D4AF37',
    'breast': '#D4AF37',
    
    // Beef - red/brown
    'beef': '#8B4513',
    'burger': '#8B4513',
    'steak': '#8B4513',
    
    // Pizza - orange/red
    'pizza': '#FF6B35',
    
    // Fish - blue
    'fish': '#4A90E2',
    'salmon': '#FF6B6B',
    'cod': '#4A90E2',
    
    // Sides - green/brown
    'fries': '#8B4513',
    'potato': '#8B4513',
    'rice': '#F4A460',
    'salad': '#228B22',
    'vegetables': '#228B22',
    
    // Drinks - blue/purple
    'soda': '#4A90E2',
    'cola': '#8B0000',
    'water': '#87CEEB',
    'beer': '#FFD700',
    'wine': '#8B0000',
    'coffee': '#8B4513',
    'tea': '#228B22',
    
    // Desserts - pink/purple
    'ice-cream': '#FF69B4',
    'cake': '#FF69B4',
    'cookie': '#D2691E',
    'dessert': '#FF69B4',
    
    // Sauces - orange/red
    'sauce': '#FF4500',
    'ketchup': '#FF0000',
    'mayo': '#FFFFF0',
    'mustard': '#FFD700',
  }

  // Try to find by type first
  const typeKey = type.toLowerCase()
  if (typeColors[typeKey]) {
    return typeColors[typeKey]
  }

  // Fallback to category colors
  const categoryColors: Record<string, string> = {
    'main': colors.accent,
    'side': colors.success,
    'drink': colors.info,
    'dessert': colors.pink,
  }

  const categoryKey = category.toLowerCase()
  if (categoryColors[categoryKey]) {
    return categoryColors[categoryKey]
  }

  // Default fallback
  return colors.primary
}

// Get icon size class based on context
export const getIconSizeClass = (size: 'sm' | 'md' | 'lg' = 'md'): string => {
  switch (size) {
    case 'sm':
      return 'w-4 h-4'
    case 'md':
      return 'w-5 h-5'
    case 'lg':
      return 'w-6 h-6'
    default:
      return 'w-5 h-5'
  }
} 