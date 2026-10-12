import React from 'react'
import { CornerGrid } from '../common/CornerGrid'
import { UserCheck, Building } from 'lucide-react'
import type { AddressInfo } from '../../types/document'

interface AddressDetailsCardProps {
  sender: AddressInfo
  customer: AddressInfo
  onUpdateSender: (field: keyof AddressInfo, val: string) => void
  onUpdateCustomer: (field: keyof AddressInfo, val: string) => void
  onSwapAddresses?: () => void
}

export const AddressDetailsCard: React.FC<AddressDetailsCardProps> = ({
  sender,
  customer,
  onUpdateSender,
  onUpdateCustomer,
}) => {
  return (
    <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-sm cursor-default">
      <div className="flex items-center gap-2 border-b border-[var(--border-color)] pb-3 mb-4">
        <CornerGrid />
        <span className="section-label">PARTIES & ADDRESS DETAILS</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* SENDER (FROM) CARD */}
        <div className="rounded-lg border border-[var(--border-color)] bg-[var(--bg-card)] p-4 space-y-3 shadow-sm">
          <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-2">
            <span className="font-mono-tech text-[10.5px] font-bold text-[var(--text-primary)] flex items-center gap-1.5 uppercase tracking-wider">
              <Building className="h-3.5 w-3.5 text-[var(--accent-red)]" />
              SENDER (BILLED FROM)
            </span>
            <span className="font-mono-tech text-[9px] text-[var(--text-secondary)] bg-[var(--bg-surface)] px-2 py-0.5 rounded border border-[var(--border-color)]">
              ORIGIN
            </span>
          </div>

          <div className="space-y-2">
            <div className="input-container group">
              <label className="section-label block mb-1">Company / Sender Name</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="Sender Business Name"
                value={sender.name}
                onChange={(e) => onUpdateSender('name', e.target.value)}
              />
            </div>

            <div className="input-container group">
              <label className="section-label block mb-1">Address Line 1 (Street / Building)</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="Door/Plot/Street"
                value={sender.address_line_1}
                onChange={(e) => onUpdateSender('address_line_1', e.target.value)}
              />
            </div>

            <div className="input-container group">
              <label className="section-label block mb-1">Address Line 2 (Area / Locality / Landmark)</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="Locality / Area (Optional)"
                value={sender.address_line_2 || ''}
                onChange={(e) => onUpdateSender('address_line_2', e.target.value)}
              />
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div className="input-container group">
                <label className="section-label block mb-1">City</label>
                <input
                  type="text"
                  className="nothing-input"
                  placeholder="City"
                  value={sender.city}
                  onChange={(e) => onUpdateSender('city', e.target.value)}
                />
              </div>
              <div className="input-container group">
                <label className="section-label block mb-1">State / Region</label>
                <input
                  type="text"
                  className="nothing-input"
                  placeholder="State"
                  value={sender.state || ''}
                  onChange={(e) => onUpdateSender('state', e.target.value)}
                />
              </div>
              <div className="input-container group">
                <label className="section-label block mb-1">Postal Code</label>
                <input
                  type="text"
                  className="nothing-input font-mono-tech"
                  placeholder="PIN/ZIP"
                  value={sender.postal_code}
                  onChange={(e) => onUpdateSender('postal_code', e.target.value)}
                />
              </div>
            </div>

            <div className="input-container group">
              <label className="section-label block mb-1">Phone</label>
              <input
                type="text"
                className="nothing-input font-mono-tech"
                placeholder="+91 9876543210"
                value={sender.phone}
                onChange={(e) => onUpdateSender('phone', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* CUSTOMER (TO) CARD */}
        <div className="rounded-lg border border-[var(--border-color)] bg-[var(--bg-card)] p-4 space-y-3 shadow-sm">
          <div className="flex items-center justify-between border-b border-[var(--border-color)] pb-2">
            <span className="font-mono-tech text-[10.5px] font-bold text-[var(--text-primary)] flex items-center gap-1.5 uppercase tracking-wider">
              <UserCheck className="h-3.5 w-3.5 text-[var(--accent-red)]" />
              CUSTOMER (BILLED / SHIPPED TO)
            </span>
            <span className="font-mono-tech text-[9px] text-[var(--text-secondary)] bg-[var(--bg-surface)] px-2 py-0.5 rounded border border-[var(--border-color)]">
              DESTINATION
            </span>
          </div>

          <div className="space-y-2">
            <div className="input-container group">
              <label className="section-label block mb-1">Customer / Recipient Name</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="Recipient / Customer Name"
                value={customer.name}
                onChange={(e) => onUpdateCustomer('name', e.target.value)}
              />
            </div>

            <div className="input-container group">
              <label className="section-label block mb-1">Address Line 1 (Street / Building)</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="Door/Street/Locality"
                value={customer.address_line_1}
                onChange={(e) => onUpdateCustomer('address_line_1', e.target.value)}
              />
            </div>

            <div className="input-container group">
              <label className="section-label block mb-1">Address Line 2 (Area / Locality / Landmark)</label>
              <input
                type="text"
                className="nothing-input"
                placeholder="Floor / Area / Hospital (Optional)"
                value={customer.address_line_2 || ''}
                onChange={(e) => onUpdateCustomer('address_line_2', e.target.value)}
              />
            </div>

            <div className="grid grid-cols-3 gap-2">
              <div className="input-container group">
                <label className="section-label block mb-1">City</label>
                <input
                  type="text"
                  className="nothing-input"
                  placeholder="City"
                  value={customer.city}
                  onChange={(e) => onUpdateCustomer('city', e.target.value)}
                />
              </div>
              <div className="input-container group">
                <label className="section-label block mb-1">State / Country</label>
                <input
                  type="text"
                  className="nothing-input"
                  placeholder="e.g. UAE"
                  value={customer.state || ''}
                  onChange={(e) => onUpdateCustomer('state', e.target.value)}
                />
              </div>
              <div className="input-container group">
                <label className="section-label block mb-1">Postal Code</label>
                <input
                  type="text"
                  className="nothing-input font-mono-tech"
                  placeholder="PIN/ZIP"
                  value={customer.postal_code}
                  onChange={(e) => onUpdateCustomer('postal_code', e.target.value)}
                />
              </div>
            </div>

            <div className="input-container group">
              <label className="section-label block mb-1">Phone</label>
              <input
                type="text"
                className="nothing-input font-mono-tech"
                placeholder="+971 52 301 0566"
                value={customer.phone}
                onChange={(e) => onUpdateCustomer('phone', e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
