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
    'soda': 'mdi:bottle-soda-classic',
    'cola': 'mdi:bottle-soda-classic',
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
    'sauce': 'game-icons:ketchup',
    'ketchup': 'game-icons:ketchup',
    'mayo': 'game-icons:ketchup',
    'mustard': 'game-icons:ketchup',
    
    // Additional types
    'snack': 'mdi:food-variant',
    'fruit': 'mdi:food-apple',
    'sub': 'game-icons:sandwich',
    'sandwich': 'mdi:food-hot-dog',
    'wrap': 'mdi:food-hot-dog',
    'soup': 'mdi:food-variant',
    'curry': 'mdi:food-variant',
    'kebab': 'mdi:food-variant',
    'hotdog': 'mdi:food-hot-dog',
    'panini': 'mdi:food-hot-dog',
    'quesadilla': 'mdi:food-variant',
    'burrito': 'mdi:food-variant',
    'enchilada': 'mdi:food-variant',
    'fajita': 'mdi:food-variant',
    'gyro': 'mdi:food-variant',
    'shawarma': 'mdi:food-variant',
    'falafel': 'mdi:food-variant',
    'dumpling': 'mdi:food-variant',
    'springroll': 'mdi:food-variant',
    'eggroll': 'mdi:food-variant',
    'tempura': 'mdi:food-variant',
    'teriyaki': 'mdi:food-variant',
    'stirfry': 'mdi:food-variant',
    'lo mein': 'mdi:food-variant',
    'pad thai': 'mdi:food-variant',
    'pho': 'mdi:food-variant',
    'ramen': 'mdi:food-variant',
    'udon': 'mdi:food-variant',
    'soba': 'mdi:food-variant',
    'bibimbap': 'mdi:food-variant',
    'bulgogi': 'mdi:food-variant',
    'japchae': 'mdi:food-variant',
    'kimchi': 'mdi:food-variant',
    'taco': 'mdi:food-variant',
    'thai': 'mdi:food-variant',
    'noodlesoup': 'mdi:food-variant',
    'noodles': 'mdi:food-variant',
    'pasta': 'mdi:food-variant',
    'sushi': 'mdi:food-variant',
    
    // Generic by category
    'main': 'mdi:food',
    'side': 'mdi:food-fork-drink',
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

