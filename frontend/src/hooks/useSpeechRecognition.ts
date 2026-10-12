import { useState, useEffect, useRef, useCallback } from 'react'

interface SpeechRecognitionHookResult {
  isListening: boolean
  transcript: string
  isSupported: boolean
  error: string | null
  startListening: () => void
  stopListening: () => void
  resetTranscript: () => void
}

// Window interface augmentation for browser speech recognition
declare global {
  interface Window {
    SpeechRecognition?: any
    webkitSpeechRecognition?: any
  }
}

export function useSpeechRecognition(onResultCallback?: (text: string) => void): SpeechRecognitionHookResult {
  const [isListening, setIsListening] = useState<boolean>(false)
  const [transcript, setTranscript] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [isSupported] = useState<boolean>(() => {
    return typeof window !== 'undefined' && Boolean(window.SpeechRecognition || window.webkitSpeechRecognition)
  })

  const recognitionRef = useRef<any>(null)
  const transcriptRef = useRef<string>('')
  const hasReportedFinalRef = useRef<boolean>(false)
  const onResultCallbackRef = useRef(onResultCallback)

  useEffect(() => {
    onResultCallbackRef.current = onResultCallback
  }, [onResultCallback])

  useEffect(() => {
    const SpeechRecognitionClass = window.SpeechRecognition || window.webkitSpeechRecognition
    if (SpeechRecognitionClass) {
      const instance = new SpeechRecognitionClass()
      instance.continuous = false
      instance.interimResults = true
      // Use device local language or fallback to en-IN / en-US
      instance.lang = navigator.language || 'en-US'

      instance.onresult = (event: any) => {
        let fullTranscript = ''
        let hasFinal = false

        for (let i = 0; i < event.results.length; i++) {
          const res = event.results[i]
          fullTranscript += res[0].transcript
          if (res.isFinal) {
            hasFinal = true
          }
        }

        const cleaned = fullTranscript.trim()
        setTranscript(cleaned)
        transcriptRef.current = cleaned

        if (hasFinal && cleaned && !hasReportedFinalRef.current) {
          hasReportedFinalRef.current = true
          if (onResultCallbackRef.current) {
            onResultCallbackRef.current(cleaned)
          }
          setIsListening(false)
        }
      }

      instance.onerror = (event: any) => {
        if (event.error === 'not-allowed') {
          setError('Microphone permission denied. Tap the lock/info icon in your browser URL bar to allow microphone.')
        } else if (event.error === 'no-speech') {
          // Normal timeout when silence; no need to show an aggressive error
          setError(null)
        } else {
          setError(`Mic notice: ${event.error}`)
        }
        setIsListening(false)
      }

      instance.onend = () => {
        setIsListening(false)
        // If ended with transcript that was not yet reported as final, report it now
        if (transcriptRef.current && !hasReportedFinalRef.current) {
          hasReportedFinalRef.current = true
          if (onResultCallbackRef.current) {
            onResultCallbackRef.current(transcriptRef.current)
          }
        }
      }

      recognitionRef.current = instance
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort()
        } catch {
          // ignore cleanup abort
        }
      }
    }
  }, [])

  const startListening = useCallback(() => {
    setError(null)
    setTranscript('')
    transcriptRef.current = ''
    hasReportedFinalRef.current = false

    if (!recognitionRef.current) {
      setError('Speech recognition is not supported in this browser. Please use Chrome on Android or PC.')
      return
    }

    try {
      recognitionRef.current.start()
      setIsListening(true)
    } catch (e: any) {
      if (e.name !== 'InvalidStateError') {
        setError('Microphone is busy. Please try again.')
      }
    }
  }, [])

  const stopListening = useCallback(() => {
    if (!recognitionRef.current) return
    try {
      recognitionRef.current.stop()
    } catch {
      // ignore
    }
    setIsListening(false)
  }, [])

  const resetTranscript = useCallback(() => {
    setTranscript('')
    transcriptRef.current = ''
  }, [])

  return {
    isListening,
    transcript,
    isSupported,
    error,
    startListening,
    stopListening,
    resetTranscript,
  }
}
