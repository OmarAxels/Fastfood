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

  // Generate pastel color for restaurants without predefined theme
  const generatePastel = (str: string) => {
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash)
    }
    const h = hash % 360
    return `hsl(${h}, 70%, 85%)`
  }

  const themeColor = restaurantThemes[restaurant.name as keyof typeof restaurantThemes] || generatePastel(restaurant.name)


  // Generate initials from restaurant name
  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div 
      className="rounded-none" 

    >
      {/* Restaurant Header */}
      <div className="flex items-center justify-between px-4 py-4 sticky top-0 z-10 bg-slate-100" >
        <div className="flex items-center gap-3">
          {restaurant.logo ? (
            <img 
              src={restaurant.logo} 
              alt={restaurant.name} 
              className="w-10 h-10 rounded-full shadow-sm" 
            />
          ) : (
            <div 
              className="w-10 h-10 rounded-full shadow-sm flex items-center justify-center font-bold text-sm"
              style={{ 
                backgroundColor: themeColor,
                color: colors.white
              }}
            >
              {getInitials(restaurant.name)}
            </div>
          )}
          <div>
            <h2 className="text-xl font-bold" style={{ color: colors.primary }}>
              {restaurant.name}
            </h2>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium" style={{ 
            color: colors.gray[500]
          }}>
            {restaurant.offers.length} tilboð
          </span>
          
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
      </div>

      {/* Offers - Full width, alternating shade */}
      <div>
        {restaurant.offers.map((offer, idx) => (
          <OfferItem 
            key={offer.id} 
            offer={offer} 
          />
        ))}
      </div>
    </div>
  )
} 