/* eslint-disable @next/next/no-img-element */
import { FoodItem as FoodItemType } from '@/types'
import { colors } from '@/config/colors'
import { Icon } from '@iconify/react'

// Helper component to handle both iconify icons and custom images
const FoodIcon = ({ icon, className, style }: { icon: string; className?: string; style?: React.CSSProperties }) => {
  // Check if it's a custom image path (starts with /)
  if (icon.startsWith('/')) {
    return (
      <img 
        src={icon} 
        alt="food icon" 
        className={className}
        style={style}
      />
    )
  }
  
  // Otherwise use iconify
  return <Icon icon={icon} className={className} style={style} />
}

interface FoodItemProps {
  item: FoodItemType
  // Add this prop to indicate if ANY item in the list has quantity > 1
  hasQuantityColumn?: boolean
  isChoice?: boolean
}

export default function FoodItem({ item, hasQuantityColumn = false, isChoice = false }: FoodItemProps) {
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

  const sizeText = getSizeText()
  const iconColor = item.icon_color || colors.primary

  // Use CSS Grid for consistent alignment
  return (
    <div
      className="grid items-center gap-2 px-3 py-2 rounded-lg hover:shadow-md transition-all duration-200 w-fit"
      style={{
        gridTemplateColumns: hasQuantityColumn 
          ? 'auto auto 1fr' // quantity column, icon column, content column
          : 'auto 1fr' // just icon column and content column
      }}
    >
      {/* Quantity column - only render if hasQuantityColumn is true */}
      {hasQuantityColumn && (
        <div className="flex items-center justify-center w-6 h-6">
          {item.quantity > 1 && (
            <div className="flex items-center justify-center w-6 h-6 rounded-full text-sm font-bold text-gray-700">
              {`x${item.quantity}`}
            </div>
          )}
        </div>
      )}
      
      {/* Icon column */}
      <FoodIcon
        icon={item.icon}
        className={`${isChoice ? 'w-4 h-4' : 'w-6 h-6'}`}
        style={{ color: iconColor }}
      />
      
      {/* Content column */}
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-1">
          <span className={`text-sm font-semibold ${isChoice ? 'text-xs' : ''}`}>{item.name}</span>
          {sizeText && (
            <span className={`text-sm opacity-80 ${isChoice ? 'text-xs' : ''}`}>({sizeText})</span>
          )}
        </div>
        {item.modifiers.length > 0 && (
          <div className="text-xs opacity-80">
            {item.modifiers.slice(0, 4).join(', ')}
            {item.modifiers.length > 4 && '...'}
          </div>
        )}
      </div>
    </div>
  )
}