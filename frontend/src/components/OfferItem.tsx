import { Offer } from '@/types'
import { useState } from 'react'
import MealVisualizer from './MealVisualizer'
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

// Convert hex to rgba with given alpha percentage (0-1)
const hexToRgba = (hex: string, alpha: number) => {
  const res = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  if (!res) return hex // return original if not hex
  const r = parseInt(res[1], 16)
  const g = parseInt(res[2], 16)
  const b = parseInt(res[3], 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

// General category mapping for collapsed view
const GENERAL_CATEGORIES: {
  key: string;
  label: string;
  icon: string;
  color: string;
  synonyms: string[];
}[] = [
  {
    key: 'pizza',
    label: 'Pizza',
    icon: 'twemoji:pizza',
    color: '#FF6B35',
    synonyms: ['pizza', 'pizz']
  },
  {
    key: 'kjuklingur',
    label: 'Kjúklingur',
    icon: 'mdi:food-drumstick',
    color: '#D4AF37',
    synonyms: ['kjúkling', 'chicken', 'kjúklingur']
  },
  {
    key: 'fish',
    label: 'Fiskur',
    icon: 'mdi:fish',
    color: '#4A90E2',
    synonyms: ['fish', 'fiskur', 'lax', 'salmon', 'cod', 'þorskur']
  },
  {
    key: 'noodlesoup',
    label: 'Núðlusúpa',
    icon: 'mdi:food-variant',
    color: '#8B4513',
    synonyms: ['noodlesoup', 'núðlusúp', 'núðlusúpa']
  },
  {
    key: 'noodles',
    label: 'Núðlur',
    icon: 'mdi:food-variant',
    color: '#8B4513',
    synonyms: ['noodles', 'núðlur', 'pasta']
  },
  {
    key: 'burger',
    label: 'Borgari',
    icon: 'fluent-emoji:hamburger',
    color: '#3d9021',
    synonyms: ['burger', 'borgari']
  },
  {
    key: 'shrimp',
    label: 'Rækjur',
    icon: 'noto-v1:shrimp',
    color: '#FF6B6B',
    synonyms: ['shrimp', 'rækja', 'rækjur']
  },
  {
    key: 'beef',
    label: 'Nautakjöt',
    icon: 'mdi:food-steak',
    color: '#8B4513',
    synonyms: ['beef', 'nautakjöt', 'steak']
  },
  {
    key: 'sub',
    label: 'Sub',
    icon: 'game-icons:sandwich',
    color: '#228B22',
    synonyms: ['sub', 'sandwich', 'bátur', 'grænmetisbátur']
  },
  {
    key: 'fries',
    label: 'Franskar',
    icon: 'noto:french-fries',
    color: '#8B4513',
    synonyms: ['franskar', 'fries', 'pommes', 'kartöflur', 'potato']
  }
]

function extractGeneralTags(offer: Offer) {
  const allItems = [
    ...(offer.main_items || []),
    ...(offer.side_items || []),
    ...(offer.drink_items || []),
    ...(offer.dessert_items || [])
  ]

  const tags: { label: string; icon: string; color: string; key: string }[] = []

  GENERAL_CATEGORIES.forEach(cat => {
    const found = allItems.some(item => {
      const type = item.type?.toLowerCase() || ''
      const name = item.name?.toLowerCase() || ''
      return cat.synonyms.some(syn => type.includes(syn) || name.includes(syn))
    })
    if (found) {
      tags.push({ key: cat.key, label: cat.label, icon: cat.icon, color: cat.color })
    }
  })

  return tags
}

interface OfferItemProps {
  offer: Offer
  index?: number
  themeColor?: string
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
// Add background tag like food tags
const PeopleIcon = ({ count, color }: { count: number, color: string }) => (
  <div className="flex items-center space-x-1 text-xs px-2 py-1 transition-all duration-200 rounded-md" style={{ 
    backgroundColor: hexToRgba(color, 0.15),
    color: color,
    border: `1px solid ${hexToRgba(color, 0.3)}`
  }}>
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" className="flex-shrink-0">
      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
    </svg>
    <span className="font-medium leading-none">{count}</span>
  </div>
)

export default function OfferItem({ offer, index = 0, themeColor = '#ffffff' }: OfferItemProps) {
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
    <div className="relative group w-full border-b border-t border-gray-100 bg-slate-50">
      <div 
         className="p-4 cursor-pointer hover:opacity-95 transition-all duration-200 select-none"
       
        onClick={handleClick}
        onMouseDown={(e) => e.preventDefault()}
      >
        {/* Main content - always visible */}
        <div className="flex items-start justify-between gap-4">
          {/* Left side - Title and Food visualization */}
          <div className="flex-1 min-w-0">
            {/* Offer Title - If all caps then capitalize only first letter*/}
            <h3 className="text-md font-bold mb-3" style={{ color: colors.primary }}>
              {offer.name.toUpperCase() === offer.name ? offer.name.charAt(0).toUpperCase() + offer.name.slice(1).toLowerCase() : offer.name}
            </h3>
            
            {/* General Food Category Tags */}
            <div className="flex flex-wrap gap-1 mb-3">
              {extractGeneralTags(offer).map(tag => (
                <div
                  key={tag.key}
                  className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium"
                  style={{
                    backgroundColor: hexToRgba(tag.color, 0.12),
                    color: tag.color,
                    border: `1px solid ${hexToRgba(tag.color, 0.3)}`
                  }}
                >
                  <FoodIcon icon={tag.icon} className="w-3 h-3" />
                  <span>{tag.label}</span>
                </div>
              ))}
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
                <PeopleIcon count={offer.suits_people} color={colors.info} />
              )}
              
              {/* Pickup/Delivery with floating style */}
    
              {offer.pickup_delivery && (
                <div className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium"
                style={{
                  backgroundColor: hexToRgba(colors.success, 0.15),
                  color: colors.success,
                  border: `1px solid ${hexToRgba(colors.success, 0.3)}`
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
          <div className="mt-0 pt-0 space-y-0" style={{ borderTop: `1px solid ${colors.gray[200]}` }}>


            {/* Description */}
            {offer.description && (
              <div className="bg-gray-50 p-3 rounded-lg">
                <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Lýsing</h4>
                <p className="text-sm leading-relaxed" style={{ color: colors.secondary }}>
                  {offer.description}
                </p>
              </div>
            )}
                  {/* Detailed Food Visualization */}
                  <MealVisualizer offer={offer}/>

          
          </div>
        )}
      </div>
    </div>
  )
}