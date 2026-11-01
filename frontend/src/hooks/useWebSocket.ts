import { useState, useEffect, useRef, useCallback } from 'react'
import { SystemState } from '../types/telemetry'

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected'

export function useWebSocket() {
  const [data, setData] = useState<SystemState | null>(null)
  const [status, setStatus] = useState<ConnectionStatus>('connecting')
  const [history, setHistory] = useState<SystemState[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)

  // Fetch initial REST snapshot
  useEffect(() => {
    fetch('/api/status')
      .then(res => res.json())
      .then((initialData: SystemState) => {
        setData(initialData)
        setHistory(prev => (prev.length === 0 ? [initialData] : prev))
      })
      .catch(err => {
        console.warn('Initial REST status fetch error:', err)
      })

    // Pre-fetch past 30 history points
    fetch('/api/history?limit=30')
      .then(res => res.json())
      .then((past: SystemState[]) => {
        if (Array.isArray(past) && past.length > 0) {
          setHistory(past)
        }
      })
      .catch(err => console.warn('History fetch error:', err))
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/telemetry`

    try {
      setStatus('connecting')
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        setStatus('connected')
        console.log('[WebSocket] Connected to RailConnect telemetry stream')
      }

      ws.onmessage = (event) => {
        try {
          const payload: SystemState = JSON.parse(event.data)
          setData(payload)
          setHistory(prev => {
            const next = [...prev, payload]
            return next.length > 50 ? next.slice(next.length - 50) : next
          })
        } catch (e) {
          console.error('[WebSocket] Failed to parse telemetry payload:', e)
        }
      }

      ws.onerror = () => {
        setStatus('disconnected')
      }

      ws.onclose = () => {
        setStatus('disconnected')
        wsRef.current = null
        // Reconnect after 2 seconds
        reconnectTimeoutRef.current = window.setTimeout(() => {
          connect()
        }, 2000)
      }
    } catch (err) {
      setStatus('disconnected')
      reconnectTimeoutRef.current = window.setTimeout(connect, 3000)
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  const sendControl = async (command: Record<string, any>) => {
    try {
      const res = await fetch('/api/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(command)
      })
      return await res.json()
    } catch (err) {
      console.error('Failed to send control command:', err)
      throw err
    }
  }

  return { data, status, history, sendControl }
}
