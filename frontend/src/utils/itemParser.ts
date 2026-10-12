import type { ItemLine } from '../types/item'

export function parseSpokenItemClient(text: string): Omit<ItemLine, 'id'> {
  let cleaned = text.trim()
  let count = '1'
  let price = '0'

  // 1. Look for price marker
  const priceMatch = cleaned.match(/(?:price|amount|cost|rate|for|rs\.?|rupees|inr)\s*(?:is|of)?\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)/i)
  if (priceMatch && priceMatch.index !== undefined) {
    price = priceMatch[1]
    cleaned = cleaned.substring(0, priceMatch.index) + ' ' + cleaned.substring(priceMatch.index + priceMatch[0].length)
  } else {
    // Check trailing number
    const trailingMatch = cleaned.match(/([0-9]+(?:\.[0-9]+)?)\s*(?:rupees|rs\.?|inr)?\s*$/i)
    if (trailingMatch && trailingMatch.index !== undefined) {
      price = trailingMatch[1]
      cleaned = cleaned.substring(0, trailingMatch.index)
    }
  }

  // 2. Look for count/qty marker
  const countMatch = cleaned.match(/(?:count|qty|quantity|nos|pieces|pcs)\s*(?:is|of)?\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?(?:\s*[a-zA-Z]+)?)/i)
  if (countMatch && countMatch.index !== undefined) {
    count = countMatch[1].trim()
    cleaned = cleaned.substring(0, countMatch.index) + ' ' + cleaned.substring(countMatch.index + countMatch[0].length)
  } else {
    // Check leading count: "10 boxes", "add 5 chairs"
    const leadingCount = cleaned.match(/^(?:add\s+)?([0-9]+(?:\.[0-9]+)?)\s+([a-zA-Z\s]+)/i)
    if (leadingCount) {
      count = leadingCount[1].trim()
      cleaned = leadingCount[2]
    }
  }

  // 3. Clean remaining text as name
  let name = cleaned
    .replace(/^(?:add\s+|item\s+|new\s+)+/i, '')
    .replace(/\s+(?:for|at|with|price|count)\s*$/i, '')
    .trim()

  if (!name) {
    name = 'Item'
  }

  return {
    name,
    count,
    price,
  }
}
