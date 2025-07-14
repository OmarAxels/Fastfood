'use client'

import React, { useState, useEffect } from 'react'
import { Restaurant, Offer } from '@/types'
import { OffersService } from '@/services/offersService'

export default function HomePage() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedRestaurants, setExpandedRestaurants] = useState<Set<number>>(new Set())

  const offersService = OffersService.getInstance()

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const data = await offersService.getRestaurantsWithOffers()
        
        setRestaurants(data.restaurants || [])
        // Expand all restaurants by default
        setExpandedRestaurants(new Set(data.restaurants?.map(r => r.id) || []))
        
      } catch (err) {
        console.error('Fetch error:', err)
        setError(err instanceof Error ? err.message : 'Failed to load restaurant offers')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleRefresh = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Refresh the cache and fetch new data
      await offersService.refreshCache()
      const data = await offersService.getRestaurantsWithOffers()
      
      setRestaurants(data.restaurants || [])
      
    } catch (err) {
      console.error('Refresh error:', err)
      setError(err instanceof Error ? err.message : 'Failed to refresh offers')
    } finally {
      setLoading(false)
    }
  }

  const toggleRestaurant = (restaurantId: number) => {
    const newExpanded = new Set(expandedRestaurants)
    if (newExpanded.has(restaurantId)) {
      newExpanded.delete(restaurantId)
    } else {
      newExpanded.add(restaurantId)
    }
    setExpandedRestaurants(newExpanded)
  }

  const getFoodIcon = (offer: Offer) => {
    const icons: string[] = []
    
    // Add icons based on food items
    if (offer.main_items && offer.main_items.length > 0) {
      offer.main_items.forEach(item => {
        icons.push(item.icon || '🍽️')
      })
    }
    
    if (offer.side_items && offer.side_items.length > 0) {
      offer.side_items.forEach(item => {
        icons.push(item.icon || '🥄')
      })
    }
    
    if (offer.drink_items && offer.drink_items.length > 0) {
      offer.drink_items.forEach(item => {
        icons.push(item.icon || '🥤')
      })
    }
    
    if (offer.dessert_items && offer.dessert_items.length > 0) {
      offer.dessert_items.forEach(item => {
        icons.push(item.icon || '🍰')
      })
    }
    
    // Remove duplicates and limit to 4 icons
    return [...new Set(icons)].slice(0, 4)
  }

  const getIconClass = (icon: string) => {
    switch (icon) {
      case '🍔': return 'icon-burger'
      case '🍗': return 'icon-chicken'
      case '🍟': return 'icon-fries'
      case '🥤': return 'icon-drink'
      case '🍰': case '🍪': return 'icon-dessert'
      default: return 'icon-burger'
    }
  }

  const getPersonIcon = (count: number) => {
    if (count === 1) return '👤'
    if (count === 2) return '👥'
    if (count >= 3 && count <= 4) return '👨‍👩‍👧'
    if (count >= 5) return '👨‍👩‍👧‍👦'
    return '👥'
  }

  const getCorrectPrice = (price: number, restaurantName: string) => {
    // Temporary fix for KFC pricing issue - prices appear to be missing a digit
    if (restaurantName.toLowerCase().includes('kfc') && price < 1000) {
      return price * 10
    }
    return price
  }

  const getRestaurantLogo = (restaurant: Restaurant) => {
    // Use the actual logo from the API if available
    if (restaurant.logo) {
      return restaurant.logo
    }
    // Fallback to initials
    const name = restaurant.name.toLowerCase()
    if (name.includes('kfc')) return 'KFC'
    if (name.includes('domino')) return 'DOM'
    if (name.includes('subway')) return 'SUB'
    return restaurant.name.substring(0, 3).toUpperCase()
  }

  if (loading) {
    return (
      <div style={{
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        minHeight: '100vh',
        padding: '20px',
        color: '#1d1d1f'
      }}>
        <div style={{
          maxWidth: '414px',
          margin: '0 auto',
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '20px',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '500px'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{
              width: '48px',
              height: '48px',
              border: '4px solid #667eea',
              borderTop: '4px solid transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 16px'
            }}></div>
            <p style={{ color: '#667eea', fontWeight: '600' }}>Sæki tilboð...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={{
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        minHeight: '100vh',
        padding: '20px',
        color: '#1d1d1f'
      }}>
        <div style={{
          maxWidth: '414px',
          margin: '0 auto',
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '20px',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden',
          padding: '40px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
          <p style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>Villa við að hlaða tilboð</p>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '24px' }}>{error}</p>
          <button 
            onClick={handleRefresh}
            style={{
              background: 'linear-gradient(135deg, #007aff, #0056cc)',
              color: 'white',
              border: 'none',
              padding: '16px 24px',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0, 122, 255, 0.3)'
            }}
          >
            Reyna aftur
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      <style jsx>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .icon-burger { background: #fff3cd; }
        .icon-chicken { background: #d4edda; }
        .icon-fries { background: #f8d7da; }
        .icon-drink { background: #d1ecf1; }
        .icon-dessert { background: #e2e3e5; }

        .offer-card:hover {
          background: rgba(0, 0, 0, 0.02);
        }

        .offer-card:active {
          background: rgba(0, 0, 0, 0.04);
        }

        .nav-button:hover {
          transform: translateY(-1px);
          box-shadow: 0 6px 16px rgba(0, 122, 255, 0.4);
        }

        .nav-button:active {
          transform: translateY(0);
        }

        .restaurant-header:hover {
          background: #f0f1f2;
        }

        .restaurant-header:active {
          background: #e9ecef;
        }

        .restaurant-logo img {
          width: 100%;
          height: 100%;
          object-fit: contain;
          border-radius: 8px;
        }

        @media (max-width: 480px) {
          .container {
            margin: 0 !important;
            border-radius: 0 !important;
            min-height: 100vh !important;
          }
          
          .main-body {
            padding: 0 !important;
          }
        }
      `}</style>
      
      <div className="main-body" style={{
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        minHeight: '100vh',
        padding: '20px',
        color: '#1d1d1f'
      }}>
        <div className="container" style={{
          maxWidth: '414px',
          margin: '0 auto',
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '20px',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          overflow: 'hidden'
        }}>
          {/* Header */}
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            padding: '30px 24px 32px',
            textAlign: 'center',
            position: 'relative'
          }}>
            <div style={{
              content: '',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)'
            }}></div>
            <div style={{ position: 'relative', zIndex: 1 }}>
              <h1 style={{
                fontSize: '28px',
                fontWeight: '700',
                color: 'white',
                marginBottom: '8px',
                letterSpacing: '-0.5px'
              }}>
                Skynditilboð 🍔
              </h1>
              <p style={{
                fontSize: '16px',
                color: 'rgba(255, 255, 255, 0.8)',
                fontWeight: '400'
              }}>
                Bestu tilboðin í bænum
              </p>
            </div>
          </div>

          {/* Restaurants */}
          {restaurants.map((restaurant) => {
            const isExpanded = expandedRestaurants.has(restaurant.id)
            const logoSrc = getRestaurantLogo(restaurant)
            
            return (
              <div key={restaurant.id}>
                {/* Restaurant Header - Made sticky and clickable */}
                <div 
                  className="restaurant-header"
                  onClick={() => toggleRestaurant(restaurant.id)}
                  style={{
                    padding: '16px 24px 12px', // Reduced padding for more compact
                    background: '#f8f9fa',
                    borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
                    position: 'sticky',
                    top: '0',
                    zIndex: 10,
                    backdropFilter: 'blur(20px)',
                    cursor: 'pointer',
                    transition: 'background 0.2s ease'
                  }}
                >
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px' // Reduced gap
                  }}>
                    <div 
                      className="restaurant-logo"
                      style={{
                        width: '40px', // Reduced size
                        height: '40px', // Reduced size
                        background: restaurant.background_color || 'linear-gradient(135deg, #ff6b6b, #ee5a52)',
                        borderRadius: '10px', // Reduced border radius
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontWeight: '700',
                        fontSize: '16px', // Reduced font size
                        boxShadow: '0 3px 8px rgba(238, 90, 82, 0.3)', // Reduced shadow
                        overflow: 'hidden'
                      }}
                    >
                      {logoSrc.startsWith('/') ? (
                        <img src={logoSrc} alt={restaurant.name} />
                      ) : (
                        logoSrc
                      )}
                    </div>
                    <div style={{ flex: 1 }}>
                      <h3 style={{
                        fontSize: '18px', // Reduced from 20px
                        fontWeight: '600',
                        color: '#1d1d1f',
                        marginBottom: '0px' // Reduced margin
                      }}>
                        {restaurant.name}
                      </h3>
                      <span style={{
                        background: '#34c759',
                        color: 'white',
                        padding: '3px 6px', // Reduced padding
                        borderRadius: '6px', // Reduced border radius
                        fontSize: '11px', // Reduced font size
                        fontWeight: '600'
                      }}>
                        {restaurant.offers?.length || 0} tilboð
                      </span>
                    </div>
                    {/* Expand/Collapse Arrow */}
                    <div style={{
                      fontSize: '16px', // Reduced from 18px
                      color: '#666',
                      transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                      transition: 'transform 0.3s ease'
                    }}>
                      ▼
                    </div>
                  </div>
                </div>

                {/* Offers - Collapsible */}
                {isExpanded && (
                  <div style={{ 
                    padding: 0, 
                    background: 'white',
                    animation: 'fadeIn 0.3s ease-in-out'
                  }}>
                    {restaurant.offers?.map((offer, index) => {
                      const foodIcons = getFoodIcon(offer)
                      const isSpecial = index === 0 // Make first offer special
                      
                      return (
                        <div 
                          key={offer.id} 
                          className="offer-card"
                          style={{
                            background: 'white',
                            borderRadius: 0,
                            marginBottom: 0,
                            boxShadow: 'none',
                            overflow: 'hidden',
                            transition: 'all 0.3s ease',
                            borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
                            position: 'relative',
                            ...(isSpecial && {
                              background: 'linear-gradient(135deg, rgba(52, 199, 89, 0.05), rgba(48, 209, 88, 0.05))'
                            })
                          }}
                        >
                          <div style={{
                            padding: '12px 20px', // Reduced padding for more compact
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '6px' // Reduced gap
                          }}>
                            {/* Title Row */}
                            <div style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center'
                            }}>
                              <h3 style={{
                                fontSize: '16px', // Reduced from 18px
                                fontWeight: '600',
                                color: '#1d1d1f',
                                lineHeight: '1.2', // Tighter line height
                                flex: 1,
                                marginRight: '12px'
                              }}>
                                <span style={{ fontSize: '12px', color: '#666'}}>{index + 1}. </span> {offer.name}
                              </h3>
                              {offer.price_kr && (
                                <div style={{
                                  background: 'linear-gradient(135deg, #34c759, #30d158)',
                                  color: 'white',
                                  padding: '4px 10px', // Reduced padding
                                  borderRadius: '6px', // Smaller border radius
                                  fontSize: '13px', // Slightly smaller font
                                  fontWeight: '600',
                                  minWidth: '60px', // Reduced width
                                  textAlign: 'center',
                                  boxShadow: '0 1px 4px rgba(52, 199, 89, 0.3)' // Reduced shadow
                                }}>
                                  {Math.round(getCorrectPrice(offer.price_kr, restaurant.name))} kr.
                                </div>
                              )}
                            </div>

                            {/* Details Row */}
                            <div style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center'
                            }}>
                              <div style={{
                                display: 'flex',
                                gap: '6px'
                              }}>
                                {foodIcons.map((icon, iconIndex) => (
                                  <div 
                                    key={iconIndex}
                                    className={getIconClass(icon)}
                                    style={{
                                      width: '24px',
                                      height: '24px',
                                      borderRadius: '6px',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      fontSize: '14px'
                                    }}
                                  >
                                    {icon}
                                  </div>
                                ))}
                              </div>
                              {offer.suits_people && (
                                <div style={{
                                  background: '#007aff',
                                  color: 'white',
                                  padding: '4px 8px',
                                  borderRadius: '6px', // Changed from 12px to match food icons
                                  fontSize: '12px',
                                  fontWeight: '600',
                                  minWidth: '30px',
                                  textAlign: 'center',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '2px'
                                }}>
                                  {getPersonIcon(offer.suits_people)} {offer.suits_people}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}

          {/* Bottom Navigation */}
          <div style={{
            background: 'rgba(248, 248, 248, 0.95)',
            backdropFilter: 'blur(20px)',
            padding: '12px 24px 24px',
            borderTop: '1px solid rgba(0, 0, 0, 0.05)'
          }}>
            <button 
              className="nav-button"
              style={{
                background: 'linear-gradient(135deg, #007aff, #0056cc)',
                color: 'white',
                border: 'none',
                padding: '16px 24px',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: '600',
                width: '100%',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 12px rgba(0, 122, 255, 0.3)'
              }}
              onClick={handleRefresh}
            >
              Endurnýja tilboð
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </>
  )
} 