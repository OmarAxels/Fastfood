export interface FoodItem {
  type: string
  name: string
  category: 'main' | 'side' | 'drink' | 'dessert'
  icon: string
  quantity: number
  size?: {
    inches?: number
    liters?: number
    descriptor?: string
    unit?: string
  } | null
  modifiers: string[]
  phrase: string
}

export interface Offer {
  id: number
  name: string
  description: string
  price_kr: number | null
  available_weekdays: string | null
  available_hours: string | null
  availability_text: string | null
  pickup_delivery?: string | null
  suits_people?: number | null
  scraped_at?: string
  source_url?: string
  
  // Enhanced food information
  food_items?: FoodItem[]
  meal_type?: 'family' | 'combo' | 'sharing' | 'individual' | 'dessert' | 'snack' | 'unknown'
  is_combo?: boolean
  complexity_score?: number
  total_food_items?: number
  main_items?: FoodItem[]
  side_items?: FoodItem[]
  drink_items?: FoodItem[]
  dessert_items?: FoodItem[]
  visual_summary?: string
}

export interface Restaurant {
  id: number
  name: string
  website: string | null
  logo?: string | null
  menu_page?: string | null
  offers_page?: string | null
  created_at?: string
  offers: Offer[]
  background_color?: string | null
}

export interface RestaurantResponse {
  restaurants: Restaurant[]
  total_offers: number
  last_updated: string
}

export interface EnhancedOffer {
  offer_name: string
  description: string
  price_kr: number | null
  available_weekdays: string | null
  available_hours: string | null
  availability_text: string | null
  pickup_delivery?: string | null
  suits_people?: number | null
  scraped_at?: string
  source_url?: string
  restaurant_name: string
  
  // Enhanced food information
  food_items?: FoodItem[]
  meal_type?: 'family' | 'combo' | 'sharing' | 'individual' | 'dessert' | 'snack' | 'unknown'
  is_combo?: boolean
  complexity_score?: number
  total_food_items?: number
  main_items?: FoodItem[]
  side_items?: FoodItem[]
  drink_items?: FoodItem[]
  dessert_items?: FoodItem[]
  visual_summary?: string
}

export interface EnhancedOffersData {
  scraped_at: string
  total_offers: number
  restaurants: string[]
  offers: EnhancedOffer[]
} 