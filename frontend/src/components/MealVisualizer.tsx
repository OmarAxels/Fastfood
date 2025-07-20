import { Offer, FoodItem as FoodItemType } from '@/types'
import FoodItem from './FoodItem'

interface MealVisualizerProps {
  offer: Offer
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

const hasQuantityColumn = (items: FoodItemType[]) => {
  return items.some(item => item.quantity > 1)
}
// Component to display choice items
function ChoiceGroup({ items }: { items: FoodItemType[] }) {
  if (items.length === 0) return null
  // reduce font size
  return (
    <div className="flex items-center gap-2 p-2 rounded-lg border border-dashed border-gray-300 bg-gray-50 w-fit text-sm">
      <div className="flex items-center gap-1">
        {items.map((item, index) => (
          <div key={index} className="flex items-center gap-1">
            <FoodItem item={item} />
            {index < items.length - 1 && (
              <span className="text-xs text-gray-500 mx-1">eða</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default function MealVisualizer({ offer, }: MealVisualizerProps) {
  // Detailed view
  if (!offer.food_items || offer.food_items.length === 0) {
    return (
      <></>
    )
  }

  // Get all food items from all categories
  const allFoodItems = [
    ...(offer.main_items || []),
    ...(offer.side_items || []),
    ...(offer.drink_items || []),
    ...(offer.dessert_items || [])
  ]

  return (
    <div className="space-y-3">
      {/* All Food Items - Simple List Layout */}
      <div className="bg-gray-50 p-1 rounded-lg">
        <div className="space-y-2">
          {(() => {
            const { regularItems, choiceGroups } = groupItemsByChoices(allFoodItems)
            return (
              <>
                <div className="space-y-1">
                  {regularItems.map((item, index) => (
                    <FoodItem key={index} item={item} hasQuantityColumn={hasQuantityColumn(regularItems)} />
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
    </div>
  )
} 