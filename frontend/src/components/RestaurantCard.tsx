import { Restaurant } from '@/types'
import OfferItem from './OfferItem'

interface RestaurantCardProps {
  restaurant: Restaurant
}

export default function RestaurantCard({ restaurant }: RestaurantCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
      {/* Restaurant Header */}
      <div className="border-b border-gray-100 p-6 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {restaurant.name}
            </h2>
            {restaurant.website && (
              <a 
                href={restaurant.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-800 underline mt-1 inline-block"
              >
                Visit website →
              </a>
            )}
          </div>
          <div className="text-right">
            <div className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
              {restaurant.offers.length} offer{restaurant.offers.length !== 1 ? 's' : ''}
            </div>
          </div>
        </div>
      </div>

      {/* Offers List */}
      <div className="p-6 pt-4">
        <div className="space-y-4">
          {restaurant.offers.map((offer) => (
            <OfferItem key={offer.id} offer={offer} />
          ))}
        </div>
      </div>
    </div>
  )
} 