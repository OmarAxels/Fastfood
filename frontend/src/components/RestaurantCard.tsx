import { Restaurant } from '@/types'
import OfferItem from './OfferItem'
import { colors, restaurantThemes } from '@/config/colors'

interface RestaurantCardProps {
  restaurant: Restaurant
}

export default function RestaurantCard({ restaurant }: RestaurantCardProps) {
  if (!restaurant.offers || restaurant.offers.length === 0) {
    return null
  }

  // Get restaurant theme color or fallback to info color
  const themeColor = restaurantThemes[restaurant.name as keyof typeof restaurantThemes] || colors.info
  
  return (
    <div 
      className="rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-300 border border-gray-100" 
      style={{ 
        backgroundColor: colors.surface
      }}
    >
      {/* Restaurant Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {restaurant.logo && (
            <img 
              src={restaurant.logo} 
              alt={restaurant.name} 
              className="w-10 h-10 rounded-full shadow-sm" 
            />
          )}
          <div>
            <h2 className="text-xl font-bold" style={{ color: colors.primary }}>
              {restaurant.name}
            </h2>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-sm px-3 py-1 rounded-full font-medium shadow-sm" style={{ 
                color: colors.white,
                background: `linear-gradient(135deg, ${themeColor} 0%, ${themeColor}CC 100%)`
              }}>
                {restaurant.offers.length} tilboð
              </span>
            </div>
          </div>
        </div>
        
        {restaurant.website && (
          <a
            href={restaurant.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium hover:opacity-80 transition-all duration-200 px-3 py-2 rounded-lg hover:shadow-sm"
            style={{ 
              color: colors.info,
              backgroundColor: colors.gray[50]
            }}
          >
            Heimasíða ↗
          </a>
        )}
      </div>

      {/* Offers - One per row */}
      <div className="space-y-4">
        {restaurant.offers.map((offer) => (
          <OfferItem key={offer.id} offer={offer} />
        ))}
      </div>
    </div>
  )
} 