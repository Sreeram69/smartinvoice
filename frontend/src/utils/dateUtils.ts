/**
 * Utility functions for local Indian Standard Time (IST, UTC+5:30) date handling.
 */

export const getIndiaDate = (): string => {
  try {
    return new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(new Date())
  } catch {
    const now = new Date()
    const istOffset = 5.5 * 60 * 60 * 1000
    return new Date(now.getTime() + istOffset).toISOString().split('T')[0]
  }
}

/**
 * Sanitizes destination country name into a clean uppercase slug for Address Numbering (e.g. USA, UAE, UK).
 */
export const getCountrySlug = (countryOrState?: string): string => {
  const val = (countryOrState || '').trim().toUpperCase()
  if (!val) return 'DEST'

  if (val.includes('USA') || val.includes('UNITED STATES') || val.includes('AMERICA')) {
    return 'USA'
  }
  if (val.includes('UAE') || val.includes('EMIRATES') || val.includes('DUBAI') || val.includes('ABU DHABI')) {
    return 'UAE'
  }
  if (val.includes('UK') || val.includes('UNITED KINGDOM') || val.includes('ENGLAND') || val.includes('LONDON')) {
    return 'UK'
  }
  if (val.includes('CANADA')) return 'CANADA'
  if (val.includes('AUSTRALIA')) return 'AUSTRALIA'
  if (val.includes('GERMANY')) return 'GERMANY'
  if (val.includes('SINGAPORE')) return 'SINGAPORE'
  if (val.includes('INDIA')) return 'INDIA'

  // Extract first clean alphanumeric word
  const match = val.match(/[A-Z0-9]+/g)
  if (match && match.length > 0) {
    return match[0].slice(0, 10)
  }
  return 'DEST'
}
