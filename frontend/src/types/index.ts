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
}

export interface Restaurant {
  id: number
  name: string
  website: string | null
  menu_page?: string | null
  offers_page?: string | null
  created_at?: string
  offers: Offer[]
}

export interface RestaurantResponse {
  restaurants: Restaurant[]
  total_offers: number
  last_updated: string
} 