import { Offer } from '@/types'
import { useState } from 'react'

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
  return new Intl.NumberFormat('is-IS').format(price)
}

export default function OfferItem({ offer }: OfferItemProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="relative group">
      <div 
        className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm cursor-pointer hover:shadow-md transition-shadow w-full"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {/* Offer Title */}
        <h3 className="text-md font-semibold text-gray-800 truncate mb-1">
          {offer.name}
        </h3>
        
        {/* Price */}
        {offer.price_kr !== null ? (
          <p className="text-sm text-green-700 font-medium mb-2">
            {formatPrice(offer.price_kr)} kr.
          </p>
        ) : (
          <p className="text-sm text-gray-500 font-medium mb-2">
            Sjá nánar
          </p>
        )}

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {/* People count */}
          {offer.suits_people && (
            <div className="flex items-center space-x-1 text-gray-500 text-sm">
              <span>👤</span>
              <span>{offer.suits_people}</span>
            </div>
          )}
          
          {/* Pickup/Delivery */}
          {offer.pickup_delivery && (
            <div className="bg-green-100 text-green-800 text-xs font-medium px-2 py-0.5 rounded-full">
              {offer.pickup_delivery === 'Pickup' || offer.pickup_delivery === 'sækja' ? 'Sótt' : offer.pickup_delivery === 'Delivery' ? 'Heimsent' : offer.pickup_delivery}
            </div>
          )}
          
          {/* Available hours */}
          {offer.available_hours && (
            <div className="bg-orange-100 text-orange-800 text-xs font-medium px-2 py-0.5 rounded-full">
              {offer.available_hours}
            </div>
          )}
          
          {/* Available days */}
          {offer.available_weekdays && (
            <div className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded-full">
              {formatWeekdays(offer.available_weekdays)}
            </div>
          )}
        </div>

        {/* Description - shown when expanded on mobile or hover on desktop */}
        {offer.description && (
          <>
            {/* Mobile: Expanded description */}
            {isExpanded && (
              <div className="mt-3 pt-3 border-t border-gray-100 md:hidden">
                <p className="text-sm text-gray-600 leading-relaxed">
                  {offer.description}
                </p>
              </div>
            )}
            
            {/* Desktop: Hover description */}
            <div className="hidden md:block absolute left-0 right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg p-3 shadow-lg z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none group-hover:pointer-events-auto">
              <p className="text-sm text-gray-600 leading-relaxed">
                {offer.description}
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
} 