// Get main food type from offer
export const getMainFoodType = (offer: { main_items?: Array<{ type: string; quantity?: number }> }): { type: string; displayName: string; icon: string } => {
  // Check if we have main items
  if (offer.main_items && offer.main_items.length > 0) {
          // If multiple main items, create a combined display
      if (offer.main_items.length > 1) {
        const uniqueTypes = [...new Set(offer.main_items.map(item => item.type.toLowerCase()))]
        
                // Check if all items are the same type (e.g., multiple burgers)
        const allSameType = uniqueTypes.length === 1
        const totalQuantity = offer.main_items.reduce((sum, item) => sum + (item.quantity || 1), 0)
        
        // Map food types to display names
        const typeDisplayNames: Record<string, string> = {
          'chicken': 'Chicken',
          'wings': 'Chicken Wings',
          'breast': 'Chicken Breast',
          'beef': 'Beef',
          'burger': 'Burger',
          'steak': 'Steak',
          'pizza': 'Pizza',
          'fish': 'Fish',
          'salmon': 'Salmon',
          'cod': 'Cod',
          'taco': 'Taco',
          'thai': 'Thai',
          'noodlesoup': 'Noodle Soup',
          'noodles': 'Noodles',
          'pasta': 'Pasta',
          'sushi': 'Sushi',
          'sandwich': 'Sandwich',
          'wrap': 'Wrap',
          'salad': 'Salad',
          'soup': 'Soup',
          'curry': 'Curry',
          'kebab': 'Kebab',
          'hotdog': 'Hot Dog',
          'sub': 'Sub',
          'panini': 'Panini',
          'quesadilla': 'Quesadilla',
          'burrito': 'Burrito',
          'enchilada': 'Enchilada',
          'fajita': 'Fajita',
          'gyro': 'Gyro',
          'shawarma': 'Shawarma',
          'falafel': 'Falafel',
          'dumpling': 'Dumpling',
          'springroll': 'Spring Roll',
          'eggroll': 'Egg Roll',
          'tempura': 'Tempura',
          'teriyaki': 'Teriyaki',
          'stirfry': 'Stir Fry',
          'friedrice': 'Fried Rice',
          'lo mein': 'Lo Mein',
          'pad thai': 'Pad Thai',
          'pho': 'Pho',
          'ramen': 'Ramen',
          'udon': 'Udon',
          'soba': 'Soba',
          'bibimbap': 'Bibimbap',
          'bulgogi': 'Bulgogi',
          'japchae': 'Japchae',
          'kimchi': 'Kimchi',
          'snack': 'Snack',
          'fruit': 'Fruit',
          'cookie': 'Cookie',
          'dessert': 'Dessert',
          'ice-cream': 'Ice Cream',
          'cake': 'Cake',
          'drink': 'Drink',
          'soda': 'Soda',
          'water': 'Water',
          'coffee': 'Coffee',
          'tea': 'Tea',
          'beer': 'Beer',
          'wine': 'Wine',
          'sauce': 'Sauce',
          'ketchup': 'Ketchup',
          'mayo': 'Mayo',
          'mustard': 'Mustard',
          'fries': 'Fries',
          'potato': 'Potato',
          'rice': 'Rice',
          'vegetables': 'Vegetables'
        }
        
        // Create combined display name
        if (allSameType && totalQuantity > 1) {
          // If all items are the same type and total quantity > 1, show quantity
          const primaryType = uniqueTypes[0]
          const displayName = `${totalQuantity} ${typeDisplayNames[primaryType] || primaryType.charAt(0).toUpperCase() + primaryType.slice(1)}s`
          const icon = getFoodIcon(primaryType, 'main')
          return { type: primaryType, displayName, icon }
        } else {
          // Different types or single item
          const displayNames = uniqueTypes.map(type => 
            typeDisplayNames[type] || type.charAt(0).toUpperCase() + type.slice(1)
          )
          const displayName = displayNames.join(' + ')
          
          // Use the first type for icon (or a generic combo icon)
          const primaryType = uniqueTypes[0]
          const icon = getFoodIcon(primaryType, 'main')
          
          return { type: primaryType, displayName, icon }
        }
    } else {
      // Single main item - use original logic
      const mainItem = offer.main_items[0]
      const type = mainItem.type.toLowerCase()
      
      // Map food types to display names
      const typeDisplayNames: Record<string, string> = {
        'chicken': 'Chicken',
        'wings': 'Chicken Wings',
        'breast': 'Chicken Breast',
        'beef': 'Beef',
        'burger': 'Burger',
        'steak': 'Steak',
        'pizza': 'Pizza',
        'fish': 'Fish',
        'salmon': 'Salmon',
        'cod': 'Cod',
        'taco': 'Taco',
        'thai': 'Thai',
        'noodlesoup': 'Noodle Soup',
        'noodles': 'Noodles',
        'pasta': 'Pasta',
        'sushi': 'Sushi',
        'sandwich': 'Sandwich',
        'wrap': 'Wrap',
        'salad': 'Salad',
        'soup': 'Soup',
        'curry': 'Curry',
        'kebab': 'Kebab',
        'hotdog': 'Hot Dog',
        'sub': 'Sub',
        'panini': 'Panini',
        'quesadilla': 'Quesadilla',
        'burrito': 'Burrito',
        'enchilada': 'Enchilada',
        'fajita': 'Fajita',
        'gyro': 'Gyro',
        'shawarma': 'Shawarma',
        'falafel': 'Falafel',
        'dumpling': 'Dumpling',
        'springroll': 'Spring Roll',
        'eggroll': 'Egg Roll',
        'tempura': 'Tempura',
        'teriyaki': 'Teriyaki',
        'stirfry': 'Stir Fry',
        'friedrice': 'Fried Rice',
        'lo mein': 'Lo Mein',
        'pad thai': 'Pad Thai',
        'pho': 'Pho',
        'ramen': 'Ramen',
        'udon': 'Udon',
        'soba': 'Soba',
        'bibimbap': 'Bibimbap',
        'bulgogi': 'Bulgogi',
        'japchae': 'Japchae',
        'kimchi': 'Kimchi',
        'snack': 'Snack',
        'fruit': 'Fruit',
        'cookie': 'Cookie',
        'dessert': 'Dessert',
        'ice-cream': 'Ice Cream',
        'cake': 'Cake',
        'drink': 'Drink',
        'soda': 'Soda',
        'water': 'Water',
        'coffee': 'Coffee',
        'tea': 'Tea',
        'beer': 'Beer',
        'wine': 'Wine',
        'sauce': 'Sauce',
        'ketchup': 'Ketchup',
        'mayo': 'Mayo',
        'mustard': 'Mustard',
        'fries': 'Fries',
        'potato': 'Potato',
        'rice': 'Rice',
        'vegetables': 'Vegetables'
      }
      
      const displayName = typeDisplayNames[type] || type.charAt(0).toUpperCase() + type.slice(1)
      const icon = getFoodIcon(type, 'main')
      
      return { type, displayName, icon }
    }
  }
  
  // Fallback if no main items
  return { type: 'food', displayName: 'Mat', icon: 'mdi:food' }
}