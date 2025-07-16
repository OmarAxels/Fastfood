import { Offer } from '@/types'
import FoodItem from './FoodItem'
import { colors } from '@/config/colors'
import { Icon } from '@iconify/react'
import { getMainFoodType } from '@/utils/iconMapping'

interface MealVisualizerProps {
  offer: Offer
  showDetails?: boolean
}

export default function MealVisualizer({ offer, showDetails = false }: MealVisualizerProps) {
  if (!showDetails) {
    // Compact view - show main food type
    const mainFood = getMainFoodType(offer)
    return (
      <div className="flex items-center gap-1 text-sm font-medium" style={{ color: colors.primary }}>
        <Icon 
          icon={mainFood.icon} 
          className="w-4 h-4" 
          style={{ color: colors.accent }}
        />
        <span>{mainFood.displayName}</span>
      </div>
    )
  }

  // Detailed view
  if (!offer.food_items || offer.food_items.length === 0) {
    return (
      <div className="space-y-3">
        <div className="text-sm text-gray-500 italic">
          Engin nánari upplýsingar um matvæli í boði.
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3">

      {/* Food Items by Category */}
      <div className="space-y-3">
        {/* Main Items */}
        {offer.main_items && offer.main_items.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Aðalréttur</h4>
            <div className="flex flex-wrap gap-2">
              {offer.main_items.map((item, index) => (
                <FoodItem key={index} item={item} showDetails={true} />
              ))}
            </div>
          </div>
        )}

        {/* Side Items */}
        {offer.side_items && offer.side_items.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Meðlæti</h4>
            <div className="flex flex-wrap gap-2">
              {offer.side_items.filter(item => item.category === 'side' && item.type !== 'sauce').map((item, index) => (
                <FoodItem key={index} item={item} showDetails={true} />
              ))}
            </div>
          </div>
        )}

        {/* Extras (Sauces) */}
        {offer.side_items && offer.side_items.filter(item => item.type === 'sauce').length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Auka</h4>
            <div className="flex flex-wrap gap-2">
              {offer.side_items.filter(item => item.type === 'sauce').map((item, index) => (
                <FoodItem key={index} item={item} showDetails={true} />
              ))}
            </div>
          </div>
        )}

        {/* Drinks */}
        {offer.drink_items && offer.drink_items.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Drykkir</h4>
            <div className="flex flex-wrap gap-2">
              {offer.drink_items.map((item, index) => (
                <FoodItem key={index} item={item} showDetails={true} />
              ))}
            </div>
          </div>
        )}

        {/* Desserts */}
        {offer.dessert_items && offer.dessert_items.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Eftirréttur</h4>
            <div className="flex flex-wrap gap-2">
              {offer.dessert_items.map((item, index) => (
                <FoodItem key={index} item={item} showDetails={true} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 