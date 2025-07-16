import { Offer } from '@/types'
import { useState } from 'react'
import MealVisualizer from './MealVisualizer'
import { colors } from '@/config/colors'
import { Icon } from '@iconify/react'

interface OfferItemProps {
  offer: Offer
}

function formatWeekdays(weekdays: string | null): string {
  if (!weekdays) return ''
  
  const dayMapping: Record<string, string> = {
    'mánudagur': 'Mán',
    'þriðjudagur': 'Þri',
    'miðvikudagur': 'Mið',
    'fimmtudagur': 'Fim',
    'föstudagur': 'Fös',
    'laugardagur': 'Lau',
    'sunnudagur': 'Sun'
  }
  
  return weekdays.split(',')
    .map(day => dayMapping[day.trim()] || day.trim())
    .join(', ')
}

function formatPrice(price: number): string {
  return price.toLocaleString('de-DE', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  })
}

// Better people icon component
const PeopleIcon = ({ count }: { count: number }) => (
  <div className="flex items-center space-x-1 text-xs px-2 py-1 transition-all duration-200" style={{ 
    color: colors.info
  }}>
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" className="flex-shrink-0">
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
    </svg>
    <span className="font-medium leading-none">{count}</span>
  </div>
)

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
        className="rounded-xl p-4 cursor-pointer hover:shadow-lg transition-all duration-300 w-full border border-gray-100 select-none"
        style={{ backgroundColor: colors.surface }}
        onClick={handleClick}
        onMouseDown={(e) => e.preventDefault()}
      >
        {/* Main content - always visible */}
        <div className="flex items-start justify-between gap-4">
          {/* Left side - Title and Food visualization */}
          <div className="flex-1 min-w-0">
            {/* Offer Title */}
            <h3 className="text-md font-bold mb-3" style={{ color: colors.primary }}>
              {offer.name}
            </h3>
            
            {/* Food Visualization - Compact */}
            <div className="mb-3">
              <MealVisualizer offer={offer} showDetails={false} />
            </div>
          </div>

          {/* Right side - Price and Tags */}
          <div className="flex flex-col items-end gap-3 flex-shrink-0">
            {/* Price with modern gradient background */}
            {offer.price_kr !== null ? (
              <div className="" style={{ 
                color: '#0073aa'
              }}>
                <p className="text-md font-bold">
                  {formatPrice(offer.price_kr)} kr.
                </p>
              </div>
            ) : (
              <p className="text-sm font-medium px-3 py-1 rounded-full" style={{ 
                color: colors.secondary,
                backgroundColor: colors.gray[100] 
              }}>
                Sjá nánar
              </p>
            )}

            {/* Tags with smooth modern styling */}
            <div className="flex flex-wrap gap-2 justify-end">
              {/* People count with custom icon */}
              {offer.suits_people && (
                <PeopleIcon count={offer.suits_people} />
              )}
              
              {/* Pickup/Delivery with floating style */}
              {offer.pickup_delivery && (
                <div className="text-xs font-medium px-2 py-1 transition-all duration-200" style={{ 
                  color: colors.success
                }}>
                  {offer.pickup_delivery === 'sækja' ? (
                    <>
                      <Icon icon="streamline-ultimate-color:car-4" className="inline-block mr-1" />
                      Sótt
                    </>
                  ) : offer.pickup_delivery === 'Delivery' ? (
                    <>
                      <Icon icon="mdi:truck" className="inline-block mr-1" />
                      Heimsent
                    </>
                  ) : (
                    offer.pickup_delivery
                  )}
                </div>
              )}
              
              {/* Available hours with floating style */}
              {offer.available_hours && (
                <div className="text-xs font-medium px-2 py-1 transition-all duration-200" style={{ 
                  color: colors.warning
                }}>
                  ⏰ {offer.available_hours}
                </div>
              )}
              
              {/* Available days with floating style */}
              {offer.available_weekdays && (
                <div className="text-xs font-medium px-2 py-1 transition-all duration-200" style={{ 
                  color: colors.pink
                }}>
                  📅 {formatWeekdays(offer.available_weekdays)}
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
            
            {/* Fallback if no food items */}
            {(!offer.food_items || offer.food_items.length === 0) && (
              <div className="bg-gray-50 p-3 rounded-lg">
                <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Upplýsingar</h4>
                <p className="text-sm leading-relaxed" style={{ color: colors.secondary }}>
                  Engin nánari upplýsingar um matvæli í boði fyrir þetta tilboð.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
} 