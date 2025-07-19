import { Offer, FoodItem as FoodItemType } from '@/types'
import FoodItem from './FoodItem'

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
  // Compact (collapsed) view – just show icons for a quick glance
  if (!showDetails) {
    const allFoodItems = [
      ...(offer.main_items || []),
      ...(offer.side_items || []),
      ...(offer.drink_items || []),
      ...(offer.dessert_items || [])
    ]

    if (allFoodItems.length === 0) return <></>

    return (
      <div className="flex flex-wrap items-center gap-2">
        {allFoodItems.slice(0, 8).map((item, index) => (
          <FoodItem key={index} item={item} showDetails={false} />
        ))}
      </div>
    )
  }

  // Check display properties from backend
  const displayProps = offer.display_properties || {
    show_category_headers: false,
    show_fallback_info: false,
    compact_view: true,
    max_tags: 3
  }

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
      <div className="bg-gray-50 p-3 rounded-lg">
        <div className="space-y-2">
          {(() => {
            const { regularItems, choiceGroups } = groupItemsByChoices(allFoodItems)
            return (
              <>
                <div className="space-y-2">
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
    </div>
  )
} 