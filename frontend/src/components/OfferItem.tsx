import { Offer } from '@/types'
import { useState } from 'react'
import MealVisualizer from './MealVisualizer'
import { colors } from '@/config/colors'
import { Icon } from '@iconify/react'

interface OfferItemProps {
  offer: Offer
}

function formatPrice(price: number): string {
  return price.toLocaleString('de-DE', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })
}

function formatTitle(title: string): string {
  // Convert ALL CAPS to Title Case for better readability
  // Handle Icelandic characters properly
  if (title === title.toUpperCase() && title.length > 3) {
    return title.charAt(0).toUpperCase() + title.slice(1).toLowerCase()
  }
  return title
}


export default function OfferItem({ offer }: OfferItemProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    console.log('Offer clicked, current state:', isExpanded)
    console.log('Offer name:', offer.name)
    setIsExpanded(!isExpanded)
    console.log('New state will be:', !isExpanded)
  }

  return (
    <div className="relative group w-full">
      <div 
        className="p-4 cursor-pointer hover:shadow-lg transition-all duration-300 w-full border-t border-b border-gray-100 select-none"
        style={{ backgroundColor: colors.surface }}
        onClick={handleClick}
        onMouseDown={(e) => e.preventDefault()}
      >
        {/* Main content - always visible */}
        <div className="flex items-start justify-between gap-4">
          {/* Left side - Title and Food visualization */}
          <div className="flex-1 min-w-0">
            {/* Offer Title */}
            <h3 className="text-md font-bold mb-1" style={{ color: colors.primary }}>
              {formatTitle(offer.name)}
            </h3>

            {offer.description && (
              <p className="text-xs mb-2" style={{ color: colors.gray[500] }}>
                {offer.description.length > 30 ? `${offer.description.slice(0, 30)}...` : offer.description}
              </p>
            )}
            
            {/* Food Visualization - Compact */}
            <div className="mb-3">
              <MealVisualizer offer={offer} showDetails={false} />
            </div>
            
            {/* Standardized Tags */}
            <div className="flex flex-wrap gap-1 mb-2">
              {offer.standardized_tags?.map((tag, index) => (
                <div 
                  key={index}
                  className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium"
                  style={{ 
                    backgroundColor: `${tag.color}15`,
                    color: tag.color,
                    border: `1px solid ${tag.color}30`
                  }}
                >
                  <Icon icon={tag.icon} className="w-3 h-3" />
                  <span>{tag.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right side - Price and Tags */}
          <div className="flex flex-col items-end gap-3 flex-shrink-0">
            {/* Price with price per person */}
            {offer.price_kr !== null ? (
              <div className="text-right" style={{ 
                color: '#0073aa'
              }}>
                <p className="text-md font-bold">
                  {formatPrice(offer.price_kr)} kr.
                </p>
                {offer.suits_people && offer.suits_people > 1 && (
                  <p className="text-xs font-medium mt-1" style={{ 
                    color: colors.gray[500] 
                  }}>
                    ({formatPrice(Math.round(offer.price_kr / offer.suits_people))} kr./mann)
                  </p>
                )}
              </div>
            ) : (
              <p className="text-sm font-medium px-3 py-1 rounded-full" style={{ 
                color: colors.secondary,
                backgroundColor: colors.gray[100] 
              }}>
                Sjá nánar
              </p>
            )}

            {/* Additional tags with new styling */}
            <div className="flex flex-wrap gap-1 justify-end mt-2">
              {/* People count with new tag styling */}
              {offer.suits_people && (
                <div className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium" style={{ 
                  backgroundColor: `${colors.info}15`,
                  color: colors.info,
                  border: `1px solid ${colors.info}30`
                }}>
                  <Icon icon="mdi:people" className="w-3 h-3" />
                  <span>{offer.suits_people}</span>
                </div>
              )}
              
              {/* Pickup/Delivery with new tag styling */}
              {offer.pickup_delivery && (
                <div className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium" style={{ 
                  backgroundColor: `${colors.success}15`,
                  color: colors.success,
                  border: `1px solid ${colors.success}30`
                }}>
                  {offer.pickup_delivery === 'sækja' ? (
                    <>
                      <Icon icon="mdi:package-variant" className="w-3 h-3" />
                      <span>Sótt</span>
                    </>
                  ) : offer.pickup_delivery === 'Delivery' ? (
                    <>
                      <Icon icon="mdi:truck" className="w-3 h-3" />
                      <span>Heimsent</span>
                    </>
                  ) : (
                    <>
                      <Icon icon="mdi:information" className="w-3 h-3" />
                      <span>{offer.pickup_delivery}</span>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Expand/Collapse indicator */}
          <div className="flex items-center ml-2">
            <Icon 
              icon={isExpanded ? "mdi:chevron-up" : "mdi:chevron-down"} 
              className="w-5 h-5 transition-transform duration-200"
              style={{ color: colors.secondary }}
            />
          </div>
        </div>

        {/* Expanded content - shown when expanded */}
        {isExpanded && (
          <div className="mt-4 pt-4 space-y-3" style={{ borderTop: `1px solid ${colors.gray[200]}` }}>
            {/* Detailed Food Visualization */}
            <MealVisualizer offer={offer} showDetails={true} />
            
            {/* Description */}
            {offer.description && (
              <div className="bg-gray-50 p-3 rounded-lg">
                <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Lýsing</h4>
                <p className="text-sm leading-relaxed" style={{ color: colors.secondary }}>
                  {offer.description}
                </p>
              </div>
            )}
            

          </div>
        )}
      </div>
    </div>
  )
} 