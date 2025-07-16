'use client'

import React, { useState, useEffect } from 'react'
import { Restaurant } from '@/types'
import { OffersService } from '@/services/offersService'
import { Icon } from '@iconify/react'
import RestaurantCard from '@/components/RestaurantCard'

export default function HomePage() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const offersService = OffersService.getInstance()

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const data = await offersService.getRestaurantsWithOffers()
        
        setRestaurants(data.restaurants || [])
        
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
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>
            <Icon icon="mdi:alert-circle" style={{ color: '#ff6b6b' }} />
          </div>
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

          {/* Restaurants using RestaurantCard component */}
          <div >
            {restaurants.map((restaurant) => (
              <RestaurantCard key={restaurant.id} restaurant={restaurant} />
            ))}
          </div>

          {/* Bottom Navigation */}
          <div style={{
            background: 'rgba(248, 248, 248, 0.95)',
            backdropFilter: 'blur(20px)',
            padding: '12px 24px 24px',
            borderTop: '1px solid rgba(0, 0, 0, 0.05)'
          }}>
            <button 
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
    </>
  )
} 