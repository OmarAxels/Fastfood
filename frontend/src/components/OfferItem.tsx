import { Offer } from '@/types'

interface OfferItemProps {
  offer: Offer
}

function formatWeekdays(weekdays: string | null): string {
  if (!weekdays) return ''
  
  const dayMapping: Record<string, string> = {
    'mánudagur': 'Monday',
    'þriðjudagur': 'Tuesday',
    'miðvikudagur': 'Wednesday',
    'fimmtudagur': 'Thursday',
    'föstudagur': 'Friday',
    'laugardagur': 'Saturday',
    'sunnudagur': 'Sunday'
  }
  
  return weekdays.split(',')
    .map(day => dayMapping[day.trim()] || day.trim())
    .join(', ')
}

export default function OfferItem({ offer }: OfferItemProps) {
  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
      <div className="flex items-start justify-between gap-4">
        {/* Offer Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 text-lg mb-2">
            {offer.name}
          </h3>
          <p className="text-gray-600 text-sm leading-relaxed mb-3">
            {offer.description}
          </p>
          
          {/* Availability info */}
          {(offer.available_weekdays || offer.available_hours || offer.availability_text) && (
            <div className="flex flex-wrap gap-2 mb-2">
              {offer.available_weekdays && (
                <span className="inline-flex items-center bg-green-50 text-green-700 px-2 py-1 rounded-md text-xs font-medium">
                  📅 {formatWeekdays(offer.available_weekdays)}
                </span>
              )}
              {offer.available_hours && (
                <span className="inline-flex items-center bg-blue-50 text-blue-700 px-2 py-1 rounded-md text-xs font-medium">
                  🕒 {offer.available_hours}
                </span>
              )}
            </div>
          )}
          
          {/* Additional details */}
          <div className="flex flex-wrap gap-2 text-xs text-gray-500">
            {offer.pickup_delivery && (
              <span>📦 {offer.pickup_delivery}</span>
            )}
            {offer.suits_people && (
              <span>👥 For {offer.suits_people} people</span>
            )}
          </div>
        </div>
        
        {/* Price */}
        <div className="flex-shrink-0 text-right">
          {offer.price_kr !== null ? (
            <div className="bg-orange-50 border border-orange-200 rounded-lg px-3 py-2">
              <div className="text-lg font-bold text-orange-900">
                {offer.price_kr.toLocaleString()} kr
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
              <div className="text-sm text-gray-500 font-medium">
                See details
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 