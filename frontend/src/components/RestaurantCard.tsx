import { Restaurant } from '@/types'
import OfferItem from './OfferItem'

interface RestaurantCardProps {
  restaurant: Restaurant
}

function getRestaurantLogo(restaurantName: string): string {
  const name = restaurantName.toLowerCase()
  if (name.includes('dominos') || name.includes('domino')) {
    return '/dominos.png'
  } else if (name.includes('kfc')) {
    return '/kfc.png'
  }
  // Default placeholder if no logo found
  return '/dominos.png' // You can change this to a generic restaurant icon
}

function getRestaurantColors(restaurantName: string): { bg: string; text: string } {
  const name = restaurantName.toLowerCase()
  if (name.includes('dominos') || name.includes('domino')) {
    return { bg: 'bg-blue-50', text: 'text-blue-700' }
  } else if (name.includes('kfc')) {
    return { bg: 'bg-red-50', text: 'text-red-700' }
  }
  // Default colors
  return { bg: 'bg-red-50', text: 'text-red-700' }
}

export default function RestaurantCard({ restaurant }: RestaurantCardProps) {
  const logoSrc = getRestaurantLogo(restaurant.name)
  const colors = getRestaurantColors(restaurant.name)
  
  return (
    <div className="mb-6">
      {/* Restaurant Banner */}
      <div className="-mx-4 mb-4">
        {restaurant.website ? (
          <a
            href={restaurant.website}
            target="_blank"
            rel="noopener noreferrer"
            className={`block ${colors.bg} rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow`}
          >
            <div className="flex items-center space-x-3">
              <img
                src={logoSrc}
                alt={restaurant.name}
                className="w-8 h-8 rounded-md"
              />
              <div>
                <h2 className={`text-lg font-semibold ${colors.text}`}>
                  {restaurant.name}
                </h2>
                <p className="text-sm text-gray-600">
                  {restaurant.offers.length} tilboð
                </p>
              </div>
            </div>
          </a>
        ) : (
          <div className={`${colors.bg} rounded-xl p-4 shadow-sm`}>
            <div className="flex items-center space-x-3">
              <img
                src={logoSrc}
                alt={restaurant.name}
                className="w-8 h-8 rounded-md"
              />
              <div>
                <h2 className={`text-lg font-semibold ${colors.text}`}>
                  {restaurant.name}
                </h2>
                <p className="text-sm text-gray-600">
                  {restaurant.offers.length} tilboð
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Offer Cards */}
      <div className="grid grid-cols-3 gap-2">
        {restaurant.offers.map((offer) => (
          <OfferItem key={offer.id} offer={offer} />
        ))}
      </div>
    </div>
  )
} 