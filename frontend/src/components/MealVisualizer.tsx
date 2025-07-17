import { Offer, FoodItem as FoodItemType } from '@/types'
import FoodItem from './FoodItem'
import { colors } from '@/config/colors'
import { Icon } from '@iconify/react'
import { getMainFoodType } from '@/utils/iconMapping'

interface MealVisualizerProps {
  offer: Offer
  showDetails?: boolean
}

// Helper function to group items by choice group
function groupItemsByChoices(items: FoodItemType[]) {
  const regularItems = items.filter(item => !item.is_choice)
  const choiceItems = items.filter(item => item.is_choice)
  
  // Group choice items by choice_group
  const choiceGroups: { [key: string]: FoodItemType[] } = {}
  choiceItems.forEach(item => {
    const group = item.choice_group || 'default'
    if (!choiceGroups[group]) {
      choiceGroups[group] = []
    }
    choiceGroups[group].push(item)
  })
  
  return { regularItems, choiceGroups }
}

// Component to display choice items
function ChoiceGroup({ items }: { items: FoodItemType[] }) {
  if (items.length === 0) return null
  
  return (
    <div className="flex items-center gap-2 p-2 rounded-lg border border-dashed border-gray-300 bg-gray-50">
      <span className="text-xs font-medium text-gray-600">Val:</span>
      <div className="flex items-center gap-1">
        {items.map((item, index) => (
          <div key={index} className="flex items-center gap-1">
            <FoodItem item={item} showDetails={true} />
            {index < items.length - 1 && (
              <span className="text-xs text-gray-500 mx-1">eða</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function MealVisualizer({ offer, showDetails = false }: MealVisualizerProps) {
  if (!showDetails) {

    return (
      <></>
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
      {/* Food Items by Category - Compact Grid Layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Main Items */}
        {offer.main_items && offer.main_items.length > 0 && (
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Aðalréttur</h4>
            <div className="space-y-1">
              {(() => {
                const { regularItems, choiceGroups } = groupItemsByChoices(offer.main_items)
                return (
                  <>
                    <div className="space-y-1">
                      {regularItems.map((item, index) => (
                        <FoodItem key={index} item={item} showDetails={true} />
                      ))}
                    </div>
                    {Object.entries(choiceGroups).map(([groupName, items]) => (
                      <ChoiceGroup key={groupName} items={items} />
                    ))}
                  </>
                )
              })()}
            </div>
          </div>
        )}

        {/* Side Items */}
        {offer.side_items && offer.side_items.length > 0 && (
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Meðlæti</h4>
            <div className="space-y-1">
              {(() => {
                const sideItemsNoSauce = offer.side_items.filter(item => item.category === 'side' && item.type !== 'sauce')
                const { regularItems, choiceGroups } = groupItemsByChoices(sideItemsNoSauce)
                return (
                  <>
                    <div className="space-y-1">
                      {regularItems.map((item, index) => (
                        <FoodItem key={index} item={item} showDetails={true} />
                      ))}
                    </div>
                    {Object.entries(choiceGroups).map(([groupName, items]) => (
                      <ChoiceGroup key={groupName} items={items} />
                    ))}
                  </>
                )
              })()}
            </div>
          </div>
        )}

        {/* Extras (Sauces) */}
        {offer.side_items && offer.side_items.filter(item => item.type === 'sauce').length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Auka</h4>
            <div className="space-y-2">
              {(() => {
                const sauceItems = offer.side_items.filter(item => item.type === 'sauce')
                const { regularItems, choiceGroups } = groupItemsByChoices(sauceItems)
                return (
                  <>
                    <div className="flex flex-wrap gap-2">
                      {regularItems.map((item, index) => (
                        <FoodItem key={index} item={item} showDetails={true} />
                      ))}
                    </div>
                    {Object.entries(choiceGroups).map(([groupName, items]) => (
                      <ChoiceGroup key={groupName} items={items} />
                    ))}
                  </>
                )
              })()}
            </div>
          </div>
        )}

        {/* Drinks */}
        {offer.drink_items && offer.drink_items.length > 0 && (
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Drykkir</h4>
            <div className="space-y-1">
              {(() => {
                const { regularItems, choiceGroups } = groupItemsByChoices(offer.drink_items)
                return (
                  <>
                    <div className="space-y-1">
                      {regularItems.map((item, index) => (
                        <FoodItem key={index} item={item} showDetails={true} />
                      ))}
                    </div>
                    {Object.entries(choiceGroups).map(([groupName, items]) => (
                      <ChoiceGroup key={groupName} items={items} />
                    ))}
                  </>
                )
              })()}
            </div>
          </div>
        )}

        {/* Desserts */}
        {offer.dessert_items && offer.dessert_items.length > 0 && (
          <div className="bg-gray-50 p-3 rounded-lg">
            <h4 className="text-sm font-semibold mb-2" style={{ color: colors.primary }}>Eftirréttur</h4>
            <div className="space-y-1">
              {(() => {
                const { regularItems, choiceGroups } = groupItemsByChoices(offer.dessert_items)
                return (
                  <>
                    <div className="space-y-1">
                      {regularItems.map((item, index) => (
                        <FoodItem key={index} item={item} showDetails={true} />
                      ))}
                    </div>
                    {Object.entries(choiceGroups).map(([groupName, items]) => (
                      <ChoiceGroup key={groupName} items={items} />
                    ))}
                  </>
                )
              })()}
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 