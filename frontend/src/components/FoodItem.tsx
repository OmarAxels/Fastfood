import { FoodItem as FoodItemType } from '@/types'
import { colors } from '@/config/colors'

interface FoodItemProps {
  item: FoodItemType
  showDetails?: boolean
}

export default function FoodItem({ item, showDetails = false }: FoodItemProps) {
  const getSizeText = () => {
    if (!item.size) return null
    
    if (item.size.inches) {
      return `${item.size.inches}"`
    }
    if (item.size.liters) {
      return `${item.size.liters}L`
    }
    if (item.size.descriptor) {
      return item.size.descriptor
    }
    return null
  }

  const getCategoryColor = () => {
    switch (item.category) {
      case 'main': 
        return { 
          background: `linear-gradient(135deg, ${colors.accent} 0%, #FF6B6B 100%)`,
          color: colors.white
        }
      case 'side': 
        return { 
          background: `linear-gradient(135deg, ${colors.success} 0%, #48BB78 100%)`,
          color: colors.white
        }
      case 'drink': 
        return { 
          background: `linear-gradient(135deg, ${colors.info} 0%, ${colors.purple} 100%)`,
          color: colors.white
        }
      case 'dessert': 
        return { 
          background: `linear-gradient(135deg, ${colors.pink} 0%, #ED64A6 100%)`,
          color: colors.white
        }
      default: 
        return { 
          background: `linear-gradient(135deg, ${colors.warning} 0%, #F6AD55 100%)`,
          color: colors.white
        }
    }
  }

  const sizeText = getSizeText()
  const categoryColors = getCategoryColor()

  if (!showDetails) {
    // Compact view - just icon and quantity
    return (
      <div className="flex items-center gap-1">
        <span className="text-base">{item.icon}</span>
        {item.quantity > 1 && (
          <span className="text-sm font-semibold" style={{ color: colors.primary }}>{item.quantity}x</span>
        )}
        {sizeText && (
          <span className="text-sm" style={{ color: colors.secondary }}>({sizeText})</span>
        )}
      </div>
    )
  }

  // Detailed view
  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded-lg shadow-sm hover:shadow-md transition-all duration-200" style={{ 
      background: categoryColors.background,
      color: categoryColors.color
    }}>
      <span className="text-base">{item.icon}</span>
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-1">
          {item.quantity > 1 && (
            <span className="text-sm font-bold">{item.quantity}x</span>
          )}
          <span className="text-sm font-semibold">{item.name}</span>
          {sizeText && (
            <span className="text-sm opacity-80">({sizeText})</span>
          )}
        </div>
        {item.modifiers.length > 0 && (
          <div className="text-xs opacity-80">
            {item.modifiers.slice(0, 2).join(', ')}
            {item.modifiers.length > 2 && '...'}
          </div>
        )}
      </div>
    </div>
  )
} 