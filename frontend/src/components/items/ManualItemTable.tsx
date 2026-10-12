import React from 'react'
import { Plus, Trash2, Hash, RotateCcw } from 'lucide-react'
import { CornerGrid } from '../common/CornerGrid'
import type { ItemLine } from '../../types/item'

interface ManualItemTableProps {
  items: ItemLine[]
  onUpdateItem: (id: string, field: keyof ItemLine, value: string) => void
  onAddItem: () => void
  onRemoveItem: (id: string) => void
  customTotal: string
  onUpdateCustomTotal: (val: string) => void
  isManualTotalEdited?: boolean
  onResetAutoTotal?: () => void
}

export const ManualItemTable: React.FC<ManualItemTableProps> = ({
  items,
  onUpdateItem,
  onAddItem,
  onRemoveItem,
  customTotal,
  onUpdateCustomTotal,
  isManualTotalEdited = false,
  onResetAutoTotal,
}) => {
  // Handles editing row total amount directly (e.g. user enters total 3000 for 2 items => rate becomes 1500)
  const handleRowAmountChange = (item: ItemLine, newTotalStr: string) => {
    const qty = parseFloat(item.count) || 1
    const totalVal = parseFloat(newTotalStr.replace(/,/g, ''))
    if (!isNaN(totalVal) && qty > 0) {
      const unitRate = (totalVal / qty).toFixed(2).replace(/\.00$/, '')
      onUpdateItem(item.id, 'price', unitRate)
    } else {
      onUpdateItem(item.id, 'price', newTotalStr)
    }
  }

  return (
    <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] p-4 sm:p-5 shadow-sm cursor-default">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-[var(--border-color)] pb-3 mb-4">
        <div className="flex items-center gap-2">
          <CornerGrid />
          <span className="section-label">ITEM DETAILS & PRICING</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onAddItem}
            className="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5"
          >
            <Plus className="h-3.5 w-3.5 text-[var(--accent-red)]" />
            <span>ADD ROW</span>
          </button>
        </div>
      </div>

      {/* Responsive Table Container */}
      <div className="overflow-x-auto scrollable-list rounded-lg border border-[var(--border-color)] bg-[var(--bg-card)] shadow-sm">
        <table className="w-full text-left border-collapse min-w-[620px]">
          <thead>
            <tr className="border-b border-[var(--border-color)] text-[var(--text-secondary)] font-mono-tech text-[10px] uppercase tracking-wider bg-[var(--bg-surface)]">
              <th className="py-2.5 px-3 w-12 text-center">#</th>
              <th className="py-2.5 px-3 min-w-[200px]">Item Name / Description</th>
              <th className="py-2.5 px-3 w-28 text-center">Count / Qty</th>
              <th className="py-2.5 px-3 w-36 text-right">Price / Item (Rate ₹)</th>
              <th className="py-2.5 px-3 w-40 text-right">Total Amount (₹)</th>
              <th className="py-2.5 px-2 w-12 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--border-color)]">
            {items.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-xs text-[var(--text-muted)] font-mono-tech">
                  NO ITEMS YET. CLICK "ADD ROW" OR USE VOICE INPUT ABOVE.
                </td>
              </tr>
            ) : (
              items.map((item, idx) => {
                const qty = parseFloat(item.count) || 1
                const unitPrice = parseFloat(item.price.replace(/,/g, '')) || 0
                const lineTotal = (qty * unitPrice).toFixed(2)

                return (
                  <tr key={item.id} className="hover:bg-[var(--bg-card-hover)] transition-colors group">
                    {/* Row Number */}
                    <td className="py-2 px-3 text-center font-mono-tech text-xs text-[var(--text-muted)]">
                      {idx + 1}
                    </td>

                    {/* Item Name */}
                    <td className="py-2 px-3">
                      <input
                        type="text"
                        className="nothing-input"
                        placeholder="e.g. Saree, Cardboard Boxes"
                        value={item.name}
                        onChange={(e) => onUpdateItem(item.id, 'name', e.target.value)}
                      />
                    </td>

                    {/* Count / Quantity */}
                    <td className="py-2 px-3">
                      <input
                        type="text"
                        className="nothing-input text-center font-mono-tech font-bold"
                        placeholder="1"
                        value={item.count}
                        onChange={(e) => onUpdateItem(item.id, 'count', e.target.value)}
                      />
                    </td>

                    {/* Unit Price (Price per item) */}
                    <td className="py-2 px-3">
                      <div className="relative">
                        <span className="absolute left-2.5 top-1/2 -translate-y-1/2 font-mono-tech text-xs text-[var(--text-muted)]">
                          ₹
                        </span>
                        <input
                          type="text"
                          className="nothing-input pl-6 text-right font-mono-tech text-[var(--text-primary)]"
                          placeholder="0.00"
                          value={item.price}
                          onChange={(e) => onUpdateItem(item.id, 'price', e.target.value)}
                        />
                      </div>
                    </td>

                    {/* Line Total Amount (Qty * Rate) */}
                    <td className="py-2 px-3">
                      <div className="relative">
                        <span className="absolute left-2.5 top-1/2 -translate-y-1/2 font-mono-tech text-xs text-[var(--accent-red)] font-bold">
                          ₹
                        </span>
                        <input
                          type="text"
                          className="nothing-input pl-6 text-right font-mono-tech font-bold text-[var(--text-primary)] bg-[var(--bg-surface)] focus:bg-[var(--bg-card)]"
                          placeholder="0.00"
                          value={lineTotal}
                          onChange={(e) => handleRowAmountChange(item, e.target.value)}
                          title="Row total (Qty × Rate). You can edit this directly to adjust price per item."
                        />
                      </div>
                    </td>

                    {/* Delete Action */}
                    <td className="py-2 px-2 text-center">
                      <button
                        type="button"
                        onClick={() => onRemoveItem(item.id)}
                        className="inline-flex h-8 w-8 items-center justify-center rounded border border-transparent text-[var(--text-muted)] hover:border-[var(--accent-red)] hover:text-[var(--accent-red)] transition-all cursor-pointer"
                        title="Remove item"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Summary & User-Defined Total Bar */}
      <div className="mt-4 pt-4 border-t border-[var(--border-color)] flex flex-col sm:flex-row items-end sm:items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs font-mono-tech text-[var(--text-secondary)]">
          <Hash className="h-4 w-4 text-[var(--accent-red)]" />
          <span>ITEMS COUNT: {items.length}</span>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          {isManualTotalEdited && onResetAutoTotal && (
            <button
              type="button"
              onClick={onResetAutoTotal}
              className="btn-secondary text-[10.5px] py-1 px-2 flex items-center gap-1 cursor-pointer"
              title="Reset document total to exact sum of item rows"
            >
              <RotateCcw className="h-3 w-3 text-[var(--accent-red)]" />
              <span>RESET SUM</span>
            </button>
          )}

          <span className="section-label whitespace-nowrap">DOCUMENT TOTAL:</span>
          <div className="relative w-40 sm:w-48">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 font-mono-tech text-sm text-[var(--accent-red)] font-bold">
              ₹
            </span>
            <input
              type="text"
              value={customTotal}
              onChange={(e) => onUpdateCustomTotal(e.target.value)}
              className="nothing-input pl-7 text-right font-mono-tech text-base font-bold text-[var(--text-primary)]"
              placeholder="0.00"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
