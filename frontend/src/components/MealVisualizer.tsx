import { Offer } from '@/types'
import FoodItem from './FoodItem'
import { colors } from '@/config/colors'

interface MealVisualizerProps {
  offer: Offer
  showDetails?: boolean
}

export default function MealVisualizer({ offer, showDetails = false }: MealVisualizerProps) {
  if (!offer.food_items || offer.food_items.length === 0) {
    return null
  }


  if (!showDetails) {
    // Compact view - show visual summary without sauces and no plus signs
    const getFilteredVisualSummary = () => {
      if (offer.visual_summary) {
        // Remove plus signs and sauce icons from visual summary
        return offer.visual_summary
          .replace(/\s*\+\s*/g, ' ')  // Remove plus signs
          .replace(/🥄/g, '')          // Remove sauce icons
          .replace(/\s+/g, ' ')       // Clean up extra spaces
          .trim()
      }
      return '🍽️ Mat'
    }

    return (
      <div className="text-sm font-medium" style={{ color: colors.primary }}>
        {getFilteredVisualSummary()}
      </div>
    )
  }

  // Detailed view
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