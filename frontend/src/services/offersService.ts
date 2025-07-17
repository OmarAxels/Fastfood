import { EnhancedOffersData, Restaurant } from '@/types'

export class OffersService {
  private static instance: OffersService
  private cachedData: { restaurants: Restaurant[], total_offers: number, last_updated: string } | null = null
  private lastFetch: number = 0
  private readonly CACHE_DURATION = 5 * 60 * 1000 // 5 minutes
  private readonly API_BASE_URL = 'https://fastfood-production-2985.up.railway.app'

  static getInstance(): OffersService {
    if (!OffersService.instance) {
      OffersService.instance = new OffersService()
    }
    return OffersService.instance
  }

  async getRestaurantsWithOffers(): Promise<{ restaurants: Restaurant[], total_offers: number, last_updated: string }> {
    const now = Date.now()
    
    // Return cached data if it's still fresh
    if (this.cachedData && (now - this.lastFetch) < this.CACHE_DURATION) {
      return this.cachedData
    }

    try {
      // Try enhanced-offers endpoint first for rich food visualization data
      const response = await fetch(`${this.API_BASE_URL}/enhanced-offers`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        // Don't cache the request
        cache: 'no-cache'
      })
      
      if (!response.ok) {
        throw new Error(`Enhanced API error! status: ${response.status} - ${response.statusText}`)
      }
      
      const data = await response.json()
      
      // Transform the backend response to match our frontend types
      const result = {
        restaurants: data.restaurants || [],
        total_offers: data.total_offers || 0,
        last_updated: data.last_updated || new Date().toISOString()
      }
      
      // Cache the data
      this.cachedData = result
      this.lastFetch = now
      
      return result
    } catch (error) {
      console.error('Failed to fetch enhanced offers from backend:', error)
      
      // Fallback to basic restaurants endpoint
      try {
        console.log('Falling back to basic restaurants endpoint...')
        const fallbackResponse = await fetch(`${this.API_BASE_URL}/restaurants`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          cache: 'no-cache'
        })
        
        if (fallbackResponse.ok) {
          const fallbackData = await fallbackResponse.json()
          const fallbackResult = {
            restaurants: fallbackData.restaurants || [],
            total_offers: fallbackData.total_offers || 0,
            last_updated: fallbackData.last_updated || new Date().toISOString()
          }
          
          this.cachedData = fallbackResult
          this.lastFetch = now
          
          return fallbackResult
        }
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError)
      }
      
      // If it's a network error, provide a more helpful message
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Ekki hægt að tengjast við bakenda. Vinsamlegast passaðu að bakendinn sé að keyra á http://localhost:8000')
      }
      
      throw error
    }
  }

  // Method to refresh the cache
  async refreshCache(): Promise<void> {
    this.cachedData = null
    this.lastFetch = 0
    await this.getRestaurantsWithOffers()
  }

  // Remove the old method that tried to fetch enhanced offers
  async fetchEnhancedOffers(): Promise<EnhancedOffersData> {
    throw new Error('This method is deprecated. Use getRestaurantsWithOffers instead.')
  }
} 