import type { ItemLine } from './item'

export interface AddressInfo {
  name: string
  address_line_1: string
  address_line_2: string
  city: string
  state: string
  postal_code: string
  phone: string
  gstin?: string
}

export interface DocumentGenerationPayload {
  doc_type: 'invoice' | 'challan' | 'address' | 'address_label' | 'booking' | 'awb'
  doc_number: string
  date: string
  sender: AddressInfo
  customer: AddressInfo
  items: ItemLine[]
  total: string
  notes?: string
  transport_mode?: string
  vehicle_number?: string
  include_invoice?: boolean
  include_address_label: boolean
  address_format: 'pdf' | 'docx'
  invoice_format?: 'pdf' | 'xlsx'
  weight?: string
  awb_number?: string
  // Booking AWB Fields
  service_partner?: string
  package_type?: string
  pieces?: string
  actual_weight?: string
  volumetric_weight?: string
  chargeable_weight?: string
  rate_per_kg?: string
  freight_amount?: string
  other_charges?: string
  discount?: string
  payment_status?: string
  payment_mode?: string
  contents_description?: string
  destination_country?: string
}
