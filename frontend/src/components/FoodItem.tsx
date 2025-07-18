import { FoodItem as FoodItemType } from '@/types'
import { colors } from '@/config/colors'
import { Icon } from '@iconify/react'

interface FoodItemProps {
  item: FoodItemType
  showDetails?: boolean
}

export default function FoodItem({ item, showDetails = false }: FoodItemProps) {
  const getSizeText = () => {
    if (!item.size) return null

    if (item.size.inches) {
      return `${item.size.inches}\"`;
    }
    if (item.size.liters) {
      return `${item.size.liters}L`
    }
    if (item.size.descriptor) {
      return item.size.descriptor
    }
    return null
  }

  // Compute size letter for badge (L: lítið/small, M: miðlungs/medium, S: stórt/large)
  const getSizeLetter = () => {
    if (!item.size || !item.size.descriptor) return null
    const d = item.size.descriptor.toLowerCase()
    if (d.includes('lítið') || d === 'small') return 'L'
    if (d.includes('miðlungs') || d === 'medium') return 'M'
    if (d.includes('stórt') || d === 'large') return 'S'
    return null
  }

  const sizeText = getSizeText()
  const sizeLetter = getSizeLetter()
  const iconColor = item.icon_color || colors.primary

  if (!showDetails) {
    // Compact view - badge and icon
    return (
      <div className="flex items-center gap-2">
        {item.quantity > 1 && (
          <div className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 text-sm font-bold text-gray-700">
            {`${sizeLetter || ''}${item.quantity}`}
          </div>
        )}
        <Icon
          icon={item.icon}
          className="w-5 h-5"
          style={{ color: iconColor }}
        />
        {sizeText && (
          <span className="text-sm" style={{ color: colors.secondary }}>
            ({sizeText})
          </span>
        )}
      </div>
    )
  }

  // Detailed view
  return (
    <div
      className="flex items-center gap-3 px-3 py-2 rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
     /* style={{
        background: categoryColors.background,
        color: categoryColors.color,
      }}*/
    >
      {item.quantity > 1 && (
        <div className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 text-sm font-bold text-gray-700">
          {`${sizeLetter || ''}${item.quantity}`}
        </div>
      )}
      <Icon
        icon={item.icon}
        className="w-6 h-6"
        style={{ color: iconColor }}
      />
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-1">
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
