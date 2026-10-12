import React, { useState, useEffect } from 'react'
import { CornerGrid } from '../common/CornerGrid'
import {
  Save,
  Loader2,
  PlaneTakeoff,
} from 'lucide-react'
import { buildApiUrl, getAuthHeaders } from '../../utils/apiConfig'
import type { AddressInfo } from '../../types/document'
import { NothingDatePicker } from '../common/NothingDatePicker'

interface BookingAwbCardProps {
  sender?: AddressInfo
  customer: AddressInfo
  onUpdateSender?: (field: keyof AddressInfo, val: string) => void
  onUpdateCustomer: (field: keyof AddressInfo, val: string) => void
  onSwapAddresses?: () => void
  awbNumber: string
  onUpdateAwbNumber: (num: string) => void
  docDate: string
  onUpdateDocDate: (date: string) => void
  weight: string
  onUpdateWeight: (val: string) => void
  onNotify: (msg: string) => void
  onSuccess?: () => void
}

export const BookingAwbCard: React.FC<BookingAwbCardProps> = ({
  sender,
  customer,
  onUpdateCustomer,
  awbNumber,
  onUpdateAwbNumber,
  docDate,
  onUpdateDocDate,
  weight,
  onUpdateWeight,
  onNotify,
  onSuccess,
}) => {
  // Routing: From & To Countries
  const [originCountry, setOriginCountry] = useState<string>('INDIA')
  const [destinationCountry, setDestinationCountry] = useState<string>(
    customer.state || ''
  )

  // Shipment Specifications State
  const [servicePartner, setServicePartner] = useState<string>('DHL Express')
  const [packageType, setPackageType] = useState<string>('Non Document')
  const [pieces, setPieces] = useState<string>('1')
  const [contentsDescription, setContentsDescription] = useState<string>('')

  // Pricing Given to Customer
  const [totalPricing, setTotalPricing] = useState<string>('0.00')

  // Payment
  const [paymentStatus, setPaymentStatus] = useState<'PAID' | 'PENDING'>('PAID')
  const [paymentMode, setPaymentMode] = useState<string>('UPI')

  // Loading state
  const [isSaving, setIsSaving] = useState<boolean>(false)

  // Sync destination country with customer state
  useEffect(() => {
    if (customer.state && customer.state.trim()) {
      const trimmed = customer.state.trim()
      setDestinationCountry((prev) => (prev !== trimmed ? trimmed : prev))
    }
  }, [customer.state])

  // Save Booking AWB to database and archive (no downloadable file provided)
  const handleSaveBooking = async () => {
    if (!awbNumber.trim()) {
      onNotify('Please enter a valid AWB / Consignment Number')
      return
    }

    setIsSaving(true)
    onNotify(`Saving Booking AWB (${awbNumber})...`)

    try {
      const payload = {
        doc_type: 'booking',
        doc_number: awbNumber.trim().toUpperCase(),
        date: docDate,
        sender: {
          ...(sender || {}),
          state: originCountry,
          city: sender?.city || originCountry,
        },
        customer: {
          ...customer,
          state: destinationCountry,
          city: customer.city || destinationCountry,
        },
        items: [],
        total: totalPricing,
        service_partner: servicePartner,
        package_type: packageType,
        pieces: pieces,
        contents_description: contentsDescription,
        weight: weight,
        payment_status: paymentStatus,
        payment_mode: paymentMode,
        destination_country: destinationCountry,
        include_address_label: false,
      }

      const response = await fetch(buildApiUrl('/api/v1/documents/save'), {
        method: 'POST',
        headers: getAuthHeaders({
          'Content-Type': 'application/json',
        }),
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized (401): Missing or invalid API key.')
        }
        let detail = response.statusText
        try {
          const errData = await response.json()
          if (errData.detail) detail = errData.detail
        } catch {
          // ignore
        }
        throw new Error(`Save failed: ${detail}`)
      }

      onNotify(`Saved Booking #${awbNumber} successfully!`)
      if (onSuccess) {
        onSuccess()
      }
    } catch (err: any) {
      onNotify(`Error: ${err.message || 'Failed to save Booking AWB'}`)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      {/* 1. TOP HEADER & ROUTING (FROM & TO) CARD */}
      <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[var(--border-color)] pb-3 mb-4">
          <div className="flex items-center gap-2">
            <CornerGrid />
            <span className="section-label">BOOKING CONSIGNMENT & AWB DETAILS</span>
            <span className="font-mono-tech text-[9.5px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded flex items-center gap-1">
              <PlaneTakeoff className="h-3 w-3 text-emerald-400" /> DIRECT ENTRY
            </span>
          </div>
        </div>

        {/* Clean Single Grid: AWB Number + Booking Date (IST) + FROM + TO + Courier Partner */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {/* AWB NUMBER */}
          <div className="input-container group">
            <label className="section-label block mb-1">AWB Number</label>
            <input
              type="text"
              value={awbNumber}
              onChange={(e) => onUpdateAwbNumber(e.target.value.toUpperCase())}
              className="nothing-input font-mono-tech uppercase font-bold text-[var(--accent-red)] tracking-wider"
              placeholder="AWB-USA-0001"
            />
          </div>

          {/* BOOKING DATE */}
          <div className="input-container group">
            <NothingDatePicker
              value={docDate}
              onChange={onUpdateDocDate}
              label="Booking Date (IST)"
            />
          </div>

          {/* FROM (ORIGIN COUNTRY) */}
          <div className="input-container group">
            <label className="section-label block mb-1">FROM (Origin)</label>
            <input
              type="text"
              value={originCountry}
              onChange={(e) => setOriginCountry(e.target.value.toUpperCase())}
              className="nothing-input font-mono-tech uppercase font-bold text-xs"
              placeholder="INDIA"
            />
          </div>

          {/* TO (DESTINATION COUNTRY) */}
          <div className="input-container group">
            <label className="section-label block mb-1 text-[var(--accent-red)]">TO (Destination)</label>
            <input
              type="text"
              value={destinationCountry}
              onChange={(e) => {
                const val = e.target.value.toUpperCase()
                setDestinationCountry(val)
                onUpdateCustomer('state', val)
              }}
              className="nothing-input font-mono-tech uppercase font-bold text-xs text-[var(--accent-red)]"
              placeholder="e.g. USA / UAE / UK"
            />
          </div>

          {/* NETWORK / SERVICE PARTNER */}
          <div className="input-container group sm:col-span-2 lg:col-span-1">
            <label className="section-label block mb-1">Courier Partner</label>
            <select
              value={servicePartner}
              onChange={(e) => setServicePartner(e.target.value)}
              className="nothing-input font-mono-tech text-xs bg-[var(--bg-card)]"
            >
              <option value="DHL Express">DHL Express</option>
              <option value="FedEx Priority">FedEx Priority</option>
              <option value="Aramex">Aramex</option>
              <option value="UPS Express">UPS Express</option>
              <option value="Self / Direct Cargo">Self / Direct Cargo</option>
              <option value="Express Air Cargo">Express Air Cargo</option>
            </select>
          </div>
        </div>
      </div>

      {/* 2. SHIPMENT & CARGO SPECIFICATIONS */}
      <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-sm">
        <div className="flex items-center gap-2 border-b border-[var(--border-color)] pb-3 mb-4">
          <CornerGrid />
          <span className="section-label">SHIPMENT & CARGO SPECIFICATIONS</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-3">
          {/* PACKAGE TYPE: DROPDOWN (Document / Non Document) */}
          <div className="input-container group">
            <label className="section-label block mb-1">Package Type</label>
            <select
              value={packageType}
              onChange={(e) => setPackageType(e.target.value)}
              className="nothing-input font-mono-tech text-xs bg-[var(--bg-card)]"
            >
              <option value="Document">Document</option>
              <option value="Non Document">Non Document</option>
            </select>
          </div>

          {/* PIECES */}
          <div className="input-container group">
            <label className="section-label block mb-1">Pieces</label>
            <input
              type="text"
              className="nothing-input font-mono-tech text-xs"
              placeholder="1"
              value={pieces}
              onChange={(e) => setPieces(e.target.value)}
            />
          </div>

          {/* PARCEL WEIGHT / PCS CONTAINER (IDENTICAL TO INVOICE) */}
          <div className="input-container group">
            <label className="section-label block mb-1">
              Parcel Weight / Pcs (Optional)
            </label>
            <input
              type="text"
              className="nothing-input font-mono-tech text-xs font-bold text-[var(--accent-red)]"
              placeholder="e.g. 14KG or 1PCS"
              value={weight || ''}
              onChange={(e) => onUpdateWeight(e.target.value)}
            />
          </div>

          {/* CONTENTS DESCRIPTION */}
          <div className="input-container group">
            <label className="section-label block mb-1">Contents Description</label>
            <input
              type="text"
              className="nothing-input text-xs"
              placeholder="e.g. Personal Goods, Clothes"
              value={contentsDescription}
              onChange={(e) => setContentsDescription(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* 3. PRICING GIVEN TO CUSTOMER */}
      <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-sm">
        <div className="flex items-center gap-2 border-b border-[var(--border-color)] pb-3 mb-4">
          <CornerGrid />
          <span className="section-label">PRICING GIVEN TO CUSTOMER (INR ₹)</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-center">
          {/* TOTAL PRICING */}
          <div className="p-3 rounded-lg border border-[var(--border-color)] bg-[var(--bg-card)]">
            <div className="flex items-center justify-between mb-1">
              <span className="font-mono-tech text-[10px] uppercase font-bold text-[var(--text-secondary)]">
                TOTAL PRICING
              </span>
              <span className="text-[9px] font-mono-tech text-emerald-400">AMOUNT GIVEN</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="font-mono-tech text-base font-bold text-[var(--text-primary)]">₹</span>
              <input
                type="text"
                className="nothing-input font-mono-tech text-xl font-bold text-[var(--text-primary)] py-0.5 px-1 bg-transparent border-0 focus:ring-0"
                value={totalPricing}
                onChange={(e) => setTotalPricing(e.target.value)}
                placeholder="0.00"
              />
            </div>
          </div>

          {/* PAYMENT STATUS */}
          <div className="input-container group">
            <label className="section-label block mb-1.5">Payment Status</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setPaymentStatus('PAID')}
                className={`flex-1 py-2 px-3 rounded-lg border font-mono-tech text-xs font-bold transition-all cursor-pointer ${
                  paymentStatus === 'PAID'
                    ? 'border-emerald-500 bg-emerald-500/15 text-emerald-400'
                    : 'border-[var(--border-color)] bg-[var(--bg-card)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                PAID
              </button>
              <button
                type="button"
                onClick={() => setPaymentStatus('PENDING')}
                className={`flex-1 py-2 px-3 rounded-lg border font-mono-tech text-xs font-bold transition-all cursor-pointer ${
                  paymentStatus === 'PENDING'
                    ? 'border-amber-500 bg-amber-500/15 text-amber-400'
                    : 'border-[var(--border-color)] bg-[var(--bg-card)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                PENDING
              </button>
            </div>
          </div>

          {/* PAYMENT MODE */}
          <div className="input-container group">
            <label className="section-label block mb-1.5">Payment Mode</label>
            <select
              value={paymentMode}
              onChange={(e) => setPaymentMode(e.target.value)}
              className="nothing-input font-mono-tech text-xs bg-[var(--bg-card)] py-2"
            >
              <option value="UPI">UPI / GPay / PhonePe</option>
              <option value="CASH">Cash</option>
              <option value="BANK TRANSFER">Bank Transfer (NEFT/IMPS)</option>
              <option value="CARD">Credit / Debit Card</option>
            </select>
          </div>
        </div>
      </div>

      {/* 4. SAVE BOOKING ACTION BUTTON (NO DOWNLOADABLE FILE) */}
      <div className="pt-1">
        <button
          type="button"
          onClick={handleSaveBooking}
          disabled={isSaving}
          className="btn-primary w-full py-3.5 flex items-center justify-center gap-2 text-sm font-mono-tech tracking-wider cursor-pointer shadow-md"
        >
          {isSaving ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>SAVING BOOKING AWB...</span>
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              <span>SAVE BOOKING AWB</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}
